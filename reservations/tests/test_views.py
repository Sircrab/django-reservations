import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages.storage.cookie import CookieStorage
from django.utils import timezone
from .. import models


def get_messages_as_list(response):
    return CookieStorage(response)._decode(response.cookies['messages'].value)


class SignUpTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            'username': 'test',
            'first_name': 'test',
            'last_name': 'test',
            'password1': 'uniqueTestingPassword123',
            'password2': 'uniqueTestingPassword123',
            'email': 'test@test.com',
        }

    def test_user_added_on_signup(self):
        """
        Tests that after a succesful signup the user is effectively added to the database.
        """
        response = self.client.post(reverse('signup'), self.data)
        # Check redirection
        self.assertEquals(response.status_code, 302)
        user = models.User.objects.get(username="test")
        self.assertEquals(user is not None, True)

    def test_user_logged_in(self):
        """
        Tests that a user is effectively logged in after a succesful signup process
        """
        response = self.client.post(reverse('signup'), self.data)
        self.assertEquals(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_created_user_is_not_chef_or_admin(self):
        """
        Tests that a user created by the signup process is not either a chef or an admin user,
        (which can enter the admin panel)
        """
        response = self.client.post(reverse('signup'), self.data)
        self.assertEquals(response.status_code, 302)
        user = models.User.objects.get(username="test")
        self.assertEquals(not user.is_chef and not user.is_staff, True)


class MenuTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(MenuTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='Dummy menu')
        dummy_choice = models.MenuItem.objects.create(item_text='dummy_1', menu=dummy_menu)
        models.MenuItem.objects.create(item_text='dummy_2', menu=dummy_menu)
        dummy_user = models.User.objects.create(username='testuser')
        dummy_user.set_password('12345')
        dummy_user.is_chef = False
        dummy_user.save()
        cls.valid_menu = dummy_menu
        cls.dummy_user = dummy_user
        cls.dummy_choice = dummy_choice

    def test_404_on_non_existent_menu(self):
        """
        Tests that trying to access to a menu whose uuid that doesn't exist results in 404 error.
        """
        invalid_uuid = '5bfa3016-ded3-424c-9140-5b0554d962a6'
        response = self.client.get(reverse('menu', kwargs={'unique_id': invalid_uuid}))
        self.assertEquals(response.status_code, 404)

    def test_menu_displays(self):
        """
        Tests that an existing menu is indeed sent to the template on correct URL.
        """
        response = self.client.get(reverse(
            'menu',
            kwargs={'unique_id': MenuTests.valid_menu.unique_id}))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['menu'], MenuTests.valid_menu)

    def test_catch_prev_order(self):
        """
        Tests that a logged in user which has a previous order sends is detected, and the previous
        order is sent to the template via context.
        """
        self.client.login(username='testuser', password='12345')
        dummy_order = models.Order.objects.create(
            item_choice=MenuTests.dummy_choice,
            user=MenuTests.dummy_user
        )
        response = self.client.get(
            reverse(
                'menu',
                kwargs={'unique_id': MenuTests.valid_menu.unique_id}
            )
        )
        self.assertEquals(response.context['order'].first(), dummy_order)


class ViewMenuOrderTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(ViewMenuOrderTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='Dummy menu')
        dummy_choice = models.MenuItem.objects.create(
            item_text='dummy_1',
            menu=dummy_menu
        )
        models.MenuItem.objects.create(
            item_text='dummy_2',
            menu=dummy_menu
        )
        chef_user = models.User.objects.create(username='chef_user')
        chef_user.set_password('12345')
        chef_user.is_chef = True
        chef_user.save()
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        cls.chef_user = chef_user
        cls.client_user = client_user
        cls.dummy_menu = dummy_menu
        cls.dummy_choice = dummy_choice

    def test_404_on_non_existent_menu(self):
        """
        Tests that trying to access to a menu's orders that doesn't exist returns a 404
        """
        self.client.login(username='chef_user', password='12345')
        invalid_uuid = '5bfa3016-ded3-424c-9140-5b0554d962a6'
        response = self.client.get(reverse('menu_orders', kwargs={'unique_id': invalid_uuid}))
        self.assertEquals(response.status_code, 404)

    def test_block_anonymous_user(self):
        """
        Tests that trying to access to a valid menu's orders without login in is blocked
        """
        response = self.client.get(
            reverse(
                'menu_orders',
                kwargs={'unique_id': ViewMenuOrderTests.dummy_menu.unique_id}
            )
        )
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Para continuar debe identificarse.")

    def test_block_client_user(self):
        """
        Tests that trying to access to a valid menu's orders while logged in as a client results
        in a redirection and an error message
        """
        self.client.login(username='client_user', password='12345')
        response = self.client.get(reverse(
            'menu_orders',
            kwargs={'unique_id': ViewMenuOrderTests.dummy_menu.unique_id})
        )
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Usted debe ser chef para poder ver esta página!")

    def test_show_orders_to_chef(self):
        """
        Tests that trying to access to a valid menu's orders while logged in as a chef results
        in the correct orders being sent to the template.
        """
        dummy_order = models.Order.objects.create(
            item_choice=ViewMenuOrderTests.dummy_choice,
            user=ViewMenuOrderTests.client_user)
        self.client.login(username='chef_user', password='12345')
        response = self.client.get(reverse(
            'menu_orders',
            kwargs={'unique_id': ViewMenuOrderTests.dummy_menu.unique_id})
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['menu'], ViewMenuOrderTests.dummy_menu)
        self.assertEquals(response.context['orders'].object_list[0], dummy_order)


class ViewClientOrdersTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(ViewClientOrdersTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='Dummy menu')
        dummy_choice = models.MenuItem.objects.create(
            item_text='dummy_1',
            menu=dummy_menu
        )
        models.MenuItem.objects.create(
            item_text='dummy_2',
            menu=dummy_menu
        )
        chef_user = models.User.objects.create(username='chef_user')
        chef_user.set_password('12345')
        chef_user.is_chef = True
        chef_user.save()
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        different_client_user = models.User.objects.create(username='different_client_user')
        different_client_user.set_password('12345')
        different_client_user.save()
        cls.chef_user = chef_user
        cls.client_user = client_user
        cls.dummy_menu = dummy_menu
        cls.dummy_choice = dummy_choice
        cls.different_client_user = different_client_user

    def test_404_on_non_existent_user(self):
        """
        Tests that a 404 response is returned in case of trying to access a non existing user.
        """
        self.client.login(username='client_user', password='12345')
        non_existent_user_id = 999
        response = self.client.get(reverse(
            'user_orders',
            kwargs={'user_id': non_existent_user_id})
        )
        self.assertEquals(response.status_code, 404)

    def test_block_anonymous_user(self):
        """
        Tests that an anonymous user is redirected and given an error message on trying to access
        a valid user's order
        """
        response = self.client.get(reverse(
            'user_orders',
            kwargs={'user_id': ViewClientOrdersTests.client_user.pk})
        )
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Para continuar debe identificarse.")

    def test_block_different_user(self):
        """
        Tests that a client user cannot see a different client's orders, redirecting and returning
        a message
        """
        self.client.login(username='client_user', password='12345')
        response = self.client.get(reverse(
            'user_orders',
            kwargs={'user_id': ViewClientOrdersTests.different_client_user.pk})
        )
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), 'Usted no esta autorizado para entrar a esta página!')

    def test_same_user_can_access(self):
        """
        Tests that a client can see his own orders, resulting in the orders being sent to the
        template.
        """
        dummy_order = models.Order.objects.create(
            item_choice=ViewClientOrdersTests.dummy_choice,
            user=ViewClientOrdersTests.client_user
        )
        self.client.login(username='client_user', password='12345')
        response = self.client.get(reverse(
            'user_orders',
            kwargs={'user_id': ViewClientOrdersTests.client_user.pk})
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['orders'].object_list[0], dummy_order)

    def test_chef_user_can_access(self):
        """
        Tests that a chef user can access a different user's orders and see them, resulting
        in the orders being sent to the template
        """
        dummy_order = models.Order.objects.create(
            item_choice=ViewClientOrdersTests.dummy_choice,
            user=ViewClientOrdersTests.different_client_user
        )
        self.client.login(username='chef_user', password='12345')
        response = self.client.get(reverse(
            'user_orders',
            kwargs={'user_id': ViewClientOrdersTests.different_client_user.pk})
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['orders'].object_list[0], dummy_order)


class CreateMenuViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(CreateMenuViewTests, cls).setUpClass()
        chef_user = models.User.objects.create(username='chef_user')
        chef_user.set_password('12345')
        chef_user.is_chef = True
        chef_user.save()
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        cls.chef_user = chef_user
        cls.client_user = client_user

    def test_anonymous_user_redirect(self):
        """
        Tests that an anonymous user cannot enter the create menu view, instead, it is redirected
        to the login screen with a corresponding message.
        """
        response = self.client.get(reverse('new_menu'))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Para continuar debe identificarse.")

    def test_client_user_redirect(self):
        """
        Tests that a client user cannot enter the create menu view, instead, it is redirected
        to the login screen with a corresponding message.
        """
        self.client.login(username='client_user', password='12345')
        response = self.client.get(reverse('new_menu'))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Usted debe ser chef para acceder a esta página")

    def test_chef_user_can_enter(self):
        """
        Tests that a chef user can indeed connect to the create menu view.
        """
        self.client.login(username='chef_user', password='12345')
        response = self.client.get(reverse('new_menu'))
        self.assertEquals(response.status_code, 200)

    def test_chef_user_can_publish_menu(self):
        """
        Tests that a chef client that sends by POST a valid Menu form, gets added to the database
        """
        self.client.login(username='chef_user', password='12345')
        response = self.client.post(reverse('new_menu'), {
            'menu_title': 'Test menu',
            'form-0-item_text': 'Menu 1',
            'form-0-id': '',
            'form-1-id': '',
            'form-1-item_text': 'Menu 2',
            'form-TOTAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000'
        })
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Menú añadido exitosamente!")
        cur_menu = models.Menu.objects.filter(menu_title='Test menu')
        self.assertTrue(cur_menu)

    def test_chef_user_cannot_publish_twice(self):
        """
        Tests that a chef client after having created a menu for the day, cannot create another one
        """
        self.client.login(username='chef_user', password='12345')
        self.client.post(reverse('new_menu'), {
            'menu_title': 'Test menu',
            'form-0-item_text': 'Menu 1',
            'form-0-id': '',
            'form-1-id': '',
            'form-1-item_text': 'Menu 2',
            'form-TOTAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000'
        })
        response = self.client.post(reverse('new_menu'), {
            'menu_title': 'Another menu',
            'form-0-item_text': 'Menu 1',
            'form-0-id': '',
            'form-1-id': '',
            'form-1-item_text': 'Menu 2',
            'form-TOTAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000'
        })
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[1]), '¡Ya se publicó el menú de hoy, no puede crear otro!')
        cur_menu = models.Menu.objects.filter(menu_title='Another menu')
        self.assertFalse(cur_menu)


class EditMenuViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(EditMenuViewTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='Dummy menu')
        models.MenuItem.objects.create(
            item_text='dummy_1',
            menu=dummy_menu
        )
        models.MenuItem.objects.create(
            item_text='dummy_2',
            menu=dummy_menu
        )
        chef_user = models.User.objects.create(username='chef_user')
        chef_user.set_password('12345')
        chef_user.is_chef = True
        chef_user.save()
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        cls.chef_user = chef_user
        cls.client_user = client_user
        cls.dummy_menu = dummy_menu

    def test_anonymous_user_redirect(self):
        """
        Tests that an anonymous user cannot edit a menu, instead it is redirected to the login
        page with an error message.
        """
        response = self.client.get(reverse(
            'edit_menu',
            kwargs={'unique_id': EditMenuViewTests.dummy_menu.unique_id}
        ))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Para continuar debe identificarse.")

    def test_client_user_redirect(self):
        """
        Tests that a client user cannot edit a menu, instead it is redirected to the login page with
        an error message.
        """
        self.client.login(username='client_user', password='12345')
        response = self.client.get(reverse(
            'edit_menu',
            kwargs={'unique_id': EditMenuViewTests.dummy_menu.unique_id}
        ))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Usted debe ser chef para acceder a esta página")

    def test_get_404_on_non_existent_menu(self):
        """
        Tests that a chef client that tries to edit a non existent menu gets a 404 HTTP error code.
        """
        invalid_uuid = '5bfa3016-ded3-424c-9140-5b0554d962a6'
        self.client.login(username='chef_user', password='12345')
        response = self.client.get(reverse(
            'edit_menu',
            kwargs={'unique_id': invalid_uuid}
        ))
        self.assertEquals(response.status_code, 404)

    def test_chef_can_edit_menu(self):
        """
        Tests that a chef client that tries to edit an existing menu, indeed, manages to modify
        the menu and it gets saved to the database.
        """
        self.client.login(username='chef_user', password='12345')
        response = self.client.post(
            reverse('edit_menu', kwargs={'unique_id': EditMenuViewTests.dummy_menu.unique_id}),
            {
                'menu_title': 'Dummy menu edited',
                'form-0-item_text': 'Menu 1 edited',
                'form-0-id': '',
                'form-1-id': '',
                'form-2-id': '',
                'form-1-item_text': 'Menu 2 edited',
                'form-2-item_text': 'Menu 3 added',
                'form-TOTAL_FORMS': '3',
                'form-MIN_NUM_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000'
            }
        )
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Menú actualizado exitosamente!")
        cur_menu = models.Menu.objects.filter(menu_title='Dummy menu edited')
        self.assertTrue(cur_menu)

class CreateOrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(CreateOrderViewTests, cls).setUpClass()
        dummy_menu = models.Menu.objects.create(menu_title='Dummy menu')
        models.MenuItem.objects.create(
            item_text='dummy_1',
            menu=dummy_menu
        )
        models.MenuItem.objects.create(
            item_text='dummy_2',
            menu=dummy_menu
        )
        chef_user = models.User.objects.create(username='chef_user')
        chef_user.set_password('12345')
        chef_user.is_chef = True
        chef_user.save()
        client_user = models.User.objects.create(username='client_user')
        client_user.set_password('12345')
        client_user.is_chef = False
        client_user.save()
        cls.chef_user = chef_user
        cls.client_user = client_user
        cls.dummy_menu = dummy_menu

    def test_anonymous_user_order_redirect(self):
        """
        Tests that an anonymous user cannot make an order, instead it is redirected to the login
        page with an error message.
        """
        response = self.client.get(reverse(
            'new_order',
            kwargs={'unique_id': CreateOrderViewTests.dummy_menu.unique_id}
        ))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Para continuar debe identificarse.")

    def test_chef_user_order_redirect(self):
        """
        Tests that a chef user cannot make an order, instead it is redirected to the login page
        with an error message.
        """
        self.client.login(username='chef_user', password='12345')
        response = self.client.get(reverse(
            'new_order',
            kwargs={'unique_id': CreateOrderViewTests.dummy_menu.unique_id}
        ))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), "Usted debe ser cliente para acceder a esta página")

    def test_redirect_on_invalid_menu(self):
        """
        Tests that trying to access a non existent menu results in a redirection to home with an
        error message.
        """
        self.client.login(username='client_user', password='12345')
        invalid_uuid = '5bfa3016-ded3-424c-9140-5b0554d962a6'
        response = self.client.get(reverse(
            'new_order',
            kwargs={'unique_id': invalid_uuid}
        ))
        self.assertEquals(response.status_code, 302)
        messages = get_messages_as_list(response)
        self.assertEquals(str(messages[0]), 'El menú al que trató de acceder no existe!')

