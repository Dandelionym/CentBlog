from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from CentBLG import models
from CentBLG.models import UserInfo


register = template.Library()


@register.inclusion_tag('classfication.html')
def get_classfication_style(username):
	user = UserInfo.objects.filter(username=username).first()
	blog = user.blog
	cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values()
	tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
	date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count('nid')).values_list('month', 'c')

	return {'blog': blog,
	        'username':username,
	        'cate_list':cate_list,
	        'tag_list':tag_list,
	        'date_list':date_list,
	        'avatar': user.avatar,
	        'user':user}
