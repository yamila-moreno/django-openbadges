Django OpenBadges
=================

Django application to integrated with Mozilla OpenBadges system
(http://openbadges.org/). Every time, a award is given to a user, an assertion
(OBI compliant) is created.

To use this app, it's necessary to configure in the django settings:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "openbadges",
        ...
    ]
    BADGES_BASE_URL = 'http://localhost/'

Base url where assertions will be available. When a user loads a badge to his
backpack, OBI checks the assertion url is correct.

How works?
----------

To generate the assertion, we use some functions attached to post_save signals:

.. code-block:: python

    copy_image_to_award()

Inserts the assertion url to the badge image.

.. code-block:: python

    save_identity_for_user()

Copies the actual user data to the assertion for future consistency.

.. code-block:: python

    create_identity_for_user()

As the assertion identity hash contains the email information, if the email
changes, the identity should also change.
