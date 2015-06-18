Cookie
======
 
.. sectionauthor:: Bill Bushey <bill.bushey@e-democracy.org>

The impetus for creating this end-point is to provide an
mechanism for the JavaScript based bulk adding [#addCSV]_. To see
a list of available parameters, including which parameters are
required, make a ``GET`` request to ``gs-group-member-add.json``
in the Group context.

To add, make a ``POST`` request to ``gs-group-member-add.json``,
supplying all required data via the
:mimetype:`application/x-www-form-urlencoded` content-type. This
request must include the parameter ``submit`` to indicate the
request is to be processed [#formlib]_. This request must also
pass a cookie with the parameter __ac and a value that
corresponds to an authenticated session.

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
Group:

.. code-block:: console

    $ curl -H "Accept: application/json" -b "__ac=<VALUE_FROM_BROWSER>" \
      -X POST -d "toAddr=example_user%40example.com&fn=Example%20User&delivery=email&message=Hi&fromAddr=<YOUR_EMAIL_ADDRESS>&subject=Welcome&submit" \
      http://gsbox/groups/example_group/gs-group-member-add.json

In Firefox, if you are logged into your GroupServer instance, you
can find the value for ``__ac`` at
<chrome://browser/content/preferences/cookies.xul>.

.. [#addCSV] The code for adding people in bulk is provided by
   ``gs.group.member.add.csv``
   <https://github.com/groupserver/gs.group.member.add.csv>

.. [#formlib] Blame ``zope.formlib`` for requiring the ``submit``
   parameter. Or just blame HTTP and HTML for being generally
   messed up when it comes to forms.
