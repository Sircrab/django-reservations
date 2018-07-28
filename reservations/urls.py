from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .class_views import OrderCreateView, HomeView, MenuCreateView, MenuEditView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup', views.signup, name='signup'),
    path(
        'login',
        auth_views.LoginView.as_view(template_name='reservations/login.html'),
        name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('menu/<uuid:unique_id>', views.menu, name='menu'),
    path('edit_menu/<uuid:unique_id>', MenuEditView.as_view(), name='edit_menu'),
    path('new_menu', MenuCreateView.as_view(), name='new_menu'),
    path('new_order/<uuid:unique_id>', OrderCreateView.as_view(), name='new_order'),
    path('menu_orders/<uuid:unique_id>', views.view_menu_orders, name='menu_orders'),
    path('view_orders/<int:user_id>', views.view_user_orders, name='user_orders')

]
