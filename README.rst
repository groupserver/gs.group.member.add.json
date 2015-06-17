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
    http://creativecommons.org/licenses/by-sa/4.0/

Introduction
============

This product provides an API to allow people to be added to a
GroupServer_ group, without an invitation being sent
[#inviteJSON]_. There are two slight variants: 

* One is a `web hook`_, designed to be used by external systems.
* The other requires a cookie_, and is designed to be used by the
  JavaScript on GroupServer pages

Web hook
========

The web hook ``gs-group-member-add.json`` in the **site** context
takes the following parameters:

``token``:
  The authentication token [#token]_

``groupId``:
  The group that the person is joining.

``email``:
  The email address of the new member.

``fn``:
  The name of the new member.

``biography``:
  The HTML-formatted biography for the new member (optional).

``tz``:
  The timezone for the new member (optional).

:Note: Unlike the cookie_ version, the web hook can **only**
       handle the **basic** GroupServer profile information. This
       is because the hook cannot be in the context of a group
       (because the hook is visible to the public, but the group
       may be secret) and groups can have specific settings.

Returns
-------

On completion a JSON object is returned. The ``status`` and
``message`` fields are always set.

``status``:
  * ``0``: success, as a profile was created and the person was
    added to the group.
  * ``1``: success, as a person with an existing profile was
    added to the group.
  * ``256``: failure, as the person was already a group member.
  * ``257``: unexpected failure

``message``:
  A message explaining the status.

In the case that a new member was added to the group, or the
person was already a member of the group (the statuses ``0``,
``1``, and ``256``) then the ``user`` property will be set with
the following values:

``id``:
  The identifier of the profile.

``name``:
  The name of the person.

``url``:
  The URL of the profile.

``groups``:
  A list of identifiers for the groups that the person is a
  member of.

``email``:
  The email addresses associated with the profile.

  * ``all``: All the addresses.
  * ``preferred``: The preferred address or addresses.
  * ``unverified``: The unverified addresses.
  * ``other``: The verified addresses that are not preferred.

Cookie
======

The impetus for creating this end-point is to provide an
mechanism for the JavaScript based bulk adding [#addCSV]_. To see
a list of available parameters, including which parameters are
required, make a ``GET`` request to ``gs-group-member-add.json``
in the Group context.

To add, make a ``POST`` request to ``gs-group-member-add.json``,
supplying all required data via the
``application/x-www-form-urlencoded`` content-type. This request
must include the parameter ``submit`` to indicate the request is
to be processed [#formlib]_. This request must also pass a cookie
with the parameter __ac and a value that corresponds to an
authenticated session.

``fromAddr``
------------

The documentation provided by ``gs-group-member-add.json``
indicates that ``fromAddr`` is required, but does not indicate
that only certain values are accepted: ``fromAddr`` must be an
email address associated with the authenticated session the
submitted cookie corresponds to.

CURL Example
------------

Assuming an instance of GroupServer is running at ``gsbox``, the
following example will attempt to add a user to the Example
Group::

    curl -H "Accept: application/json" -b "__ac=<VALUE_FROM_BROWSER>" 
    -X POST -d "toAddr=example_user%40example.com&fn=Example%20User&delivery=email&message=Hi&fromAddr=<YOUR_EMAIL_ADDRESS>&subject=Welcome&submit" 
    http://gsbox/groups/example_group/gs-group-member-add.json

In Firefox, if you are logged into your GroupServer instance, you
can find the value for ``__ac`` at
<chrome://browser/content/preferences/cookies.xul>.

Resources
=========

- Code repository:
  https://github.com/groupserver/gs.group.member.add.json
- Questions and comments to
  http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. [#token] See ``gs.auth.token`` for more information
   <https://github.com/groupserver/gs.auth.token>

.. [#inviteJSON] The equivalent for inviting people is provided
   by ``gs.group.member.add.json``
   <https://github.com/groupserver/gs.group.member.add.json>

.. [#addCSV] The code for adding people in bulk is provided by
   ``gs.group.member.add.csv``
   <https://github.com/groupserver/gs.group.member.add.csv>

.. [#formlib] Blame ``zope.formlib`` for requiring the ``submit``
   parameter. Or just blame HTTP and HTML for being generally
   messed up when it comes to forms.

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
