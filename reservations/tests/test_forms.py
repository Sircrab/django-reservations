from .. import models, forms
from django.test import TestCase


class SignUpFormTests(TestCase):

    def test_valid_data(self):
        """
        Tests that a form filled with valid data indeed passes the is_valid() method and that
        once saved, all the fields check out and it isn't neither an admin user or a chef user.
        """
        form = forms.SignUpForm({
            'username': "TestName",
            'password1': "ASafePassword1234!",
            'password2': "ASafePassword1234!",
            'email': 'testmail@test.com',
            'first_name': 'John',
            'last_name': 'Doe'
        })
        self.assertTrue(form.is_valid())
        new_user = form.save()
        self.assertEqual(new_user.get_username(), 'TestName')
        self.assertEqual(new_user.email, 'testmail@test.com')
        self.assertEqual(new_user.first_name, 'John')
        self.assertEqual(new_user.last_name, 'Doe')
        self.assertEquals(not new_user.is_chef and not new_user.is_staff, True)

    def test_blank_data(self):
        """
        Tests that a form without any info given does not pass the is_valid()
        """
        form = forms.SignUpForm({})
        self.assertFalse(form.is_valid())


class MenuFormTests(TestCase):

    def test_valid_data(self):
        """
        Tests that a MenuForm filled with valid data (i.e: a menu title), passes the is_valid()
        method and that the fields check out.
        """

        form = forms.MenuForm({
            'menu_title': 'A valid title'
        })
        self.assertTrue(form.is_valid())
        new_menu = form.save()
        self.assertEqual(new_menu.menu_title, 'A valid title')

    def test_blank_data(self):
        """
        Tests that a MenuForm without a title doesn't pass the is_valid method
        """

        form = forms.MenuForm({})
        self.assertFalse(form.is_valid())


class OrderFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(OrderFormTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='dummy_menu')
        dummy_choice = models.MenuItem.objects.create(
            item_text='dummy_1',
            menu=dummy_menu
        )
        models.MenuItem.objects.create(
            item_text='dummy_2',
            menu=dummy_menu
        )
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        cls.client_user = client_user
        cls.dummy_menu = dummy_menu
        cls.dummy_choice = dummy_choice

    def test_valid_data(self):
        """
        Tests that a form filled with valid data for an Order (item_choice, comment and size)
        passes the is_valid() method and that the fields check out.
        """

        form = forms.OrderForm({
            'item_choice': OrderFormTests.dummy_choice.pk,
            'comments': 'Dummy comment',
            'size': models.Order.NORMAL
        })
        self.assertTrue(form.is_valid())
        new_order_without_user = form.save()
        self.assertEquals(new_order_without_user.item_choice, OrderFormTests.dummy_choice)
        self.assertEquals(new_order_without_user.size, models.Order.NORMAL)
        self.assertEquals(new_order_without_user.comments, 'Dummy comment')

    def test_no_item_choice(self):
        """
        Tests that an OrderForm without a MenuItem choice doesn't pass the is_valid method
        """

        form = forms.OrderForm({
            'comments': 'Dummy comment',
            'size': models.Order.LARGE
        })
        self.assertFalse(form.is_valid())

    def test_save_with_user_and_sum(self):
        """
        Tests that an OrderForm with valid info saved with the save_with_user method,
        indeed associates the user to the order and that it sums to the item_choice
        MenuItem's count.
        """
        form = forms.OrderForm({
            'item_choice': OrderFormTests.dummy_choice.pk,
            'comments': 'Dummy comments',
            'size': models.Order.NORMAL
        })
        self.assertTrue(form.is_valid())
        new_order_with_user = form.save_with_user_and_add_to_count(OrderFormTests.client_user)
        self.assertEquals(new_order_with_user.user, OrderFormTests.client_user)
        item_choice = models.MenuItem.objects.get(pk=OrderFormTests.dummy_choice.pk)
        self.assertEquals(item_choice.count, 1)
