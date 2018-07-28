from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Menu, MenuItem, Order, User
from .utils import still_in_ordering_time
from .forms import SignUpForm
from .decorators import chef_required, login_required_message
from django.shortcuts import get_object_or_404
from django.contrib import messages


def menu(request, unique_id):
    """
    Simple view for visualizing a single menu, returns 404 if the menu does not exist,
    otherwise it gets the Menu info, it's items and if the user is a client, any order
    associated with this menu (to see if he can order or not).
    Doesn't require authentication to visualize (But cannot do much other than see the items).

    Arguments:

    **request**
        The request object which was sent to this view
    **unique_id**
        The UUID recovered from the URL that is used to retrieve the menu.
    """
    cur_menu = get_object_or_404(Menu, pk=unique_id)
    menu_items = MenuItem.objects.filter(menu__exact=cur_menu)
    context = {
        'menu': cur_menu,
        'menu_items': menu_items
    }
    if request.user.is_authenticated and not request.user.is_chef:
        try:
            if still_in_ordering_time():
                context['in_order_time'] = True
            cur_order = Order.objects.filter(user__exact=request.user, item_choice__menu=cur_menu)
            if cur_order:
                context['order'] = cur_order
        except Order.DoesNotExist:
            pass
    return render(request, 'reservations/menu.html', context)


def signup(request):
    """
    Simple view for a signup form, it uses the custom SignUpForm in order to support the additional
    user fields, this signup form is ONLY for clients, chef users need to be set via admin.
    After a succesful signup, it logins.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request,"Usuario creado exitosamente!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'reservations/signup.html', {'form': form})


@login_required_message
@chef_required(message="Usted debe ser chef para poder ver esta página!")
def view_menu_orders(request, unique_id):
    """
    Simple view for visualizing a specific menu's associated orders, it throws 404 if the menu is
    not found. This view can only be seen by an authenticated chef user.

    Arguments:

    **request**
        The request object which was sent to this view
    **unique_id**
        The UUID recovered from the URL that is used to retrieve the menu.
    """
    cur_menu = get_object_or_404(Menu, pk=unique_id)
    menu_items = MenuItem.objects.filter(menu__exact=cur_menu)
    context = {
        'menu': cur_menu,
        'menu_items': menu_items
    }
    all_orders = Order.objects.filter(item_choice__menu=cur_menu)
    cur_page = request.GET.get('page', 1)
    paginator = Paginator(all_orders, 10)
    try:
        cur_orders = paginator.page(cur_page)
    except PageNotAnInteger:
        cur_orders = paginator.page(1)
    except EmptyPage:
        cur_orders = paginator.page(paginator.num_pages)
    context['orders'] = cur_orders
    return render(request, 'reservations/menu_orders.html', context)

@login_required_message
def view_user_orders(request, user_id):
    """
    Simple view for visualizing an user specific orders, it throws 404 if the user doesn't exist,
    or redirects with an error if the user doesn't have authorization to see the orders.

    Arguments:

    **user_id**
        A user ID derived from the URL, used to check if the user has access to this view.
    """
    cur_user = get_object_or_404(User, pk=user_id)
    if(not request.user.is_chef and cur_user != request.user):
        messages.error(request, 'Usted no esta autorizado para entrar a esta página!')
        return redirect('home')
    all_orders = Order.objects.filter(user__exact=cur_user)
    cur_page = request.GET.get('page', 1)
    paginator = Paginator(all_orders, 10)
    try:
        cur_orders = paginator.page(cur_page)
    except PageNotAnInteger:
        cur_orders = paginator.page(1)
    except EmptyPage:
        cur_orders = paginator.page(paginator.num_pages)
    return render(
        request, 'reservations/view_orders.html',
     {'orders': cur_orders, 'req_user': cur_user}
     )
