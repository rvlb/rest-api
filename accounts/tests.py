import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

User = get_user_model()

class AccountTestCase(APITestCase):    
    def test_user_creation(self):
        '''Ensure we can create a new user via API'''
        response = self.client.post(
            '/users/', 
            json.dumps(
                {'username': 'test_username', 'email': 'test@username.com', 'password': 'test123'}
            ), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        '''Ensure we can't create another user with the same username'''
        response = self.client.post(
            '/users/', 
            json.dumps(
                {'username': 'test_username', 'email': 'test2@username.com', 'password': 'test1234'}
            ), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_can_authenticate(self):
        '''Ensure we can authenticate an existing user'''
        user = User.objects.create_user('test_username', 'test@username.com', 'test123')
        response = self.client.post(
            '/get_auth_token/', 
            json.dumps({'username': 'test_username', 'password': 'test123'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('token'), Token.objects.get_or_create(user=user)[0].key)

        '''Ensure we can't authenticate with invalid credentials'''
        response = self.client.post(
            '/get_auth_token/', 
            json.dumps({'username': 'dumbass', 'password': 'abcd123'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_retrieval(self):
        '''Ensure an user can retrieve itself'''
        user = User.objects.create_user('test_username', 'test@username.com', 'test123')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(Token.objects.get_or_create(user=user)[0].key)
        )
        response = self.client.get('/users/{}/'.format(user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        '''Ensure an user can't retrieve another user'''
        another = User.objects.create_user('another_user', 'another@user.com', 'test123')
        response = self.client.get('/users/{}/'.format(another.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        '''Ensure a superuser can retrieve itself and any existing user'''
        admin = User.objects.create_superuser('admin', 'admin@admin.com', 'test123')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(Token.objects.get_or_create(user=admin)[0].key)
        )
        response = self.client.get('/users/{}/'.format(user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/users/{}/'.format(user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/users/{}/'.format(admin.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        '''Ensure a not-existing user can't be retrieved even by a superuser'''
        response = self.client.get('/users/{}/'.format(99))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_password_change(self):
        '''Ensure an user can change it's password'''
        user = User.objects.create_user('test_username', 'test@username.com', 'test123')
        old_token = Token.objects.get_or_create(user=user)[0].key
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(old_token)
        )
        response = self.client.post(
            '/users/{}/change_password/'.format(user.id),
            json.dumps({'password': 'picapau@#'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        '''Ensure user's token has changed and it was returned in response'''
        new_token = Token.objects.get_or_create(user=user)[0].key
        self.assertNotEqual(new_token, old_token)
        self.assertEqual(response.data.get('token'), new_token)

        '''Ensure old token is invalid'''
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(old_token)
        )
        response = self.client.post(
            '/users/{}/change_password/'.format(user.id),
            json.dumps({'password': 'popcorn00'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        '''Ensure an user can't change another's password'''
        another = User.objects.create_user('dumbass', 'dumb@ass.com', 'test123')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(new_token)
        )
        response = self.client.post(
            '/users/{}/change_password/'.format(another.id),
            json.dumps({'password': 'abcd123'}), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        