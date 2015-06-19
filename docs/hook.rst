========
Web hook
========

Synopsis
========

``/gs-group-member-add.json``? :option:`token` =<t> & :option:`groupId` =<g> & :option:`email` =<e> & :option:`fn` =<n> [& :option:`biography` =<b>] [& :option:`tz` =<t>] & :option:`add`


Description
===========

The web hook ``gs-group-member-add.json``, in the **site** context,
adds a person to a group on the site.

* If the person is new to the system then a profile is created
  and the person is added to the group.
* If the person already has a profile then they are just added to
  the group.
* Otherwise an error is raised (see Returns_).

Required arguments
==================

.. option:: token=<token>

  The authentication token [#token]_

.. option:: groupId=<groupId>

  The identifier for the group that the person is joining.

.. option:: email=<address>

  The email address of the new *group* member. The email address
  is used as the identifier for the person (see Returns_):

  * If the email has never been seen by the system then a new
    profile is created,
  * Otherwise an existing profile is added to the group.

.. option:: fn=<name>

  The name of the new member.

.. option:: add

  The action (no value needs to be set, but the argument must be
  present).

Optional arguments
==================

.. option:: biography=<bio>

  The HTML-formatted biography for the new member.

.. option:: tz=<tz>:

  The timezone for the new member.

:Note: Unlike the cookie version (see :doc:`cookie`), the web
       hook can **only** handle the **basic** GroupServer profile
       information. This is because the hook is in the context of
       the site rather than the context of a group (because the
       hook is visible to the public, but the group may be
       secret) and groups can have specific settings.

Returns
=======

On completion a JSON object is returned. In the returned object
the :js:attr:`status` and :js:attr:`message` fields are always
set, with the :js:attr:`user` field usually set.

.. js:class:: Returns()

   .. js:attribute:: status

      * ``0``: success, as a profile was created and the person
        was added to the group.
      * ``1``: success, as a person with an existing profile was
        added to the group.
      * ``256``: failure, as the person was already a group
        member.
      * ``257``: unexpected failure.

   .. js:attribute:: message

      A message explaining the status.

   .. js:attribute:: user

      In the case that a new member was added to the group, or
      the person was already a member of the group (the statuses
      ``0``, ``1``, and ``256``) then the ``user`` property will
      be set with the standard user-property values set (see `the
      core web-hook documentation`_).

Example
=======

Add a person with the name ``A Person`` and the email
``a.person@home.example.com`` to the ``test`` group on
``groups.example.com`` using :command:`wget`.

.. code-block:: console

   $ wget http://groups.example.com/gs-group-member-add.json \
     --post-data='token=Fake&groupId=test&email=a.person@home.example.com@fn=A%20Person&add'

.. _the core web-hook documentation:
   http://groupserver.readthedocs.org/en/latest/webhook.html#profile-data

.. [#token] See ``gs.auth.token`` for more information
   <https://github.com/groupserver/gs.auth.token>
