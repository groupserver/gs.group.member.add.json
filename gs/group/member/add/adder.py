# -*- coding: utf-8 -*-
from zope.component import createObject
from zope.formlib import form
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSProfile.utils import create_user_from_email, \
    enforce_schema
from gs.group.member.base.utils import user_member_of_group
from gs.group.member.invite.base.utils import set_digest
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    EmailAddressExists
from audit import Auditor, ADD_NEW_USER, ADD_OLD_USER, ADD_EXISTING_MEMBER


class Adder(object):

    def __init__(self, context, groupInfo, adminInfo):
        self.context = context
        self.groupInfo = groupInfo
        self.adminInfo = adminInfo

    def add(self, toAddr, delivery, profileDict):
        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context
        try:
            emailChecker.validate(toAddr)
        except EmailAddressExists:
            msg, userInfo, status = self.add_existing_user(toAddr, delivery)
        else:
            msg, userInfo, status = self.add_new_user(toAddr, delivery,
                                                        profileDict)
        return (msg, userInfo, status)

    def add_existing_user(self, toAddr, delivery):
        acl_users = self.context.acl_users
        user = acl_users.get_userByEmail(toAddr)
        assert user, 'User for address <%s> not found' % toAddr
        # get the user object in the context of the group and site
        userInfo = createObject('groupserver.UserFromId', self.context,
                                  user.getId())
        auditor = self.get_auditor(userInfo)
        if user_member_of_group(user, self.groupInfo):
            status = ADD_EXISTING_MEMBER
            auditor.info(status, toAddr)
            m = u'<li>The person with the email address {email} &#8213; '\
                u'{user} &#8213; is already a member of {group}. No changes '\
                u'to the profile of {user} have been made.</li>'
        else:
            status = ADD_OLD_USER
            auditor.info(status, toAddr)
            joininguser = IGSJoiningUser(userInfo)
            joininguser.silent_join(self.groupInfo)
            self.set_delivery(userInfo, delivery)
            m = u'<li>Adding the existing participant with  the email '\
                u'address {email} &#8213; {user} &#8213; to {group}</li>'
        e = u'<code class="email">{}</code>'.format(toAddr)
        msg = m.format(email=e, user=userInfo_to_anchor(userInfo),
                        group=groupInfo_to_anchor(self.groupInfo))
        retval = (msg, userInfo, status)
        return retval

    def add_new_user(self, toAddr, delivery, profileDict):
        # Email address does not exist, but it is a legitimate address
        user = create_user_from_email(self.context, toAddr)
        # force verify
        vid = '%s-%s-verified' % (toAddr, self.adminInfo.id)
        evu = createObject('groupserver.EmailVerificationUserFromEmail',
                           self.context, toAddr)
        evu.add_verification_id(vid)
        evu.verify_email(vid)

        # get the user object in the context of the group and site
        userInfo = createObject('groupserver.UserFromId', self.context,
                                user.id)
        self.add_profile_attributes(userInfo, profileDict)
        auditor = self.get_auditor(userInfo)
        status = ADD_NEW_USER
        auditor.info(status, toAddr)
        joininguser = IGSJoiningUser(userInfo)
        joininguser.silent_join(self.groupInfo)
        self.set_delivery(userInfo, delivery)
        u = userInfo_to_anchor(userInfo)
        m = u'<li>A profile for {user} has been created, and given the '\
            u'email address {email}. {user} has been joined to '\
            u'{group}.</li>\n'
        u = userInfo_to_anchor(userInfo)
        e = u'<code class="email">{}</code>'.format(toAddr)
        g = groupInfo_to_anchor(self.groupInfo)
        msg = m.format(user=u, email=e, group=g)
        retval = (msg, userInfo, status)
        return retval

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
