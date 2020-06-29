from django.test import TestCase
from CentBLG.sqlhelpers import SqlHelper

def sqlTest():
	sql = SqlHelper()
	ret = sql.get_list('select * from CentBLG_userinfo', [])
	sql.close()
	for i in ret:
		print(i['username'])

sqlTest()