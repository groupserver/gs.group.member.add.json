============================
``gs.group.member.add.json``
============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add a member to a GroupServer Group using JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-01-08
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product provides an API to allow people to be added to groups, without
sending an invitation [#inviteJSON]_.

The impetus for creating this product is to provide an end point for the
JavaScript based bulk adding [#addCSV]_. However, any code which can submit
a properly formatted request should be able to use this end point to add
people to groups.

Usage
=====

To see a list of available parameters, including which parameters are
required, make a ``GET`` request to ``gs-group-member-add.json`` in the
Group context.

To add, make a ``POST`` request to ``gs-group-member-add.json``, supplying
all required data via the ``application/x-www-form-urlencoded``
content-type. This request must include the parameter ``submit`` to
indicate the request is to be processed [#formlib]_. This request must also
pass a cookie with the parameter __ac and a value that corresponds to an
authenticated session.


``fromAddr``
------------

The documentation provided by ``gs-group-member-add.json`` indicates that
``fromAddr`` is required, but does not indicate that only certain values
are accepted: ``fromAddr`` must be an email address associated with the
authenticated session the submitted cookie corresponds to.

CURL Example
------------

Assuming an instance of GroupServer is running at ``gsbox``, the following
example will attempt to add a user to the Example Group::

    curl -H "Accept: application/json" -b "__ac=<VALUE_FROM_BROWSER>" 
    -X POST -d "toAddr=example_user%40example.com&fn=Example%20User&delivery=email&message=Hi&fromAddr=<YOUR_EMAIL_ADDRESS>&subject=Welcome&submit" 
    http://gsbox/groups/example_group/gs-group-member-invite-json.html

In Firefox, if you are logged into your GroupServer instance, you can find
the value for ``__ac`` at <chrome://browser/content/preferences/cookies.xul>.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.add.json
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/
.. [#inviteJSON] The equivalent for inviting people is provided by 
                 <https://source.iopen.net/groupserver/gs.group.member.add.json>
.. [#addCSV] The code for adding people in bulk is provided by
             <https://source.iopen.net/groupserver/gs.group.member.add.csv>
.. [#formlib] Blame ``zope.formlib`` for requiring the ``submit``
              parameter. Or just blame HTTP and HTML for being generally
              messed up when it comes to forms.
