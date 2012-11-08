# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.GSProfile.edit_profile import wym_editor_widget
from gs.content.form import select_widget, radio_widget
from gs.group.base import GroupForm
from gs.group.member.join.notify import NotifyNewMember as NotifyJoin,\
    NotifyAdmin
from gs.profile.email.base.emailuser import EmailUser
from addfields import AddFields
from adder import Adder
from audit import ADD_NEW_USER, ADD_OLD_USER
from notifier import Notifier as NotifyAdd


class AddEditProfileForm(GroupForm):
    label = u'Add a New Group Member'
    pageTemplateFileName = 'browser/templates/edit_profile_add.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(AddEditProfileForm, self).__init__(group, request)

    @Lazy
    def form_fields(self):
        retval = form.Fields(self.addFields.adminInterface,
                            render_context=False)
        retval['tz'].custom_widget = select_widget
        retval['biography'].custom_widget = wym_editor_widget
        retval['delivery'].custom_widget = radio_widget
        return retval

    @Lazy
    def defaultFromEmail(self):
        emailUser = EmailUser(self.context, self.adminInfo)
        retval = emailUser.get_delivery_addresses()[0]
        return retval

    def setUpWidgets(self, ignore_request=False):
        data = {'fromAddr': self.defaultFromEmail}

        siteTz = self.siteInfo.get_property('tz', 'UTC')
        defaultTz = self.groupInfo.get_property('tz', siteTz)
        data['tz'] = defaultTz

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @form.action(label=u'Add', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        adder = Adder(self.context, self.groupInfo, self.adminInfo)
        toAddr = data['toAddr'].strip()
        msg, userInfo, status = adder.add(toAddr, data['delivery'], data)
        self.status = msg

        # Tell the user
        if status == ADD_NEW_USER:
            notifier = NotifyAdd(self.context, self.request)
            fromAddr = ''
            toAddr = ''
            notifier.notify(self.adminInfo, userInfo, fromAddr, toAddr)
        elif status == ADD_OLD_USER:
            notifier = NotifyJoin(self.context, self.request)
            notifier.notify(userInfo)

        # Tell the administrator
        if status in (ADD_NEW_USER, ADD_OLD_USER):
            adminNotifier = NotifyAdmin(self.context, self.request)
            admins = [a for a in self.groupInfo.group_admins
                        if a.id != self.adminInfo.id]
            for adminInfo in admins:
                adminNotifier.notify(adminInfo, userInfo)
        assert self.status

    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @Lazy
    def addFields(self):
        retval = AddFields(self.context)
        return retval

    @Lazy
    def adminInfo(self):
        retval = self.loggedInUser
        return retval

    @Lazy
    def adminWidgets(self):
        return self.addFields.get_admin_widgets(self.widgets)

    @Lazy
    def profileWidgets(self):
        return self.addFields.get_profile_widgets(self.widgets)

    @Lazy
    def requiredProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if widget.required]
        return widgets

    @Lazy
    def optionalProfileWidgets(self):
        widgets = self.addFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if not(widget.required)]
        return widgets
