"""
    UnitTest File of Django Project
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.test import Client
User = get_user_model()

import datetime
import json


class CentBLGTest(TestCase):
    def setUp(self) -> None:
        """
            Create Users to be used to UNITTEST
        :return:  None
        """

        pass


    def test_login_uname_pswd(self):
        client = Client()
        resp = client.post('/login/', {'user': 'Dandelion', 'password': 'smile'})
        info = json.loads(resp.content.decode())
        self.assertEqual(info['status'], True)
        pass


    def test_login_error(self):
        client = Client()
        resp = client.post('/login/', {'user': 'Dad', 'password': 'smile'})
        info = json.loads(resp.content.decode())
        self.assertEqual(info['status'], False)
        pass
