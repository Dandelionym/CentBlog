"""BlogCN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from BlogCN import settings
from CentBLG import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('digg/', views.digg),
    path('comment/', views.comment),
    path('viewed/', views.viewed),
    path('get_valid_img/', views.get_valid_img),
    
    
    
    
    
    path('backend/', views.backend),
    path('get_readamt_data/', views.get_readamt_data),
    path('get_heatmap_data/', views.get_heatmap_data),
    path('upload/', views.upload),
    path('modify/', views.modify),



    
    # Personal sites
    re_path('^(?P<username>\w+)/(?P<condition>tag|archive|category)/(?P<param>.*)/$', views.home_site),
    re_path('^(?P<username>\w+)/$', views.home_site),
    
    # Articles
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),
    
    # Media
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]
