# Django Reservations application

This is an implementation for a Django reservations app, it was developed in Django 2.1, along with the following dependencies:

- `Sphinx`
- `django-bootstrap3`
- `django-bootstrap-dynamic-formsets`
- `Celery`
- `django-celery-email`
- `django-slack`

It features a simple chef/user account systems which allows for:

### Chefs:
- Create and Edit menus
- See user's orders
- Notify users via emails or Slack channel of a new menu (Async)
- Generate links which allow users to order from a menu.
- Limit the hour in which menus can be ordered.

### Users:
- Order from menus
- Add comments and choose the size of their meals.
- See their previous orders (but not other user's)


## Installation

In order to run this application, you must have Python installed along with PyPI, after having downloaded
this project, please run the following command inside the project's folder:

`pip install -r requirements.txt`

After this, all the project's dependencies will be installed. From there, further installation instructions are located
within the included documentation.

In order to access the documentation, open a shell within the `docs` folder of the project and run the following command:
`make html`

After this, an HTML with all of the documentation will be located within the `_build/html` folder of the `docs` folder.
Just open the `index.html` file with your favorite internet browser to see the documentation.
