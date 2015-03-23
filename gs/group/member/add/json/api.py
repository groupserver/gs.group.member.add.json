# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net, E-Democracy.org, and
# Contributors.
#
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from json import dumps as to_json
import md5
import time
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from gs.group.member.add.base import (
    Adder, AddFields, NotifyAdd, ADD_NEW_USER, ADD_OLD_USER,
    ADD_EXISTING_MEMBER)
from gs.group.member.join.notify import NotifyNewMember as NotifyJoin, \
    NotifyAdmin
from gs.profile.email.base import sanitise_address
from gs.profile.password.interfaces import IGSPasswordUser
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.XWFCore.XWFUtils import convert_int2b62


class AddUserAPI(GroupEndpoint):
    label = 'POST data to this URL to add a member to join this group.'

    def __init__(self, group, request):
        super(AddUserAPI, self).__init__(group, request)
        self.addFields = AddFields(group)

    @Lazy
    def globalConfiguration(self):
        retval = self.addFields.config
        return retval

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(self.addFields.adminInterface,
                                render_context=False)
        assert retval
        return retval

    @formlib.action(label='Submit', prefix='', failure='add_user_failure')
    def add_user_success(self, action, data):
        # Zope's regular form validation system *should* take care of
        # checking on columns and what not. So here we just have to pass
        # data on to the actual invite code and package the result up as
        # json
        return self.actual_add(data)

    def actual_add(self, data):
        retval = {}

        adder = Adder(self.context, self.groupInfo, self.loggedInUser)
        toAddr = sanitise_address(data['toAddr'])
        linked_groupname = groupInfo_to_anchor(self.groupInfo)

        msg, userInfo, status = adder.add(toAddr, data)
        linked_username = userInfo_to_anchor(userInfo)

        # Tell the user
        if status == ADD_NEW_USER:
            notifier = NotifyAdd(self.context, self.request)
            fromAddr = sanitise_address(data['fromAddr'])
            passwd = self.get_password_reset(userInfo, toAddr)
            notifier.notify(self.loggedInUser, userInfo, fromAddr, toAddr,
                            passwd)

            retval['status'] = 1
            m = []
            m.append('A profile for {0} has been created, and given the '
                     'email address <code>{1}</code>.')
            m.append('{0} has been added to {2}.')
            m = [i.format(linked_username, toAddr, linked_groupname)
                 for i in m]
            retval['message'] = m

        elif status == ADD_OLD_USER:
            notifier = NotifyJoin(self.context, self.request)
            notifier.notify(userInfo)

            retval['status'] = 2
            m = []
            m.append('Added the existing person with the email address '
                     '<code>{0}</code> ({1}) to {2}.')
            m = [i.format(toAddr, linked_username, linked_groupname)
                 for i in m]
            retval['message'] = m
        elif status == ADD_EXISTING_MEMBER:
            retval['status'] = 3
            m = []
            m.append('The person with the email address <code>{0}</code> '
                     '({1}) is already a member of {2}.')
            m.append('No changes to the profile of {1} have been made.')
            m = [i.format(toAddr, linked_username, linked_groupname)
                 for i in m]
            retval['message'] = m
        else:
            retval['status'] = 100
            retval['message'] = 'An unknown event occurred.'

        # Tell the administrator
        if status in (ADD_NEW_USER, ADD_OLD_USER):
            adminNotifier = NotifyAdmin(self.context, self.request)
            for adminInfo in self.groupInfo.group_admins:
                adminNotifier.notify(adminInfo, userInfo)

        retval = to_json(retval, indent=4)
        return retval

    def invite_user_failure(self, action, data, errors):
        return self.build_error_response(action, data, errors)

    def get_password_reset(self, userInfo, email):
        # FIXME: cut 'n' paste software engineering from
        # gs.group.member.add.base
        s = time.asctime() + email + userInfo.name + self.siteInfo.name
        vNum = long(md5.new(s).hexdigest(), 16)
        resetId = str(convert_int2b62(vNum))

        passwordUser = IGSPasswordUser(userInfo)
        passwordUser.add_password_reset(resetId)

        u = '{siteUrl}/r/password/{resetId}'
        retval = u.format(siteUrl=self.siteInfo.url, resetId=resetId)
        assert retval
        return retval
