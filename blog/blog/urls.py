"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

from apps.ygy import sitemap
from apps.ygy.sitemap import ArticleSitemap, TagSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap

from blog import settings

from rest_framework.routers import DefaultRouter
from api import views as api_views
   # restframework
sitemaps = {
    'articles': ArticleSitemap,
    'tags': TagSitemap,
    'categories': CategorySitemap
}
if settings.API_FLAG:
    router = DefaultRouter()
    router.register(r'users', api_views.UserListSet)
    router.register(r'articles', api_views.ArticleListSet)
    router.register(r'tags', api_views.TagListSet)
    router.register(r'categorys', api_views.CategoryListSet)

urlpatterns = [
    # 后台管理应用，django自带
    url(r'^admin/', admin.site.urls),
    #用户
    url(r'^accounts/', include('apps.user.urls', namespace='accounts')),
    # ygy 应用
    url('', include('apps.ygy.urls', namespace='blog')),
    url(r'^comment/', include('apps.comment.urls', namespace='comment')),
    url(r'^sitemap\.xml$', sitemap,{'sitemaps': sitemaps}, name='sitemap'),  # 网站地图
    path('ueditor/',include('DjangoUeditor.urls'))
]

if settings.API_FLAG:
    urlpatterns.append(url(r'^api/v1/', include((router.urls,'api'),namespace="api")))

if settings.DEBUG:

    media_root = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT)

    urlpatterns += static(settings.MEDIA_URL, document_root=media_root)




