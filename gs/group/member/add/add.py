# coding=utf-8
'''The form that allows an admin to invite a new person to join a group.'''
from zope.component import createObject
from zope.formlib import form
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSGroupMember.groupmembership import user_member_of_group
from Products.GSProfile.edit_profile import select_widget, wym_editor_widget
from Products.GSProfile.utils import create_user_from_email, \
    enforce_schema, verificationId_from_email
from Products.GSProfile.emailaddress import NewEmailAddress, \
    EmailAddressExists
from gs.content.form.radio import radio_widget
from gs.group.member.invite.utils import set_digest
from audit import Auditor, ADD_NEW_USER, ADD_OLD_USER, ADD_EXISTING_MEMBER
from addfields import AddFields
from gs.group.member.join.interfaces import IGSJoiningUser

class AddEditProfileForm(PageForm):
    label = u'Add a New Group Member, Without Verification'
    pageTemplateFileName = 'browser/templates/edit_profile_add.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)

        siteInfo = self.siteInfo = \
          createObject('groupserver.SiteInfo', context)
        self.__groupInfo = self.__formFields =  self.__config = None
        self.__adminInfo = None
        self.addFields = AddFields(context)

    @property
    def form_fields(self):
        if self.__formFields == None:
            self.__formFields = form.Fields(self.addFields.adminInterface, 
                render_context=False)
            tz = self.__formFields['tz']
            tz.custom_widget = select_widget
            self.__formFields['biography'].custom_widget = wym_editor_widget
            self.__formFields['delivery'].custom_widget = radio_widget
        return self.__formFields
        
    @property
    def defaultFromEmail(self):
        retval = self.adminInfo.user.get_preferredEmailAddresses()[0]
        return retval
        
    def setUpWidgets(self, ignore_request=False):        
        data = {}

        siteTz = self.siteInfo.get_property('tz', 'UTC')
        defaultTz = self.groupInfo.get_property('tz', siteTz)
        data['tz'] = defaultTz

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)
        
    @form.action(label=u'Add Without Verification', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        self.actual_handle_add(action, data)
        
    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    # Non-Standard methods below this point
    @property
    def groupInfo(self):
        if self.__groupInfo == None:
            self.__groupInfo = \
                createObject('groupserver.GroupInfo', self.context)
        return self.__groupInfo
        
    @property
    def adminInfo(self):
        if self.__adminInfo == None:
            self.__adminInfo = createObject('groupserver.LoggedInUser', 
                self.context)
        return self.__adminInfo
    
    @property
    def adminWidgets(self):
        return self.addFields.get_admin_widgets(self.widgets)

    @property
    def profileWidgets(self):
        return self.addFields.get_profile_widgets(self.widgets)    
    
    @property  
    def requiredProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if widget.required == True]
        
        return widgets
    
    @property
    def optionalProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if widget.required == False]
            
        return widgets
        
    def actual_handle_add(self, action, data):
        userInfo = None
        
        acl_users = self.context.acl_users
        toAddr = data['toAddr'].strip()
        
        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context
        e = u'<code class="email">%s</code>' % toAddr
        g = groupInfo_to_anchor(self.groupInfo)
        try:
            emailChecker.validate(toAddr)
        except EmailAddressExists, errorVal:
            user = acl_users.get_userByEmail(toAddr)
            assert user, 'User for address <%s> not found' % toAddr
            # get the user object in the context of the group and site
            userInfo = createObject('groupserver.UserFromId',
                                  self.groupInfo.groupObj,
                                  user.getId())
            auditor = self.get_auditor(userInfo)
            u = userInfo_to_anchor(userInfo)
            if user_member_of_group(user, self.groupInfo):
                auditor.info(ADD_EXISTING_MEMBER, toAddr)
                self.status=u'''<li>The person with the email address %s 
&#8213; %s &#8213; is already a member of %s.</li>'''% (e, u, g)
                self.status = u'%s<li>No changes to the profile of '\
                  '%s have been made.</li>' % (self.status, u)
            else:
                self.status=u'<li>Adding the existing person with '\
                  u'the email address %s &#8213; %s &#8213; to '\
                  u'%s.</li>'% (e, u, g)
                auditor.info(ADD_OLD_USER, toAddr)
                joininguser = IGSJoiningUser(userInfo)
                joininguser.join(self.groupInfo)
                self.set_delivery(userInfo, data['delivery'])
        else:
            # Email address does not exist, but it is a legitimate address
            user = create_user_from_email(self.context, toAddr)
            verificationId = verificationId_from_email(toAddr)
            user.add_emailAddressVerification(verificationId, toAddr)
            # force verify
            user.verify_emailAddress(verificationId)
            # get the user object in the context of the group and site
            userInfo = createObject('groupserver.UserFromId',
                                  self.groupInfo.groupObj,
                                  user.id)
            self.add_profile_attributes(userInfo, data)
            auditor = self.get_auditor(userInfo)
            auditor.info(ADD_NEW_USER, toAddr)
            joininguser = IGSJoiningUser(userInfo)
            joininguser.join(self.groupInfo)    
            self.set_delivery(userInfo, data['delivery'])
            u = userInfo_to_anchor(userInfo)
            self.status = u'''<li>A profile for %s has been created, and
given the email address %s.</li>\n''' % (u, e)
            self.status = u'%s<li>%s has been joined to '\
              u'%s.</li>\n' % (self.status, u, g)
        assert user, 'User not created or found'
        assert self.status
        return userInfo

    def add_profile_attributes(self, userInfo, data):
        enforce_schema(userInfo.user, self.addFields.profileInterface)
        fields = self.form_fields.select(*self.addFields.profileFieldIds)
        for field in fields:
            field.interface = self.addFields.profileInterface
            
        changed = form.applyChanges(userInfo.user, fields, data)
        set_digest(userInfo, self.groupInfo, data)

    def get_auditor(self, userInfo):
        ctx = get_the_actual_instance_from_zope(self.context)
        
        auditor = Auditor(self.siteInfo, self.groupInfo, 
                    self.adminInfo, userInfo)
        
        return auditor

    def set_delivery(self, userInfo, delivery):
        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)

