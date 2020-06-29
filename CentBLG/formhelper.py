from django import forms
from django.forms import widgets
from CentBLG.models import UserInfo
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

class UserForm(forms.Form):
	user = forms.CharField(max_length=32,
	                       error_messages={'required': "输入的用户名不能为空！"},
	                       widget=widgets.TextInput(
		                       attrs={'class': 'form-control expend-width'}
	                       ),
	                       label='用户名')
	pswd = forms.CharField(max_length=32,
	                       error_messages={'required': "输入的密码不能为空！"},
	                       widget=widgets.PasswordInput(
		                       attrs={'class': 'form-control expend-width'}),
	                       label='密码')
	reps = forms.CharField(max_length=32,
	                       error_messages={'required': "请再次输入密码！"},
	                       widget=widgets.PasswordInput(
		                       attrs={'class': 'form-control expend-width'}),
	                       label='确认密码')
	email = forms.EmailField(max_length=32,
	                         error_messages={'required': "输入的邮箱不能为空！"},
	                         widget=widgets.EmailInput(
		                         attrs={'class': 'form-control expend-width'}),
	                         label='邮箱')
	phone = forms.CharField(max_length=11,
	                        error_messages={'required': "输入的手机号不能为空！"},
	                        widget=widgets.TextInput(
		                        attrs={'class': 'form-control expend-width'}),
	                        label='手机')

	def clean_user(self):
		user = self.cleaned_data.get('user')
		user_status = UserInfo.objects.filter(username=user).first()
		if not user_status:
			return user
		else:
			raise ValidationError("该用户已注册！")
	
	
	def clean(self):
		pswd = self.cleaned_data.get('pswd')
		reps = self.cleaned_data.get('reps')
		if pswd and reps:
			if reps == pswd:
				return self.cleaned_data
			else:
				raise ValidationError('两次密码不一致！')
		else:
			return self.changed_data