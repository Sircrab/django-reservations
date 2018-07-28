from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import CreateView
from ..models import Menu, MenuItem, Order
from ..forms import OrderForm
from ..decorators import login_required_message, client_required
from ..utils import still_in_ordering_time

@method_decorator(
    [
        login_required_message,
        client_required(message="Usted debe ser cliente para acceder a esta página")
    ],
    name='dispatch')
class OrderCreateView(CreateView):
    """
    A CreateView that implements the ordering logic for a menu, provides a form to fill
    the preferences for a new order and also does basic validations, like checking that it's
    still ordering time, the user doesn't have previous order, menu exists, etc.
    """
    model = Order
    template_name = 'reservations/new_order.html'
    success_url = 'home'
    form_class = OrderForm

    class OrderAlreadyFound(Exception):
        """
        Exception that indicates that a given user already has an order associated with a menu.
        """
        pass

    class OutOfDateError(Exception):
        """
        Exception that indicated that an order is trying to be issued on a menu that is out of date
        to do so.
        """
        pass

    def check_no_order_or_fail(self, user, menu):
        """
        Method that looks for a previous order associated with the given menu, if it finds one it
        fails, raising an OrderAlreadyFound exception, otherwise it returns True.

        Attributes:

        **user**
            User to look for any previous order from this menu.
        
        **menu**
            Menu to look for any previous orders from the given user.
        """
        prev_orders = Order.objects.filter(user=user, item_choice__menu=menu)
        if prev_orders:
            raise OrderCreateView.OrderAlreadyFound
        return True

    def check_proper_time_or_fail(self, menu):
        """
        Method that checks that it is still a proper time to order the menu, that is, the menu
        was published today and it is before the previously set ordering time (default: before
        11 AM CLT). If it all checks, return True, otherwise raises an OutOfDateError.

        Attributes:

        **menu**
            Menu which will be checked for date.
        """
        if not menu.published_today() or not still_in_ordering_time():
            raise OrderCreateView.OutOfDateError
        return True

    def get(self, request, *args, **kwargs):
        """
        Called on GET request of this view, shows an empty form to be filled
        """
        try:
            cur_menu = Menu.objects.get(pk=self.kwargs['unique_id'])
            self.check_no_order_or_fail(self.request.user, cur_menu)
            self.check_proper_time_or_fail(cur_menu)
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            form.fields['item_choice'].queryset = MenuItem.objects.filter(menu__exact=cur_menu)
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    menu=cur_menu
                )
            )
        except Menu.DoesNotExist:
            messages.error(self.request, 'El menú al que trató de acceder no existe!')
            return redirect('home')
        except OrderCreateView.OrderAlreadyFound:
            messages.error(self.request, 'Usted ya tiene una orden para este menú!')
            return redirect('home')
        except OrderCreateView.OutOfDateError:
            messages.error(self.request, 'Ya pasó el tiempo para ordernar de este menú')
            return redirect('home')

    def post(self, request, *args, **kwargs):
        """
        called on POST request of this view, takes data from the form, validates it and
        sends an appropiate response (save and redirect or errors)
        """
        try:
            cur_menu = Menu.objects.get(pk=self.kwargs['unique_id'])
            self.check_no_order_or_fail(self.request.user, cur_menu)
            self.check_proper_time_or_fail(cur_menu)
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if(form.is_valid() and self.item_choice_valid(form, cur_menu)):
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except Menu.DoesNotExist:
            messages.error(self.request, 'El menú al que trató de acceder no existe!')
            return redirect('home')
        except OrderCreateView.OrderAlreadyFound:
            messages.error(self.request, 'Usted ya tiene una orden para este menú!')
            return redirect('home')
        except OrderCreateView.OutOfDateError:
            messages.error(self.request, 'Ya pasó el tiempo para ordernar de este menú')
            return redirect('home')

    def item_choice_valid(self, form, cur_menu):
        """
        Method used to verify that an order's item choice is indeed associated with the given menu.

        Arguments:

        **form**
            Form that will be used to build the Order object
        **cur_menu**
            Menu that will be checked against the Order object's MenuItem.
        """
        cur_order = form.save(commit=False)
        valid_choices = MenuItem.objects.filter(menu__exact=cur_menu)
        return cur_order.item_choice in valid_choices

    def form_valid(self, form):
        """
        Method called upon a succesful validation of the order form and item choice validation,
        created the order and associates it to the user, giving feedback that the order was
        correctly added and redirecting them. It also adds one to the count for this order.
        """
        self.object = form.save_with_user_and_add_to_count(self.request.user)
        messages.success(self.request, "Orden añadida exitosamente!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Method called upon an unsuccesful validation of any of the order or invalid item choice,
        sends errors to the user to be displayed.
        """
        return self.render_to_response(
            self.get_context_data(
                form=form
            )
        )
