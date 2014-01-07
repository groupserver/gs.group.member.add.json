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
from gs.group.member.invite.base.invitefields import InviteFields


class AddFields(InviteFields):
    def __init__(self, context):
        super(AddFields, self).__init__(context)

    def get_admin_widgets(self, widgets):
        assert widgets
        adminWidgetIds = ['fromAddr']
        retval = [widgets[w] for w in adminWidgetIds]
        assert retval
        return retval

    @Lazy
    def standardFieldIds(self):
        retval = ['toAddr'] + self.profileFieldIds
        return retval

    def get_standard_widgets(self, widgets):
        assert widgets
        standardWidgetIds = self.standardFieldIds
        retval = [widgets[w] for w in standardWidgetIds]
        assert retval
        return retval
