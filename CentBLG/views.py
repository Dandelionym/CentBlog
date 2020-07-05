from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from CentBLG.formhelper import UserForm
from CentBLG.models import UserInfo
from django.contrib import auth
from CentBLG import models

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
	from PIL import Image, ImageDraw, ImageFont
	from io import BytesIO
	import random
	
	width = 200
	height = 45
	
	def get_random_color():
		return random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)
	
	img = Image.new("RGBA", (width, height), color=(255, 255, 255))
	draw = ImageDraw.Draw(img)
	BHB_font = ImageFont.truetype('static/centBlog/fonts/Arial Black.ttf', size=30)
	
	official_code = ""
	
	for i in range(4):
		random_num = str(random.randint(0, 9))
		random_lower_alpha = chr(random.randint(95, 122))
		random_upper_alpha = chr(random.randint(65, 90))
		random_char = random.choice([random_num, random_upper_alpha, random_lower_alpha])
		draw.text((5 + i * 53, 5), random_char, get_random_color(), font=BHB_font)
		official_code += str(random_char)
	
	request.session["valid_code"] = official_code
	print(request.session["valid_code"])
	
	
	for i in range(25):
		x1 = random.randint(0, width)
		x2 = random.randint(0, width)
		y1 = random.randint(0, height)
		y2 = random.randint(0, height)
		draw.line((x1, y1, x2, y2), fill=get_random_color())
	
	for i in range(25):
		draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
		x = random.randint(0, width)
		y = random.randint(0, height)
		draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
	
	f = BytesIO()
	img.save(f, "png")
	data = f.getvalue()
	
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
	
	return render(request, 'article_detail.html', locals())



def digg(request):
	import json
	
	print(request.POST)
	article_id = request.POST.get('article_id')
	is_up = json.loads(request.POST.get('is_up'))
	user_id = request.user.pk
	
	ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
	
	print(ard)
	
	
	return HttpResponse('ok')


