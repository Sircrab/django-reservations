Settings
=========

Inside the ``settings.py`` file defined inside the project's main folder ``nora``, lie
many of the configuration variables that are needed to run the application. Although
they are commented inside this very same file, here is the purpose of some of those settings:

* ``DEBUG``:
    A boolean indicating if the application should be run in debug mode or not, for production
    switch this to ``False``.

* ``TIME_ZONE``:
    Time zone that will be used for calculating the hours inside the application.
    Used for the creation dates of the menus and also for checking if a client can order from
    a menu or not.

* ``AUTH_USER_MODEL``:
    Because this application doesn't use the standard Django User model, this settings tells
    the system to use this model for authentication/

* ``LOGIN_URL``:
    URL name (as in, the urls.py name property) of the View that is to be used as a login page

* ``LOGIN_REDIRECT_URL``:
    URL name (like before) of the View that is to be used as a redirection page after succesfully
    logging in.

* ``LOGOUT_REDIRECT_URL``:
    Similar to the one before, but for redirection after logging out.

* ``CELERY_BROKER_URL``:
    Because this application uses Celery in order to manage any asynchronous task (such as sending
    emails and slack messages), a "broker" is needed to communicate between the Django application
    and the Celery workers. This URL represents the access point that the Celery workers will try to
    use to communicate with the application. By default, this is the default URL provided by the
    RabbitMQ-Server broker, however should the need arise to use a different one (such as Redis),
    use this parameter to specify the new broker.

* ``EMAIL_BACKEND``:
    Setting from the app ``django_celery_email`` that specifies that the email backend will be
    Celery. This effectively "patches" the ``django.core.mail`` calls and redirects them to the
    Celery queue to be executed as tasks.

* ``EMAIL_USE_TLS``:
    Standard Django mail setting used to send emails under secure encryption.

* ``EMAIL_HOST``:
    The SMTP host mail server that will be used for sending the emails. Obviously if a different
    account or server will be used than the one provided, you can change this setting.

* ``EMAIL_PORT``:
    Port for the SMTP server connection

* ``EMAIL_HOST_USER``:
    The user which will be used to log in to the SMTP server and send the emails. If you're going
    to use a different account or server, change this setting.

* ``EMAIL_HOST_PASSWORD``:
    The password that will be used to log in to the SMTP server to send the emails. Same as before,
    change it if you need to.

* ``SLACK_TOKEN``:
    In order to send notifications from the application to a Slack channel, it is necessary to
    provide a "token" that provides authorization and authentication to send messages in a workspace.
    To generate the tokens, `this page <http://django-slack.readthedocs.io/>`_  has some good links
    and tips to do so. Once that token is generated, simply put it in this setting.

* ``SLACK_CHANNEL``:
    Self-explanatory, the token in the Slack workspace where the messages will be sent, don't
    forget to put the hashtag(#)

* ``SLACK_BACKEND``:
    A setting from the ``django-slack`` app that was used for Slack integration. By default it uses
    the Celery backend, which will handle the messages asynchronously, so long as a Celery worker
    is active.

* ``SLACK_BACKEND_FOR_QUEUE``:
    Another setting from the ``django-slack`` app, indicates the backend which will be used by the
    tasks inside the Celery Queue to actually process and send the messages.

* ``SITE_ID``:
    A Django setting from the "sites" framework that is used to indicate the current domain in which
    the server is running. Used for retrieving the domain in order to build a full URL to form the
    notification messages for Slack and Emails. The installation guide goes into a bit more detail
    about setting the domain.

* ``NORA_ORDER_HOUR_LIMIT``:
    Setting from the Nora reservations app, indicates up which hour (in a 24 hour format), it is
    possible for a client to order from a Menu that was published that day, after this hour, the
    ordering view will be blocked until a new menu is published the next day. 

Regarding HTTPS
---------------

Within the settings files there is a commented block with the settings necessary for activating
HTTPS for the application. However, doing so without having a SSL certificate will result in the
application not being able to send any pages or responding any requests. In order to properly
use HTTPS, a certificate must be acquired (or generated) and a proper deployment solution (such as
NGINX) must be used.
