from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import F
from django.db import transaction
from django.core.mail import send_mail
import threading

from BlogCN import settings
from CentBLG import codehelper
from CentBLG.formhelper import UserForm
from CentBLG.models import UserInfo
from django.contrib import auth
from CentBLG import models
from CentBLG.sqlhelpers import SqlHelper

import json

def login(request):
	""" 用户登录
	:param request:
	:return:
	"""
	ret = {'status': False, 'msg': None, 'user': None}
	if request.method == 'POST':
		user = request.POST.get('user')
		password = request.POST.get('password')
		valid_code = request.POST.get('valid_code')
		print(request.session.get('valid_code'))
		if valid_code.upper() == request.session.get('valid_code').upper():
			user = auth.authenticate(username=user, password=password)
			if user:
				ret['status'] = True
				auth.login(request, user)        # request.user == current logined object.
				ret['user'] = user.username
				return JsonResponse(ret)
			else:
				ret['status'] = False
				ret['msg'] = '用户名或密码错误!'
				return JsonResponse(ret)
		else:
			ret['status'] = False
			ret['msg'] = '验证码错误'
			return JsonResponse(ret)
	else:
		return render(request, 'login.html', {})


def register(request):
	""" 用户注册
	:param request:
	:return:
	"""
	if request.is_ajax():
		form = UserForm(request.POST)
		ret = {'status': False, 'msg': None}
		
		if form.is_valid():
			ret['status'] = True
			user = form.cleaned_data.get('user')
			pswd = form.cleaned_data.get('pswd')
			email = form.cleaned_data.get('email')
			avatar_obj = request.FILES.get('avatar')
			if avatar_obj:
				UserInfo.objects.create_user(username=user, password=pswd, email=email, avater=avatar_obj)
			else:
				UserInfo.objects.create_user(username=user, password=pswd, email=email)
			return JsonResponse(ret)
		else:
			ret['msg'] = form.errors
			
			return JsonResponse(ret)
	else:
		form = UserForm()
		return render(request, 'register.html', {'form': form})


def index(request):
	""" 用户主页
	:param request:
	:return:
	"""
	article_list = models.Article.objects.all()
	
	
	
	
	return render(request, 'index.html', {'article_list': article_list})


def logout(request):
	""" 注销功能：等同于执行 request.session.flush()
	:param request:
	:return:
	"""
	auth.logout(request)
	return redirect('/login/')
	
	
	
def get_valid_img(request):
	"""
	工具箱 ： 用于返回验证码，同时将验证码存储在session中，用于后期的校验
	"""
	def session_put(official_code):
		request.session["valid_code"] = official_code
		
	data = codehelper.official_code_img_gen(session_put)
	return HttpResponse(data)


def get_classfication_style(username):
	user = UserInfo.objects.filter(username=username).first()
	blog = user.blog
	cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values()
	tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
	date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count('nid')).values_list('month', 'c')

	return {'blog': blog, 'cate_list':cate_list, 'tag_list':tag_list, 'date_list':date_list}


def home_site(request, username, **kwargs):
	""" 个人站点视图函数
	:param username:
	:param request:
	:return:
	"""
	user = UserInfo.objects.filter(username=username).first()
	if not user:
		return render(request, 'error.html')
	# 根据Username查询当前对应的博客站点
	blog = user.blog
	# 当前博客对应的所有文章，也可以: article_list = user.article_set.all()
	if not kwargs:
		article_list = models.Article.objects.filter(user=user)
	else:
		condition = kwargs.get('condition')
		param = kwargs.get('param')
		
		if condition == 'category':
			article_list = models.Article.objects.filter(user=user).filter(category__title=param)
		elif condition == 'tag':
			article_list = models.Article.objects.filter(user=user).filter(tags__title=param)
		else:
			year, month = param.split('-')
			article_list = models.Article.objects.filter(user=user).filter(create_time__year=year, create_time__month=month)

	
	# 查询当前站点的每一个分类名称以及对应的文章数量
	# ret = models.Category.objects.values("pk").annotate(c=Count('article__title')).values()
	cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values()
	
	# 查询当前站点的每一个标签名称以及对应的文章数量
	tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
	
	# 查询当前站点的每一个年月的名称以及对应的文章数量
	# ret = models.Article.objects.extra(select={'is_recent': "create_time > 2020-06-30"})
	
	date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count('nid')).values_list('month', 'c')
	# date_list = models.Article.objects.extra(select={'y_m_d_date': 'date_format(create_time, "%%Y-%%m-%%d")'}).values('title', 'y_m_d_date')
	
	return render(request, 'home_site.html', {
					  'username': username,
		              'blog': blog,
		              'article_list': article_list,
		              'cate_list': cate_list,
		              'tag_list': tag_list,
		              'date_list': date_list
	              })


def article_detail(request, username, article_id):
	user = UserInfo.objects.filter(username=username).first()
	blog = user.blog
	article_obj = models.Article.objects.filter(pk=article_id).first()
	comment_list = models.Comment.objects.filter(article_id=article_id)
	
	
	models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
	
	try:
		# print(models.ArticleUpDown.objects.filter(user_id=request.user.pk, article_id=article_id).first().is_up)
		is_posted = 1 if models.ArticleUpDown.objects.filter(user_id=request.user.pk, article_id=article_id).first() else 0
		is_support = 1 if models.ArticleUpDown.objects.filter(user_id=request.user.pk, article_id=article_id).first().is_up else 0
	except Exception as E:
		pass
	
	return render(request, 'article_detail.html', locals())



def digg(request):
	
	ret = {'status': None, 'msg': None}
	article_id = request.POST.get('article_id')
	is_up = json.loads(request.POST.get('is_up'))
	user_id = request.user.pk
	obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
	if obj:
		ret['status'] = False
		ret['msg'] = '每个用户只能评价一次'
		return JsonResponse(ret)
	else:
		ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
		if is_up:
			ret['status'] = True
			ret['msg'] = '谢谢你的支持'
			models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
		else:
			ret['status'] = True
			ret['msg'] = '再看看其他文章吧'
			models.Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
		return JsonResponse(ret)


def comment(request):
	ret = {'status': None, 'msg': None}
	
	main_comment = request.POST.get('main_comment')
	article_id = request.POST.get('article_id')
	pid = request.POST.get('pid')
	user_id = request.user.pk
	
	# 引入事务操作
	with transaction.atomic():
		comment_obj = models.Comment.objects.create(user_id=user_id, content=main_comment, article_id=article_id, parent_comment_id=pid)
		models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)
	
	ret['status'] = True
	ret['cre_time'] = comment_obj.create_time.strftime("%Y-%m-%d %X")
	ret['content'] = main_comment
	
	article_obj = models.Article.objects.filter(pk=article_id).first()
	
	sql_obj = SqlHelper()
	email = sql_obj.get_one('select email from CentDB.CentBLG_userinfo where nid=%s', [article_obj.user_id, ])
	sql_obj.close()
	print(email)
	
	# 发送邮件
	# send_mail(
	# 	subject="「Cent」您的文章《%s》新增了一条评论内容" % article_obj.title,
	# 	message=main_comment,
	# 	from_email=settings.DEFAULT_FROM_EMAIL,
	# 	recipient_list=['dandelionatcha@163.com']
	# )
	
	threading.Thread(target=send_mail, args=(
		"【Cent】您的文章《%s》新增了一条评论内容" % article_obj.title,
		main_comment,
		settings.DEFAULT_FROM_EMAIL,
		[email['email'], ]
	)).start()
	

	return JsonResponse(ret)