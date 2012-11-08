# -*- coding: utf-8 -*-
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
