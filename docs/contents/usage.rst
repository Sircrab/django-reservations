Usage
======

Once the application is up and running with the Celery workers and everything properly configured,
you should be greeted by a home screen upon connecting to the server (by default: ``localhost:8000``).

Within the system there are 2 types of registered users, chefs and clients. Whether a user is a
chef or a client user, is only decided by the admin, which manually checks the option within the
admin interface (check the Configuration section if you have any doubts). Any user that registers
with the site's sign up form, will be a client user.

Chef users can do the following:

- Create today's menu and edit existing menus.
- Choose whether to notify and in through which channels to other users when creating a menu.
- Check any order associated with any menu, so they can see who wants what.

Client users can do the following:

- Order from today's menu, provided they haven't already ordered from it and they're still in time
  to do so (by default, before 11 AM CLT)
- Choose the size of their order and also put comments for the particular oder.
- Check their own previous orders, (but not other users).
- Be notified with their registered mail when a new menu is available

Additionaly anyone who has access to the Slack workspace and channel that the server was configured
to send the notification message will be able to access the menu's link.

All the menu's are public. But the options to order only becomes available once logged in.

Wherever you go within the site, there will always be a Navigation Bar, which has options for
logging in and/or signing up, logging out if you're already logged in. And checking your previous
orders if you're a client user. 

As a chef, a button will be available on the Home screen whenever you're capable of creating a new
menu for the day, the Menu form is pretty straightforward. Name the menu, add the options and choose
through which ways you will notify the new menu.

As a client, ordering is easy. Either click on the Today's menu link in the home page, or access a
menu directly through a link. If you're logged in, you haven't ordered already and you're still in
time to order, you can click on the order button.

Ordering is simple, choose which meal out of the options available you want, which size and put any
commentaries if you want to.

If the chef wants to see what have people ordered, simply click the Today's menu (or any menu for
that matter) link, and then click on the "See orders" button, there you will see a list of all the 
orders from that menu, and a quick count for each meal.