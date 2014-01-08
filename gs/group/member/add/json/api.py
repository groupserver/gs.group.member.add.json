# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net, E-Democracy.org, and Contributors.
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
from __future__ import unicode_literals
import json
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from gs.group.member.add.base import Adder, AddFields, ADD_NEW_USER, \
    ADD_OLD_USER, ADD_EXISTING_MEMBER


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
        # Zope's regular form validation system *should* take care of checking
        # on columns and what not. So here we just have to pass data on to the
        # actual invite code and package the result up as json
        adder = Adder(self.context, self.groupInfo, self.loggedInUser)
        addrName, toAddr = parseaddr(data['toAddr'].strip())
        toAddr = data['toAddr'].strip()
        msg, userInfo, status = adder.add(toAddr, data)

        retval = {}
        if status in (ADD_NEW_USER, ADD_OLD_USER, ADD_EXISTING_MEMBER):
            retval['status'] = status
            retval['message'] = msg
        else:
            retval['status'] = 100
            retval['message'] = 'An unknown event occurred.'

        retval = json.dumps(retval, indent=4)
        return retval

    def invite_user_failure(self, action, data, errors):
        return self.build_error_response(action, data, errors)
