from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from CentBLG import models
from CentBLG.models import UserInfo

register = template.Library()


@register.inclusion_tag('components/classfication.html')
def get_classfication_style(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values()
    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count('nid')).values_list('month', 'c')
    username = username
    avatar = user.avatar
    return locals()


@register.inclusion_tag('components/navbar.html')
def get_navbar_header(username):
    user = UserInfo.objects.filter(username=username).first()
    return locals()


@register.inclusion_tag('components/simple_table.html')
def self_change_info(username):
    user = UserInfo.objects.filter(username=username).first()

    return locals()


@register.inclusion_tag('components/change_box.html')
def change_box(username):
    user = UserInfo.objects.filter(username=username).first()

    return locals()


@register.inclusion_tag('components/functional_table.html')
def functional_table(username):
    user = UserInfo.objects.filter(username=username).first()

    return locals()


def divider(module_name):
    return locals()
