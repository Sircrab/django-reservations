import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """
    Extended User model

    Extended User model which contains whether the User is a chef or not.
    Chefs can create and edit menus, whereas regular users can only order from them.

    Attributes:

    **is_chef**
        Boolean that determines if this user is a chef (True) or a client (False)

    """
    is_chef = models.BooleanField(default=False)

class MenuManager(models.Manager):
    """
    Manager for checking the menu published today, used to avoid publishing of 2 menus in a single
    day.
    """
    def get_queryset(self):
        return super().get_queryset().filter(created__date=timezone.localdate())

class Menu(models.Model):
    """
    Model holding menu data

    A menu contains a title, the date in which it was created and last modified, as well as a
    unique id which will identify this menu.

    Attributes:

    **menu_title**
        A Char field that contains a title for this menu.

    **created**
        A Date/Time field that represents the time of creation of this menu.

    **modified**
        A Date/Time field that represents the last time this menu was modified.

    **unique_id**
        A UUID field that uniquely identifies this menu.
    """
    # Default manager
    objects = models.Manager()

    menu_title = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    todays_menu = MenuManager()

    def __str__(self):
        return self.menu_title

    def published_today(self):
        """
        returns True if this menu entry was published within today's date, False otherwise.
        """
        return timezone.localtime(self.created).date() == timezone.localdate()

    class Meta:
        ordering = ['-created']

class MenuItem(models.Model):
    """
    Model holding a specific's menu's item data

    A MenuItem is associated to a single menu, and it's just some text that represents a lunch
    option and how many times it's been ordered.

    Attributes:

    **menu**
        A Foreign key to the menu this choice is from.
    **item_text**
        A Char field with the menu's choice itself.
    **count**
        An Int field with the number of times this menu item has been ordered.
    """
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    item_text = models.CharField(max_length=200)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.item_text

class Order(models.Model):
    """
    Model holding a client's order data.

    An order contains an unique_id (since each order is indeed unique), the date it was made,
    a MenuItem selection (which in turn references the Menu), comments and a size selection from 2
    possible sizes: Normal and Large. It also contains the user that made the order.

    Attributes:

    **unique_id**
        A UUID field that uniquely identifies this order.
    **created**
        A Date/Time field that represents the time of creation of this order
    **item_choice**
        A Foreign key with this order's menu choice.
    **comments**
        A Char field with any additional comments to the order.
    **size**
        A Small Int field that represents the size choice for this order.
    **user**
        A Foreign key to the user who issued this order.
    """
    NORMAL = 0
    LARGE = 1
    MEAL_SIZES = (
        (NORMAL, 'Normal'),
        (LARGE, 'Large')
    )
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    item_choice = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    comments = models.CharField(max_length=200, blank=True)
    size = models.SmallIntegerField(choices=MEAL_SIZES, default=NORMAL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-created']