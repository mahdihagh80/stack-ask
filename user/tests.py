from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class UserCrudTestCase(APITestCase):
    def setUp(self):
        user_information = {'first_name': 'first_name',
                            'last_name': 'last_name',
                            'username': 'user1',
                            'email': 'email@email.com',
                            'password': 'password'}
        self.user = User.objects.create_user(**user_information)
        self.token = Token.objects.create(user=self.user)

    def test_user_creation(self):
        data = {'first_name': 'first_name',
                'last_name': 'last_name',
                'username': 'username',
                'email': 'email@email.com',
                'password': 'password@123456',
                'password2': 'password@123456'}
        response = self.client.post(reverse('user:user'), data=data)
        expected_response = {'email': 'email@email.com',
                             'username': 'username',
                             'first_name': 'first_name',
                             'last_name': 'last_name'}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_response)

        try:
            data.pop('password')
            data.pop('password2')
            user_dict = User.objects.values(*data.keys()).get(username=data.get('username'))
            self.assertEqual(user_dict, data)
        except User.DoesNotExist:
            self.fail('user does not create in database')

    def test_duplicate_user_creation(self):
        data = {'first_name': 'first_name',
                'last_name': 'last_name',
                'username': 'user1',
                'email': 'email@email.com',
                'password': 'password@123456',
                'password2': 'password@123456'}
        response = self.client.post(reverse('user:user'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user(self):
        data = {'first_name': 'new_first_name',
                'last_name': 'new_last_name',
                'username': 'new_user1',
                'email': 'new_email@email.com',
                'password': 'new_password',
                'password2': 'new_password'}

        response = self.client.put(reverse('user:user'), data=data, headers={'AUTHORIZATION': f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data.pop('password')
        data.pop('password2')
        self.assertEqual(response.data, data)

        user_dict = User.objects.values(*data.keys()).get(username=data.get('username'))
        self.assertEqual(user_dict, data)

        data = {'username': 'new_new_user1'}
        response = self.client.patch(reverse('user:user'), data=data, headers={'AUTHORIZATION': f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], data['username'])

    def test_change_password(self):
        data = {'password': 'new_password',
                'password2': 'new_password'}
        response = self.client.patch(reverse('user:user'), data=data, headers={'AUTHORIZATION': f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        credentials = {'username': self.user.username,
                       'password': data['password']}
        response = self.client.post(reverse('user:login'), data=credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        response = self.client.delete(reverse('user:user'), headers={'AUTHORIZATION': f'Token {self.token}'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = User.objects.filter(pk=self.user.pk).count()
        self.assertEqual(count, 0)


class LoginLogoutTestCase(APITestCase):
    def setUp(self):
        self.user_information = {'first_name': 'first_name',
                                 'last_name': 'last_name',
                                 'username': 'user1',
                                 'email': 'email@email.com',
                                 'password': 'password'}
        self.user = User.objects.create_user(**self.user_information)

    def test_login(self):
        data = {'username': 'user1', 'password': 'password'}
        response = self.client.post(reverse('user:login'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('token'))

        token = response.data.get('token')
        response = self.client.get(reverse('user:user'), headers={'AUTHORIZATION': f'Token {token}'})
        self.user_information.pop('password')
        self.assertEqual(self.user_information, response.data)

    def test_logout(self):
        token = Token(user=self.user)
        token.save()
        response = self.client.post(reverse('user:logout'), headers={'AUTHORIZATION': f'Token {token.key}'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user_token_count = Token.objects.filter(user=self.user).count()
        self.assertEqual(user_token_count, 0)
