Installation
============

Dependencies
------------

This application has the following Python dependencies:

- ``Django 2.1``
- ``Sphinx``
- ``django-bootstrap3``
- ``django-bootstrap-dynamic-formsets``
- ``Celery``
- ``django-celery-email``
- ``django-slack``

In addition to these dependencies, any other dependencies that these packages may have, are 
noted down inside the ``requirements.txt`` file in the project folder.

To install these dependencies, simply run the command:

``pip install -r requirements.txt``

From your shell, while located inside the project's folder.

Since this project also uses Celery, a "broker" between the Django application and the Celery workers
is necessary in order to function. There are several brokers available, for the development and testing
of this application ``RabbitMQ-Server`` was used as a broker, and as such is the default configuration
inside the settings.

In order to install this broker, simply head over to `this page <https://www.rabbitmq.com/download.html>`_
for instructions.

In Ubuntu or any other Debian based Linux build, you can also run the following command from the shell:

``sudo apt-get install rabbitmq-server``

After the installation is complete, the broker will be running in the background.

Configuration
-------------

After you've downloaded the project, installed the dependencies and prepared the Celery broker
it becomes necessary to configure a few setting before the app can be run without issues.

First, perform a database migration by running the following command:

``python manage.py migrate``

Afterwards, a super user must be created, in order to configure some settings from the admin interface,
run the following command and follow the prompts:

``python manage.py createsuperuser``

After a super user has been created, the server can be run with the command:

``python manage.py runserver``

If all went succesfully, you will be able to connect to the default host and port:

``locahost:8000``

From here, please enter through a web browser of you choosing to the admin interface, located at:

``localhost:8000/admin``

After putting your credentials, you will be able to see all the tables and models that the application
uses. In particular, we'll be looking at 2 tables of interest:

- ``Sites``
- ``Users``

Within the ``Sites`` models, you will find that there should be a single entry with the data ``example.com``.
This, will be the domain which will host the application, that will be used for generating the links in the
notifications. If you wish to change it, simply click on it and change both fields to the new domain.

Within the ``Users`` mdeols, you will find that there should be a single entry with the use you just
created. If you click in any user in this table, you will find that there is at the bottom of the
fields you can modify, a single checkbox with the words "is chef". If you check and save that option
for any user, that user will become a chef and it will be able to create menus, and see orders from
other users.

After saving these changes, you will be able to begin using the application by connecting to the
``localhost:8000`` URL in your browser. From here you can also create new users, which will be
marked as "client" users, that is, they will only be able to order and see menus, but not create
menus or see other users orders (but can see their own).

In order to have the notification functionalities working in order, a broker, a celery worker and
the server, must be running for the asynchronous tasks to work. If you installed the RabbitMQ broker,
you should already be running the broker in the background. The only thing remaining is running the
Celery worker, run this command within the project's folder in order to do so:

``celery worker -A nora --loglevel debug``

With that command, a celery worker will be initiated and it will report everything that happens through
it, keep that terminal open while the server is running.

To make sure that everything is in order for the notifications to work, the application must also be
properly configured. Please refer to the Settings section for more details.

Testing
--------

In order to run the tests, once everything has been properly configured and with the server not running
simply run the command:

``python manage.py test``

From the project's folder inside a shell

