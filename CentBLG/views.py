from CentBLG.views_core.functional_view import *


"""
    登录模块
"""
def login(request):
    """
        实现用户登录的功能，
        支持：POST、GET

    """
    ret = {'status': False, 'msg': None, 'user': None}
    if request.method == 'POST':
        user = request.POST.get('user')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')
        if valid_code.upper() == request.session.get('valid_code').upper():  # 验证码校验过程，通过Session筛选用户个人的验证码
            user = auth.authenticate(username=user, password=password)       # User Model定义的时候设定了 __str__(): return username
            if user:
                ret['status'] = True
                auth.login(request, user)                                    # request.user == current logined object.
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


"""
    注册模块
"""
def register(request):
    """
        输入：用户名、密码、邮箱、手机号、头像（可选）；
        处理：
            1、Form校验并获取对象
            2、是否上传头像分支（否则默认）
    """
    if request.is_ajax():  # Ajax 完整性校验、准确性校验
        form = UserForm(request.POST)
        ret = {'status': False, 'msg': None}

        if form.is_valid():  # 根据数据库完成合法性校验
            ret['status'] = True
            user = form.cleaned_data.get('user')
            pswd = form.cleaned_data.get('pswd')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
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
        return render(request, 'register.html', locals())


"""
    主页模块 —— 此模块的文章评论显示暂不渲染出，已迁移至【博客】
"""
def index(request):
    user = request.user
    article_list_all = models.Article.objects.all()
    article_list = []
    count = 0
    for i in range(len(article_list_all)):
        if i == 5: break
        article_list.append(article_list_all[i])
    sql_helper = SqlHelper()
    result = sql_helper.get_list(  # 精品文章榜单
        "select username, CentBLG_article.nid, title, up_count  from CentBLG_article, CentBLG_userinfo " \
        "where CentBLG_article.user_id=CentBLG_userinfo.nid order by up_count desc limit 4",
        [])
    sql_helper.close()
    return render(request, 'index.html', locals())


"""
    文章详情，这个组件是必须的，因为关系到必要的文案沟通
"""
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


"""
    这个页面是标准的文章管理端，是文章的编写发布界面
"""
def backend(request):
    user = request.user
    username = user.username
    article_list = models.Article.objects.filter(user_id=user.pk)
    has_blog = models.UserInfo.objects.filter(nid=user.pk).first().blog_id
    return render(request, 'backend.html', locals())


"""
    新用户创建博客，旧用户访问不到
"""
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


"""
    公众网站，对外展示的
"""
def public(request):

    return render(request, 'public.html', locals())



"""
    实验室空间展示界面
"""
def lab(request):

    return render(request, 'lab.html', locals())



"""
    社区论坛界面
"""
def community(request):
    user = request.user
    article_list_all = models.Article.objects.all()
    article_list = []
    count = 0
    for i in range(len(article_list_all)):
        if i == 5: break
        article_list.append(article_list_all[i])
    sql_helper = SqlHelper()
    result = sql_helper.get_list(  # 精品文章榜单
        "select username, CentBLG_article.nid, title, up_count  from CentBLG_article, CentBLG_userinfo " \
        "where CentBLG_article.user_id=CentBLG_userinfo.nid order by up_count desc limit 4",
        [])
    sql_helper.close()
    return render(request, 'community.html', locals())
