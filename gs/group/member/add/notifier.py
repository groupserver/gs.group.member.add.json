# -*- coding: utf-8 -*-
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
        html = self.htmlTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                    passwordLink=passwordLink)
        text = self.textTemplate(adminInfo=adminInfo, userInfo=userInfo)
        sender.send_message(subject, text, html, fromAddr, [toAddr])
