# coding=utf-8
'''The form that allows an admin to invite a new person to join a group.'''
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSGroupMember.groupmembership import user_member_of_group
from Products.GSProfile.edit_profile import select_widget, wym_editor_widget
from Products.GSProfile.utils import create_user_from_email, \
    enforce_schema
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    EmailAddressExists
from gs.content.form.radio import radio_widget
from gs.group.member.invite.base.utils import set_digest
from audit import Auditor, ADD_NEW_USER, ADD_OLD_USER, ADD_EXISTING_MEMBER
from addfields import AddFields
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.group.base import GroupForm


class AddEditProfileForm(GroupForm):
    label = u'Add a New Group Member, Without Verification'
    pageTemplateFileName = 'browser/templates/edit_profile_add.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(AddEditProfileForm, self).__init__(group, request)

    @Lazy
    def form_fields(self):
        retval = form.Fields(self.addFields.adminInterface,
                            render_context=False)
        tz = retval['tz']
        tz.custom_widget = select_widget
        retval['biography'].custom_widget = wym_editor_widget
        retval['delivery'].custom_widget = radio_widget
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

    @form.action(label=u'Add', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        self.actual_handle_add(action, data)

    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    # Non-Standard methods below this point

    @Lazy
    def addFields(self):
        retval = AddFields(self.context)
        return retval

    @Lazy
    def adminInfo(self):
        retval = self.loggedInUser
        return retval

    @Lazy
    def adminWidgets(self):
        return self.addFields.get_admin_widgets(self.widgets)

    @Lazy
    def profileWidgets(self):
        return self.addFields.get_profile_widgets(self.widgets)

    @Lazy
    def requiredProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if widget.required]

        return widgets

    @Lazy
    def optionalProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if not(widget.required)]

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
        except EmailAddressExists:
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
                self.status = u'''<li>The person with the email address %s
&#8213; %s &#8213; is already a member of %s.</li>''' % (e, u, g)
                self.status = u'%s<li>No changes to the profile of '\
                  '%s have been made.</li>' % (self.status, u)
            else:
                self.status = u'<li>Adding the existing person with '\
                  u'the email address %s &#8213; %s &#8213; to '\
                  u'%s.</li>' % (e, u, g)
                auditor.info(ADD_OLD_USER, toAddr)
                joininguser = IGSJoiningUser(userInfo)
                joininguser.join(self.groupInfo)
                self.set_delivery(userInfo, data['delivery'])
        else:
            # Email address does not exist, but it is a legitimate address
            user = create_user_from_email(self.context, toAddr)
            # force verify
            vid = '%s-%s-verified' % (toAddr, self.adminInfo.id)
            evu = createObject('groupserver.EmailVerificationUserFromEmail',
                               self.context, toAddr)
            evu.add_verification_id(vid)
            evu.verify_email(vid)

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

        form.applyChanges(userInfo.user, fields, data)
        set_digest(userInfo, self.groupInfo, data)

    def get_auditor(self, userInfo):
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
