from django.views.generic import ListView
from django.utils import timezone
from ..models import Menu


class HomeView(ListView):
    """
    Simple ListView that uses the home template, the template itself differentiates
    the content based on whether or not the user is authenticated and/or a chef.
    """
    model = Menu
    template_name = 'reservations/home.html'
    context_object_name = 'menus'
    paginate_by = 10
    today_date = timezone.localdate()
    queryset = Menu.objects.filter(created__date__lt=today_date)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        today_menu = Menu.todays_menu.all()
        context['today_menu'] = today_menu
        return context
