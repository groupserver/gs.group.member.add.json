# -*- coding: utf-8 -*-
from zope.app.apidoc.interface import getFieldsInOrder
from zope.cachedescriptors.property import Lazy
from gs.group.member.invite.base.invitefields import InviteFields


class AddFields(InviteFields):
    def __init__(self, context):
        super(AddFields, self).__init__(context)

    def get_admin_widgets(self, widgets):
        '''These widgets are specific to the Invite a New Member
            interface. They form the first part of the form.'''
        assert widgets
        adminWidgetIds = ['fromAddr']
        retval = [widgets[w] for w in adminWidgetIds]
        assert retval
        return retval

    @Lazy
    def profileFieldIds(self):
        retval = ['toAddr'] +\
                    [f[0] for f in getFieldsInOrder(self.profileInterface)]
        assert type(retval) == list, \
            'profileFieldIds is not a list ({})'.format(type(retval))
        return retval
