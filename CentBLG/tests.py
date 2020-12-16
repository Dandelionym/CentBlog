"""
    UnitTest File of Django Project
"""
from django.test import TestCase
from CentBLG.models import UserInfo
from django.contrib.auth.models import User

import datetime

get_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
