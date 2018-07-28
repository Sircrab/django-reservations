from django.shortcuts import redirect
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from ..forms import MenuForm, MenuItemFormSet
from ..decorators import chef_required, login_required_message
from ..models import Menu, MenuItem, User
from ..utils import send_notification_mails, send_slack_message


@method_decorator(
    [
        login_required_message,
        chef_required(message="Usted debe ser chef para acceder a esta página")
    ], name='dispatch')
class MenuCreateView(CreateView):
    template_name = 'reservations/new_menu.html'
    model = Menu
    form_class = MenuForm
    success_url = 'home'

    def get(self, request, *args, **kwargs):
        """
        Called on GET request of this view, shows an empty form to be filled
        """
        if Menu.todays_menu.all():
            messages.error(request, '¡Ya se publicó el menú de hoy, no puede crear otro!')
            return redirect('home')
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        menu_item_form = MenuItemFormSet(queryset=MenuItem.objects.none())
        return self.render_to_response(
            self.get_context_data(
                form=form,
                menu_item_form=menu_item_form
            )
        )

    def post(self, request, *args, **kwargs):
        """
        called on POST request of this view, takes data from the form, validates it and
        sends an appropiate response (save and redirect or errors)
        """
        if Menu.todays_menu.all():
            messages.error(request, '¡Ya se publicó el menú de hoy, no puede crear otro!')
            return redirect('home')
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        menu_item_form = MenuItemFormSet(self.request.POST)
        if(form.is_valid() and menu_item_form.is_valid()):
            return self.form_valid(form, menu_item_form)
        else:
            return self.form_invalid(form, menu_item_form)

    def form_valid(self, form, menu_item_form):
        """
        Method called upon a succesful validation of both the menu forms and the menu item forms,
        adds the menu and the menuitems to the database and redirects to home with a success
        message.
        """
        self.object = form.save()
        for item_form in menu_item_form:
            new_menu_item = MenuItem(
                menu=self.object,
                item_text=item_form.cleaned_data['item_text'],
                count=0)
            new_menu_item.save()
        # Notify via Mail
        if('notify_mail' in self.request.POST and self.request.POST['notify_mail'] == 'on'):
            users_to_mail = User.objects.all()
            send_notification_mails(users_to_mail, self.object, self.request)
        # Notify via Slack
        if('notify_slack' in self.request.POST and self.request.POST['notify_slack'] == 'on'):
            send_slack_message(self.request, self.object)
        messages.success(self.request, "Menú añadido exitosamente!")
        return redirect(self.get_success_url())

    def form_invalid(self, form, menu_item_form):
        """
        Method called upon an unsuccesful validation of any of the menu or menu item forms,
        sends the error messages to the user.
        """
        return self.render_to_response(
            self.get_context_data(
                form=form,
                menu_item_form=menu_item_form
            )
        )
