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
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, getMultiAdapter
from gs.profile.notify import MessageSender
UTF8 = 'utf-8'


class Notifier(object):
    htmlTemplateName = 'gs-group-member-add-welcome.html'
    textTemplateName = 'gs-group-member-add-welcome.txt'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.oldContentType = self.request.response.getHeader('Content-Type')

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        assert retval, 'Could not create the GroupInfo from %s' % self.context
        return retval

    @Lazy
    def htmlTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                                    name=self.htmlTemplateName)
        return retval

    @Lazy
    def textTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                                    name=self.textTemplateName)
        return retval

    def notify(self, adminInfo, userInfo, fromAddr, toAddr, passwordLink):
        sender = MessageSender(self.context, userInfo)
        subject = (u'Welcome to {}'.format(self.groupInfo.name)).encode(UTF8)
        text = self.textTemplate(adminInfo=adminInfo, userInfo=userInfo)
        html = self.htmlTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                    passwordLink=passwordLink)
        sender.send_message(subject, text, html, fromAddr, [toAddr])

        self.request.response.setHeader('Content-Type', self.oldContentType)
