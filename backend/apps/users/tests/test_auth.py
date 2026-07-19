from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthLoginTests(APITestCase):
    def setUp(self):
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            email='testuser@finmark.ai',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
        )

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'email': 'testuser@finmark.ai',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_password(self):
        response = self.client.post(self.login_url, {
            'email': 'testuser@finmark.ai',
            'password': 'WrongPassword!',
        })
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'email': 'nobody@finmark.ai',
            'password': 'AnyPass123!',
        })
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_login_inactive_user(self):
        inactive_user = User.objects.create_user(
            email='inactive@finmark.ai',
            password='TestPass123!',
            first_name='Inactive',
            last_name='User',
            is_active=False,
        )
        response = self.client.post(self.login_url, {
            'email': 'inactive@finmark.ai',
            'password': 'TestPass123!',
        })
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])


class AuthLogoutTests(APITestCase):
    def setUp(self):
        self.login_url = '/api/v1/auth/login/'
        self.logout_url = '/api/v1/auth/logout/'
        self.user = User.objects.create_user(
            email='logoutuser@finmark.ai',
            password='TestPass123!',
            first_name='Logout',
            last_name='User',
        )

    def test_logout(self):
        login_response = self.client.post(self.login_url, {
            'email': 'logoutuser@finmark.ai',
            'password': 'TestPass123!',
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url, {
            'refresh': refresh_token,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
