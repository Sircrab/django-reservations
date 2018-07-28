import datetime
from django.utils import timezone
from django.core import mail
from django.urls import reverse
from django_slack import slack_message
from django.contrib.sites.models import Site
from django.conf import settings

def still_in_ordering_time():

    """
    Utility function that returns True if it's still an ordering time (before 11 AM CLT), False
    otherwise.
    """
    return (timezone.localtime().time() < datetime.time(settings.NORA_ORDER_HOUR_LIMIT))


def send_notification_mails(users, menu, request):

    """
    Utility function to notify users of a new menu, Uses celery to send mails asynchronously,
    returning inmediately once the order is sent.

    Arguments:

    **users**
        Queryset of users to send the notification mail to.

    **menu**
        A Menu model object which will be used to form the mail's message
    """
    # NOTE: get_current() from Sites model caches after the first call!
    message = """ Esta es una notificación automatica del sistema de almuerzos Nora, para avisarte
    que un nuevo menú se encuentra disponible!, para más información por favor revisa el siguiente
    link: """
    message += 'https://' + Site.objects.get_current().domain + reverse('menu', kwargs={'unique_id': menu.unique_id})
    subject = "Nuevo menú del dia de hoy"
    from_mail = "no-reply-reservations@reservations.com"
    emails = ()
    for user in users:
        emails = ((subject, message, from_mail, [user.email]),) + emails
    results = mail.send_mass_mail(emails)


def send_slack_message(request, menu):

    """
    Utility function that send a notification message via the Slack channel specified in the
    settings file through a Celery backend (which means is done asynchronously).
    The message contains the link to the new menu.

    Arguments:
    **menu**
        A Menu model object which will be used to form the message's menu link
    """
    slack_message(
        'slack/new_menu_notification.slack',
        {'menu': menu, 'host': Site.objects.get_current().domain}
    )
