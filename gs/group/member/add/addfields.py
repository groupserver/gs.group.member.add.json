# coding=utf-8
from zope.app.apidoc.interface import getFieldsInOrder
from zope.cachedescriptors.property import Lazy
from Products.GSProfile import interfaces


class AddFields(object):
    def __init__(self, context):
        self.context = context

    @Lazy
    def config(self):
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        retval = site_root.GlobalConfiguration
        return retval

    @Lazy
    def adminInterface(self):
        adminInterfaceName = '%sAdminBasic' % self.profileInterfaceName
        assert hasattr(interfaces, adminInterfaceName), \
            'Interface "%s" not found.' % adminInterfaceName
        retval = getattr(interfaces, adminInterfaceName)
        return retval

    @Lazy
    def profileInterfaceName(self):
        ifName = self.config.getProperty('profileInterface', 'IGSCoreProfile')
        # --=mpj17=-- Sometimes profileInterface is set to ''
        retval = (ifName and ifName) or 'IGSCoreProfile'
        assert hasattr(interfaces, retval), \
            'Interface "%s" not found.' % retval
        return retval

    @Lazy
    def profileInterface(self):
        retval = getattr(interfaces, self.profileInterfaceName)
        return retval

    def get_admin_widgets(self, widgets):
        '''These widgets are specific to the Invite a New Member
            interface. They form the first part of the form.'''
        assert widgets
        adminWidgetIds = ['toAddr', 'delivery']
        retval = [widgets[w] for w in adminWidgetIds]
        assert retval
        return retval

    @Lazy
    def profileFieldIds(self):
        retval = [f[0] for f in getFieldsInOrder(self.profileInterface)]
        assert type(retval) == list
        return retval

    def get_profile_widgets(self, widgets):
        '''These widgets are the standard profile fields for this site.
            They form the second-part of the form.'''
        assert widgets
        profileWidgetIds = ['form.%s' % i for i in self.profileFieldIds]
        retval = [w for w in widgets if w.name in profileWidgetIds]
        return retval
