# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2015 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, print_function, unicode_literals
from json import dumps as to_json
from logging import getLogger
log = getLogger('gs.group.member.add.json.hook')
#from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from gs.auth.token import log_auth_error
from gs.content.form.api.json import SiteEndpoint
from gs.group.member.add.base import (
    Adder, NotifyAdd, ADD_NEW_USER, ADD_OLD_USER,
    ADD_EXISTING_MEMBER)
from gs.group.member.join.notify import NotifyNewMember as NotifyJoin, \
    NotifyAdmin
from gs.profile.email.base import sanitise_address
from gs.profile.json import user_info, groups, email_info
from .interfaces import IHookUser


class AddHook(SiteEndpoint):
    '''The page to add someone'''
    label = 'Add hook'
    form_fields = form.Fields(IHookUser, render_context=False)

    @form.action(label='Add', name='add', prefix='',
                 failure='handle_add_failure')
    def handle_add(self, action, data):
        '''Add someone to a group

:param action: The button that was clicked.
:param dict data: The form data.'''
        admin = self.siteInfo.site_admins[0]
        groupInfo = createObject('groupserver.GroupInfo', self.context,
                                 data['groupId'])
        adder = Adder(self.context, groupInfo, admin)
        toAddr = sanitise_address(data['email'])
        fromAddr = self.siteInfo.get_support_email()
        msg, userInfo, status = adder.add(toAddr, data)

        r = {'status': 257,
             'message': 'Not processed'}

        if status == ADD_NEW_USER:
            notifier = NotifyAdd(self.context, self.request)
            fromAddr = sanitise_address(self.siteInfo.get_support_email())
            passwd = self.get_password_reset(userInfo, toAddr)
            notifier.notify(self.loggedInUser, userInfo, fromAddr, toAddr,
                            passwd)
            r['status'] = 0
            m = 'Created a new profile for {0} and added {0} to {1}'
            r['message'] = m.format(userInfo.name, groupInfo.name)
            r['user'] = user_info(self.siteInfo, userInfo)
            r['user']['email'] = email_info(self.siteInfo, userInfo)
            r['user']['groups'] = groups(self.siteInfo, userInfo)
        elif status == ADD_OLD_USER:
            notifier = NotifyJoin(groupInfo.groupObj, self.request)
            notifier.notify(userInfo)
            r['status'] = 1
            r['message'] = 'Added {0} to {1}'.format(userInfo.name, groupInfo.name)
            r['user'] = user_info(self.siteInfo, userInfo)
            r['user']['email'] = email_info(self.siteInfo, userInfo)
            r['user']['groups'] = groups(self.siteInfo, userInfo)
        elif status == ADD_EXISTING_MEMBER:
            r['status'] = 256
            r['message'] = '{0} is alredy a member of {1}'.format(userInfo.name, groupInfo.name)
            r['user'] = user_info(self.siteInfo, userInfo)
            r['user']['email'] = email_info(self.siteInfo, userInfo)
            r['user']['groups'] = groups(self.siteInfo, userInfo)
        else:
            r['status'] = 257
            r['message'] = 'An unknown event occurred.'

        if status in (ADD_NEW_USER, ADD_OLD_USER):
            adminNotifier = NotifyAdmin(groupInfo.groupObj, self.request)
            for adminInfo in groupInfo.group_admins:
                adminNotifier.notify(adminInfo, userInfo)

        retval = to_json(r)
        return retval

    def handle_add_failure(self, action, data, errors):
        log_auth_error(self.context, self.request, errors)
        retval = self.build_error_response(action, data, errors)
        return retval
