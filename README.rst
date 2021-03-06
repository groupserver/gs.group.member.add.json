============================
``gs.group.member.add.json``
============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add a member to a GroupServer Group using JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2015-06-17
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

..  _Creative Commons Attribution-Share Alike 4.0 International License:
    https://creativecommons.org/licenses/by-sa/4.0/

Introduction
============

This product provides an API to allow people to be added to a
GroupServer_ group, without an invitation being sent
[#inviteJSON]_. There are two slight variants:

* One is a web hook, designed to be used by external systems.
* The other requires a cookie, and is designed to be used by the
  JavaScript on GroupServer pages


Resources
=========

- Code repository:
  https://github.com/groupserver/gs.group.member.add.json
- Questions and comments to
  http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. [#inviteJSON] The equivalent for inviting people is provided
   by ``gs.group.member.add.json``
   <https://github.com/groupserver/gs.group.member.add.json>

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
