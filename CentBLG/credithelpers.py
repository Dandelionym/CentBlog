from CentBLG import models
from BlogCN import settings
from django.db.models import F
from CentBLG import sqlhelpers


def user_level_up(request_v):
	""" 【Class  ->  Tools】 用户积分满足后等级的更新：
	:param request_v: 传入HTTP请求 Request 以获取当前登录的用户对象，通过该user对象获得name
	:return:
	"""
	user_looker = models.UserInfo.objects.filter(nid=request_v.user.pk).first()
	user_ps_credit = user_looker.ps_credit
	if user_ps_credit >= settings.LEVEL_UP_CREDIT:
		# target_user = models.UserInfo.objects.filter(username=request_v.user.username).first()
		models.UserInfo.objects.filter(username=request_v.user.username).update(level=F("level") + 1)
		models.UserInfo.objects.filter(username=request_v.user.username).update(ps_credit=user_ps_credit-settings.LEVEL_UP_CREDIT)


def credit_add_controller(request_v, add_amount):
	models.UserInfo.objects.filter(pk=request_v.user.pk).update(ps_credit=F("ps_credit") + add_amount)


def login_time_check(nid_new):
	import datetime
	sql = sqlhelpers.SqlHelper()
	ret = sql.get_one('select last_login from CentBLG_userinfo where nid=%s', [nid_new])
	sql.close()
	now = datetime.datetime.now()
	time_tuple = (now.year, now.month, now.day)
	
	return (ret['last_login'].year, ret['last_login'].month, ret['last_login'].day) == time_tuple
