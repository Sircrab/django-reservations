from django import forms
from django.forms.models import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F
from .models import User, Menu, MenuItem, Order


class SignUpForm(UserCreationForm):
    """
    Custom SignUpForm based on a UserCreationForm, it asks (and validates) for:
    - Username
    - First Name
    - Last Name
    - Email
    - Password
    - Repeat Password
    """
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        email = {
            'required': True
        }

    def save(self, commit=True):
        """
        Override of the default save functionality for this form, ensures that a user created
        by this method is NOT a chef.
        """
        user = super().save(commit=False)
        user.is_chef = False
        if commit:
            user.save()
        return user


class MenuForm(forms.ModelForm):
    """
    Model form for filling up a menu, just shows and validates the menu title.
    """
    class Meta:
        model = Menu
        fields = ['menu_title']
        labels = {
            'menu_title': ("Título del menú")
        }


class OrderForm(forms.ModelForm):
    """
    Model form for filling up an order, the user is filled automatically.
    The items to fill are the choice from a menu, optional comments and a size.
    """
    class Meta:
        model = Order
        fields = ['item_choice', 'comments', 'size']
        labels = {
            'item_choice': ("Opción de menú"),
            'comments': ('Comentaios de la orden'),
            'size': ('Tamaño')
        }

    def save_with_user_and_add_to_count(self, user):
        """
        Method to save an Order, associate the order with a given user and add one to the count
        of the MenuItem choice.

        Arguments:

        **user**
            An User model object to associate the current entry to be saved with.
        """
        order = super().save(commit=False)
        order.user = user
        order.save()
        cur_choice = order.item_choice
        cur_choice.count = F('count') + 1
        cur_choice.save()
        return order

# ModelFormSet based on the MenuItem model, just asks for the name of the menu item,
# used for dynamic forms in the create and edit menu views.
MenuItemFormSet = modelformset_factory(
    MenuItem,
    fields=('item_text',),
    labels={'item_text': ("Nombre del plato")},
    can_delete=True,
    min_num=1,
    extra=0,
    validate_min=True)
