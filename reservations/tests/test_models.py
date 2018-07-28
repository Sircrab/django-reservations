import datetime
from django.test import TestCase
from django.utils import timezone
from .. import models


class MenuTests(TestCase):

    def test_published_today_with_past_menu(self):
        """
        A menu that was published in the past must return False to published_today
        """
        past_time = timezone.localtime() + datetime.timedelta(days=-5)
        past_menu = models.Menu()
        past_menu.created = past_time
        self.assertIs(past_menu.published_today(), False)

    def test_published_today_with_today_menu(self):
        """
        A menu that was published today must return True to published_today
        """
        cur_time = timezone.localtime()
        today_menu = models.Menu()
        today_menu.created = cur_time
        self.assertIs(today_menu.published_today(), True)
