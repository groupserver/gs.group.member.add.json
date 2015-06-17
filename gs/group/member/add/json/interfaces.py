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
from __future__ import absolute_import, unicode_literals, print_function
from zope.interface import Interface
from zope.schema import ASCIILine, Text, TextLine
from gs.auth.token import AuthToken


class IHookUser(Interface):
    'A token'

    token = AuthToken(
        title='Token',
        description='The authentication token',
        required=True)

    groupId = ASCIILine(
        title='GroupIdentifier',
        description='The group to add the person to',
        required=True)

    email = ASCIILine(
        title='Email address',
        description='The email address of the new member',
        required=True)

    fn = TextLine(
        title='Name',
        description='The name of the new member',
        required=True)

    biography = Text(
        title='Biography',
        description='The HTML-formatted biography of the new member',
        required=False)

    tz = ASCIILine(
        title='Timezone',
        description='The timezone',
        required=False)
