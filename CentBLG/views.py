from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import F
from django.db import transaction
from django.core.mail import send_mail

from bs4 import BeautifulSoup
import threading
import datetime
import json
import os

from BlogCN import settings
from CentBLG import codehelper
from CentBLG.formhelper import UserForm
from CentBLG.models import UserInfo
from django.contrib import auth
from CentBLG import models
from CentBLG import credithelpers
from CentBLG.sqlhelpers import SqlHelper


class DateEnconding(json.JSONEncoder):
    """ 定义一个日期转化的类，因为日期不能直接序列化，需要指定格式 """
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')


def login(request):
    """ 实现用户登录的功能， """
    ret = {'status': False, 'msg': None, 'user': None}
    if request.method == 'POST':
        user = request.POST.get('user')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')

        if valid_code.upper() == request.session.get('valid_code').upper():  # 验证码校验过程，通过Session筛选用户个人的验证码
            user = auth.authenticate(username=user, password=password)  # User Model定义的时候设定了 __str__(): return username
            if user:
                ret['status'] = True
                auth.login(request, user)  # request.user == current logined object.
                ret['user'] = user.username
                if credithelpers.login_time_check(request.user.pk):
                    models.UserInfo.objects.filter(pk=request.user.pk).update(ps_credit=F("ps_credit") + settings.CREDIT_ADDED_OF_LOGINED)
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
    """ 用户注册	"""
    if request.is_ajax():  # Ajax 完整性校验、准确性校验
        form = UserForm(request.POST)
        ret = {'status': False, 'msg': None}

        if form.is_valid():  # 根据数据库完成合法性校验
            ret['status'] = True
            user = form.cleaned_data.get('user')
            pswd = form.cleaned_data.get('pswd')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            if avatar_obj:
                UserInfo.objects.create_user(username=user, password=pswd, email=email, avatar=avatar_obj)
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
    """ 用户主页 """  # 1，0 版本时，index 为用户主页，2.0版本中代表Cent所有产业介绍
    user = request.user
    article_list_all = models.Article.objects.all()
    article_list = []
    count = 0
    for i in range(len(article_list_all)):
        if i == 5: break
        article_list.append(article_list_all[i])
    sql_helper = SqlHelper()
    result = sql_helper.get_list(  # 精品文章榜单
        "select username, CentBLG_article.nid, title, up_count  from CentBLG_article, CentBLG_userinfo where CentBLG_article.user_id=CentBLG_userinfo.nid order by up_count desc limit 4",
        [])

    sql_helper.close()
    return render(request, 'index.html', locals())


def logout(request):
    """ 注销功能：等同于执行 request.session.flush() """
    auth.logout(request)
    return redirect('/login/')


def get_valid_img(request):
    """  工具箱 ： 用于返回验证码，同时将验证码存储在session中，用于后期的校验  """

    def session_put(official_code):
        request.session["valid_code"] = official_code

    data = codehelper.official_code_img_gen(session_put)
    return HttpResponse(data)


def home_site(request, username, **kwargs):
    """ 个人站点视图函数 """
    user = UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request, 'error.html')

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
    cate_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values()
    # cate_list = models.Category.objects.values("pk").annotate(c=Count('article__title')).values()
    # 查询当前站点的每一个标签名称以及对应的文章数量
    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    # 查询当前站点的每一个年月的名称以及对应的文章数量
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
    user_author = UserInfo.objects.filter(username=username).first()  # 文章作者对象
    user_logined = UserInfo.objects.filter(username=request.user.username).first()  # 登录用户对象
    blog = user_author.blog
    article_obj = models.Article.objects.filter(pk=article_id).first()
    auth_avatar = UserInfo.objects.filter(nid=article_obj.user_id).first().avatar
    comment_list = models.Comment.objects.filter(article_id=article_id)

    # 对文本添加浏览量
    # 更新算法：获取文章id值锁定文章的位置，调用增值函数对用户的积分进行数值控制，校验方式在credithelpers.user_level_up(request)中
    if not request.COOKIES.get('viewed-' + article_id):  # 截取文章id，该id值通过渲染绑定在标签的自定属性中
        if not user_author.nid == user_logined.nid:
            models.Article.objects.filter(pk=article_id).update(views=F("views") + 1)
            credithelpers.credit_add_controller(request, settings.CREDIT_ADDED_OF_LOOKUP_ARTICLES)

    credithelpers.user_level_up(request)  # 用户积分满足后等级的更新
    models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    try:
        is_posted = 1 if models.ArticleUpDown.objects.filter(user_id=request.user.pk, article_id=article_id).first() else 0
        is_support = 1 if models.ArticleUpDown.objects.filter(user_id=request.user.pk, article_id=article_id).first().is_up else 0
    except Exception as E:
        pass
    return render(request, 'article_detail.html', locals())


def viewed(request):
    if request.COOKIES.get('viewed'):
        return HttpResponse()
    else:
        article_id = request.POST.get('article_id')
        cookier = HttpResponse()
        cookier.set_cookie(key='viewed-' + article_id, value=True, max_age=settings.ARTICEL_VIEWED_COOKIE_AGE)
        return cookier


def digg(request):
    """ 点赞操作 """
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
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        if is_up:
            ret['status'] = True
            ret['msg'] = '谢谢你的支持'
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            ret['status'] = True
            ret['msg'] = '再看看其他文章吧'
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
        return JsonResponse(ret)


def comment(request):
    """ 评论之后讲发送邮件通知对方 """
    ret = {'status': None, 'msg': None}
    main_comment = request.POST.get('main_comment')
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    user_id = request.user.pk

    with transaction.atomic():  # 事务层
        comment_obj = models.Comment.objects.create(user_id=user_id, content=main_comment, article_id=article_id, parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    # sql_helper = SqlHelper()
    # sql_helper.modify("update CentBLG_userinfo set today_comments = today_comments + 1 where nid = %s", [user_id, ])
    # sql_helper.close()
    # 用户积分增加
    current_user = models.UserInfo.objects.filter(nid=request.user.pk).first()
    if current_user.today_comments <= settings.MAX_COMMENTS_ONE_DAY:
        credithelpers.credit_add_controller(request, settings.CREDIT_ADDED_OF_MAKE_COMMENT)
        models.UserInfo.objects.filter(nid=request.user.pk).update(today_comments=F("today_comments") + 1)
        credithelpers.user_level_up(request)  # 用户积分满足后等级的更新

    ret['status'] = True
    ret['cre_time'] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    ret['content'] = main_comment

    article_obj = models.Article.objects.filter(pk=article_id).first()

    sql_obj = SqlHelper()
    email = sql_obj.get_one("select email from CentDB2.CentBLG_userinfo where nid=%s", [article_obj.user_id, ])
    sql_obj.close()
    new_comment = "您的文章《%s》新增了一条评论内容，快去看看吧！" % article_obj.title,
    try:
        threading.Thread(target=send_mail, args=(
            "来自 CentBlog 的消息",
            new_comment,
            settings.DEFAULT_FROM_EMAIL,
            [email['email'], ]
        )).start()
    except Exception as e:
        print(str(e))
        ret['msg'] = "Something wrong with status 502：" + str(e)
    return JsonResponse(ret)


def backend(request):
    user = request.user
    username = user.username
    article_list = models.Article.objects.filter(user_id=user.pk)
    has_blog = models.UserInfo.objects.filter(nid=user.pk).first().blog_id
    return render(request, 'backend.html', locals())


def get_readamt_data(request):
    """ Ajax 操作 ： 获取阅读数量 """
    sql = SqlHelper()
    result_list = sql.get_list("select * from CentBLG_day_sumup where uid=%s", [int(request.user.pk), ])
    sql.close()
    return HttpResponse(json.dumps(result_list, cls=DateEnconding))


def get_heatmap_data(request):
    """ Ajax 操作 ： 获取阅读数量 """
    sql = SqlHelper()
    result_list = sql.get_list("select * from CentBLG_day_sumup where uid=%s", [int(request.user.pk), ])
    sql.close()
    return HttpResponse(json.dumps(result_list, cls=DateEnconding))


def upload(request):
    """ 发表文章的图片上传 """
    import random
    img = request.FILES.get('file')
    img_append = random.random().__str__()[2:]
    path = os.path.join(settings.MEDIA_ROOT, "articles", img_append + img.name)
    with open(path, "wb") as f:
        for line in img:
            f.write(line)
    response = {
        "success": True,
        "file_path": "/media/articles/%s" % (img_append + img.name),
    }
    return HttpResponse(json.dumps(response))


def modify(request):
    """ 文章的修改 """
    mode = request.POST.get('mode')
    ret = {'status': True, 'msg': None}
    if mode == 'query':
        article_id = request.POST.get('article_id')
        article_obj = models.Article.objects.filter(pk=article_id).first()
        return JsonResponse({'title': article_obj.title, 'content': article_obj.content})
    elif mode == 'modify':
        try:
            article_id = request.POST.get('article_id')
            article_title = request.POST.get('article_title')
            article_content = request.POST.get('article_content')
            models.Article.objects.filter(pk=article_id).update(title=article_title, content=article_content, desc=article_content[:250] + "...")
        except Exception as e:
            ret['status'] = True
            ret['msg'] = str(e)
        return JsonResponse(ret)
    elif mode == 'release':
        try:
            article_title = request.POST.get('article_title')
            article_content = request.POST.get('article_content')
            soup = BeautifulSoup(article_content, 'html.parser')
            desc = soup.text[:150] + "..."
            models.Article.objects.create(title=article_title, desc=desc, content=article_content, user_id=request.user.pk, status=1)
            sql_helper = SqlHelper()
            sql_helper.modify("update CentBlG_userinfo set today_release = today_release + 1 where nid=%s", [request.user.pk, ])
        except Exception as e:
            ret['status'] = True
            ret['msg'] = str(e)
        return JsonResponse(ret)
    elif mode == 'saved':
        try:
            article_id = request.POST.get('article_id')
            models.Article.objects.filter(pk=article_id).update(status=1)
        except Exception as e:
            ret['status'] = True
            ret['msg'] = str(e)
        return JsonResponse(ret)
    else:
        try:
            article_id = request.POST.get('article_id')
            models.Article.objects.filter(nid=article_id).delete()
        except Exception as e:
            ret['status'] = True
            ret['msg'] = str(e)
        return JsonResponse(ret)


def personal_info(request):
    """ 查看个人信息，如果没有博客，则自动跳转 """
    try:
        user = request.user
        blog = models.Blog.objects.filter(nid=user.blog_id).first()
        if blog:
            has_blog = True
            return render(request, 'personal_info.html', locals())
        else:
            has_blog = False
            message = "You don't have a blog yet. Would you like to create it now?"
            return render(request, 'create_blog.html', locals())
    except Exception as e:
        print(str(e))


def create_blog(request):
    """ 创建博客 """
    if request.is_ajax():
        user = request.user.pk
        site_title = request.POST.get('site_title')
        site_name = request.POST.get('site_name')
        site_theme = request.POST.get('site_theme')
        site_desc = request.POST.get('site_desc')
        nid = models.Blog.objects.create(title=site_title, site_name=site_name, theme=site_theme, desc=site_desc)
        models.UserInfo.objects.filter(pk=user).update(blog_id=nid)
        return HttpResponse("ok")
    else:
        has_blog = models.Blog.objects.filter(nid=request.user.blog_id).first()
        return render(request, 'create_blog.html', locals())


def public(request):
    return render(request, 'public.html', locals())
