from django.shortcuts import redirect
from django.views.generic import UpdateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError
from ..forms import MenuForm, MenuItemFormSet
from ..decorators import chef_required, login_required_message
from ..models import Menu, MenuItem


@method_decorator(
    [
        login_required_message,
        chef_required(message="Usted debe ser chef para acceder a esta página")
    ], name='dispatch')
class MenuEditView(UpdateView):
    template_name = 'reservations/edit_menu.html'
    model = Menu
    form_class = MenuForm
    success_url = 'home'

    def get(self, request, *args, **kwargs):
        """
        Called on GET request of this view, shows a form with an existing menu in it.
        """
        self.object = get_object_or_404(Menu, pk=self.kwargs['unique_id'])
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        menu_item_form = MenuItemFormSet(queryset=MenuItem.objects.filter(menu__exact=self.object))
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
        self.object = None
        try:
            old_menu = Menu.objects.get(pk=self.kwargs['unique_id'])
            old_menu_items = MenuItem.objects.filter(menu__exact=old_menu)
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            menu_item_form = MenuItemFormSet(self.request.POST)
            if(form.is_valid() and menu_item_form.is_valid()):
                return self.form_valid(form, menu_item_form, old_menu, old_menu_items)
            else:
                return self.form_invalid(form, menu_item_form)
        except Exception as e:
            print(e)
            return HttpResponseServerError('Ocurrió un error al tratar de actualizar menú!')

    def form_valid(self, form, menu_item_form, old_menu, old_menu_items):
        """
        Method called upon a succesful validation of both the menu forms and the menu item forms,
        Updates the menu and menuitems with information of the form. Updating the menu's title,
        and editing, deleting or adding menu items.
        DO NOTICE: That if a menu's items are deleted then so will be their corresponding orders!
        """
        # Update title
        self.object = form.save(commit=False)
        old_menu.menu_title = self.object.menu_title
        old_menu.save()
        # Update item text for existing entries, create new ones
        for idx in range(len(menu_item_form)):
            if idx < len(old_menu_items):
                old_item = old_menu_items[idx]
                old_item.item_text = menu_item_form[idx].cleaned_data['item_text']
                old_item.save()
            else:
                new_menu_item = MenuItem(
                    menu=old_menu,
                    item_text=menu_item_form[idx].cleaned_data['item_text'],
                    count=0)
                new_menu_item.save()
        # Delete excess old entries (When editing deletes entries.)
        for idx in range(len(menu_item_form), len(old_menu_items)):
            old_menu_items[idx].delete()
        messages.success(self.request, "Menú actualizado exitosamente!")
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
