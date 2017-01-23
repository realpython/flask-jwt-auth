# project/server/tests/property_tests.py

import unittest
import json

# from project.server import db
# from project.server.models import User, BlacklistToken
from project.tests.base import BaseTestCase
from hypothesis import given, assume, strategies as st

# data structures for testing
user_data = st.fixed_dictionaries({
    'email': st.text(),
    'password': st.text(min_size=6)
})


class PropertyBasedTestAuthBlueprint(BaseTestCase):
    """ Property Based testing for existing test suite """

    @given(user_data)
    def test_user_registration(self, data):
        """
        Property Based testing user registration
        :param data: user_data dict
        :return: bool
        """
        # assuming email and password exists
        assume(data['email'])
        assume(data['password'])

        response = self.client.post(
            '/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        if response.status_code == 202:
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Email or Password format is not correct.')
            self.assertTrue(response.content_type == 'application/json')
        if response.status_code == 201:
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')

    @given(user_data)
    def test_registered_user_login(self, data):
        """
        Property Based testing for login of registered-user
        :param data: user_data dict
        :return: bool
        """
        with self.client:
            # user registration
            resp_register = self.client.post(
                '/auth/register',
                data=json.dumps(data),
                content_type='application/json'
            )
            if resp_register.status_code == 202:
                data_register = json.loads(resp_register.data.decode())
                self.assertTrue(data_register['status'] == 'fail')
                self.assertTrue(data_register['message'] == 'Email or Password format is not correct.')
                self.assertTrue(resp_register.content_type == 'application/json')
            if resp_register.status_code == 201:
                data_register = json.loads(resp_register.data.decode())
                self.assertTrue(data_register['status'] == 'success')
                self.assertTrue(data_register['message'] == 'Successfully registered.')
                self.assertTrue(data_register['auth_token'])
                self.assertTrue(resp_register.content_type == 'application/json')

            # registered user login
            response = self.client.post(
                '/auth/login',
                data=json.dumps(data),
                content_type='application/json'
            )
            if response.status_code == 202:
                data = json.loads(response.data.decode())
                self.assertTrue(data['status'] == 'fail')
                self.assertTrue(data['message'] == 'Email or Password format is not correct.')
                self.assertTrue(response.content_type == 'application/json')
            if response.status_code == 200:
                data = json.loads(response.data.decode())
                self.assertTrue(data['status'] == 'success')
                self.assertTrue(data['message'] == 'Successfully logged in.')
                self.assertTrue(data['auth_token'])
                self.assertTrue(response.content_type == 'application/json')

    @given(user_data)
    def test_user_status(self, data):
        """
        Test for user status
        :param data: user_data dict
        :return: bool
        """
        with self.client:
            resp_register = self.client.post(
                '/auth/register',
                data=json.dumps(data),
                content_type='application/json'
            )
            if resp_register.status_code == 201:
                response = self.client.get(
                    '/auth/status',
                    headers=dict(
                        Authorization='Bearer ' + json.loads(
                            resp_register.data.decode()
                        )['auth_token']
                    )
                )
                data = json.loads(response.data.decode())
                self.assertTrue(data['status'] == 'success')
                self.assertTrue(data['data'] is not None)
                self.assertTrue(data['data']['email'] == 'joe@gmail.com')
                self.assertTrue(data['data']['admin'] is 'true' or 'false')
                self.assertEqual(response.status_code, 200)

    @given(user_data)
    def test_valid_logout(self, data):
        """
        Test for logout before token expires
        :param data: user_data dict
        :return: bool
        """
        with self.client:
            # user registration
            resp_register = self.client.post(
                '/auth/register',
                data=json.dumps(data),
                content_type='application/json',
            )
            if resp_register.status_code == 201:
                data_register = json.loads(resp_register.data.decode())
                self.assertTrue(data_register['status'] == 'success')
                self.assertTrue(
                    data_register['message'] == 'Successfully registered.')
                self.assertTrue(data_register['auth_token'])
                self.assertTrue(resp_register.content_type == 'application/json')
                # user login
                resp_login = self.client.post(
                    '/auth/login',
                    data=json.dumps(dict(
                        email='joe@gmail.com',
                        password='123456'
                    )),
                    content_type='application/json'
                )

                if resp_login.status_code == 200:
                    data_login = json.loads(resp_login.data.decode())
                    self.assertTrue(data_login['status'] == 'success')
                    self.assertTrue(data_login['message'] == 'Successfully logged in.')
                    self.assertTrue(data_login['auth_token'])
                    self.assertTrue(resp_login.content_type == 'application/json')

                    # valid token logout
                    response = self.client.post(
                        '/auth/logout',
                        headers=dict(
                            Authorization='Bearer ' + json.loads(
                                resp_login.data.decode()
                            )['auth_token']
                        )
                    )
                    data = json.loads(response.data.decode())
                    self.assertTrue(data['status'] == 'success')
                    self.assertTrue(data['message'] == 'Successfully logged out.')
                    self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
