# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from zope.component import createObject
from zope.formlib import form
from gs.group.member.base.utils import user_member_of_group
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    EmailAddressExists
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSProfile.utils import create_user_from_email, \
    enforce_schema
from .addfields import AddFields
from .audit import Auditor, ADD_NEW_USER, ADD_OLD_USER, ADD_EXISTING_MEMBER


class Adder(object):
    def __init__(self, context, groupInfo, adminInfo):
        self.context = context
        self.groupInfo = groupInfo
        self.adminInfo = adminInfo

    def add(self, toAddr, profileDict):
        emailChecker = NewEmailAddress(title='Email')
        emailChecker.context = self.context
        try:
            emailChecker.validate(toAddr)
        except EmailAddressExists:
            msg, userInfo, status = self.add_existing_user(toAddr)
        else:
            msg, userInfo, status = self.add_new_user(toAddr, profileDict)
        return (msg, userInfo, status)

    def add_existing_user(self, toAddr):
        acl_users = self.context.acl_users
        user = acl_users.get_userByEmail(toAddr)
        if not user:
            m = 'User for address <{0}> not found'.format(toAddr)
            raise LookupError(m)
        # get the user object in the context of the group and site
        userInfo = createObject('groupserver.UserFromId', self.context,
                                  user.getId())
        auditor = self.get_auditor(userInfo)
        if user_member_of_group(user, self.groupInfo):
            status = ADD_EXISTING_MEMBER
            auditor.info(status, toAddr)
            m = '<li>The person with the email address {email} &#8213; '\
                '{user} &#8213; is already a member of {group}. No changes '\
                'to the profile of {user} have been made.</li>'
        else:
            status = ADD_OLD_USER
            auditor.info(status, toAddr)
            joininguser = IGSJoiningUser(userInfo)
            joininguser.silent_join(self.groupInfo)
            m = '<li>Adding the existing participant with  the email '\
                'address {email} &#8213; {user} &#8213; to {group}</li>'
        e = '<code class="email">{0}</code>'.format(toAddr)
        msg = m.format(email=e, user=userInfo_to_anchor(userInfo),
                        group=groupInfo_to_anchor(self.groupInfo))
        retval = (msg, userInfo, status)
        return retval

    def add_new_user(self, toAddr, profileDict):
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
        m = '<li>A profile for {user} has been created, and given the '\
            'email address {email}.</li>\n<li>{user} has been joined to '\
            '{group}.</li>\n'
        u = userInfo_to_anchor(userInfo)
        e = '<code class="email">{0}</code>'.format(toAddr)
        g = groupInfo_to_anchor(self.groupInfo)
        msg = m.format(user=u, email=e, group=g)
        retval = (msg, userInfo, status)
        return retval

    def add_profile_attributes(self, userInfo, data):
        addFields = AddFields(self.context)
        enforce_schema(userInfo.user, addFields.profileInterface)
        f = form.Fields(addFields.adminInterface, render_context=False)
        fields = f.select(*addFields.profileFieldIds)
        for field in fields:
            field.interface = addFields.profileInterface
        form.applyChanges(userInfo.user, fields, data)

    def get_auditor(self, userInfo):
        auditor = Auditor(self.groupInfo.siteInfo, self.groupInfo,
                    self.adminInfo, userInfo)

        return auditor
