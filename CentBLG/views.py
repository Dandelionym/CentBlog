from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from CentBLG.formhelper import UserForm
from CentBLG.models import UserInfo

def login(request):
	ret = {'status': False, 'msg': None, 'user': None}
	if request.method == 'POST':
		user = request.POST.get('user')
		password = request.POST.get('password')
		valid_code = request.POST.get('valid_code')
		
		if valid_code.upper() == request.session.get('valid_code').upper():
			ret['status'] = True
			if user == 'Admin' and password == 'smile':
				return JsonResponse(ret)
			else:
				ret['status'] = False
				ret['msg'] = '密码错误!'
				return JsonResponse(ret)
		else:
			ret['status'] = False
			ret['msg'] = '验证码错误'
			return JsonResponse(ret)
	else:
		return render(request, 'login.html', {})


def register(request):
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
	
	
	
	return render(request, 'index.html', {})





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
	BHB_font = ImageFont.truetype('static/centBlog/fonts/Arial Black.ttf', size=35)
	
	official_code = ""
	
	for i in range(4):
		random_num = str(random.randint(0, 9))
		random_lower_alpha = chr(random.randint(95, 122))
		random_upper_alpha = chr(random.randint(65, 90))
		random_char = random.choice([random_num, random_upper_alpha, random_lower_alpha])
		draw.text((5 + i * 53, 5), random_char, get_random_color(), font=BHB_font)
		official_code += str(random_char)
	
	request.session["valid_code"] = official_code
	
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
