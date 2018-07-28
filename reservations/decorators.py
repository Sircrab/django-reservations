from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs
from functools import wraps
from urllib.parse import urlparse

default_message = "Para continuar debe identificarse."

def user_passes_test_message_redirect(
    test_func,
    message=default_message,
    login_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    setting a message in case of no success, and redirects to a login URL.
    The test should be a callable that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user):
                messages.error(request, message)
                path = request.build_absolute_uri()
                resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
                login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
                current_scheme, current_netloc = urlparse(path)[:2]
                if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                    path = request.get_full_path()
                return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def login_required_message(
    function=None,
    message=default_message,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url='login'):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test_message_redirect(
        test_func=lambda u: u.is_authenticated,
        message=message,
        redirect_field_name=REDIRECT_FIELD_NAME,
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def chef_required(function=None,
    message=default_message,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url='login'):
    """
    Decorator for views that are reserved only for chefs
    """
    actual_decorator = user_passes_test_message_redirect(
        lambda u: u.is_active and u.is_chef,
        message=message,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def client_required(function=None,message=default_message, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator for views that are reserved only for clients
    """
    actual_decorator = user_passes_test_message_redirect(
        lambda u: u.is_active and not u.is_chef,
        message=message,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
