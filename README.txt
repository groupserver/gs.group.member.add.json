============================
``gs.group.member.add.base``
============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add a member to a GroupServer Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-03-19
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product provides the "just add" system for GroupServer_. Normally
people become participants by actively accepting an invitation [#invite]_,
signing up [#register]_, or joining a group [#join]_.

Generally these methods are better at getting people into a group than the
`Add Form`_. People who are added have no password, so they cannot use any
of the features on the Web. They are added are dependent on the
administrator for all help. In addition all the help pages, all the email
footers, and most of the notifications are written assuming that the member
can log in.

Add Form
========

The *Add* form is very similar to the *Invite a New Member* form. It
inherits much of the functionality from the Invite system. Like the Invite
system, it requires two email addresses: a ``From`` address and a ``To``
address. The latter is used as the email address of the new member. All the
required profile fields have to be filled out, also. There are three
possible outcomes from submitting the Add form.

New Profile:
  If the email address is unrecognised then a new profile is created, the
  member is added to the group, and he or she receives the `Welcome
  notification`_.

Existing Profile:
  If the email address already belongs to an existing profile, and that
  participant is not a member of the group, then he or she is joined to the
  group and sent the *standard* Welcome notification from
  ``gs.group.member.join`` [#join]_. The (somewhat vein) hope is that the
  participant would have set a password and is able to log in by the time
  the new member is added to a second group.
  
Existing Member:
  If the email address already belongs to an existing group member then no
  action is taken.

The *Email delivery settings* selector is not present on the Add form. This
is because the new member cannot login [#login]_, so he or she generally
cannot view the posts on the web, which is necessary for *Web only* and the
*Topic digest* options to work [#digest]_.

Welcome Notification
--------------------

The *Welcome* notification sent from this product contains no links to the
group or the profile of the member. This is because *generally* the member
cannot view anything without logging in [#login]_, and the member is unable
to log in without a password.

The notification does

* Welcome the new member,
* State that the new member will get email,
* Tell the new member how to post,
* Contain a *Reset password* link, and
* Contain an ``Unsubscribe`` ``mailto``.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.add.base
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/
.. [#invite] See <https://source.iopen.net/groupserver/gs.group.member.invite>
.. [#register] See <https://source.iopen.net/groupserver/gs.group.member.signup>
.. [#join] See <https://source.iopen.net/groupserver/gs.group.member.join>
.. [#login] In the experience of `OnlineGroups.Net`_ almost all groups are
            secret, with the majority of the remainder being private. The
            public groups are enough of an exception that we do not have to
            worry about them.
.. [#digest] In the corner-case of someone being added to a public group
             and needing *Web only* or *Digest* then the administrator can
             change the email settings of the new member after adding them.
