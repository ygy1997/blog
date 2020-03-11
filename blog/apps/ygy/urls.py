from django.conf.urls import url
from django.urls import path

from .views import IndexView, AboutView, MessageView, DonateView, ExchangeView, ProjectView, QuestionView, LinkView, \
    DetailView, LoveView, MySearchView

app_name ='[blog]'

urlpatterns = [
    # 首页
    url(r'^$', IndexView.as_view(template_name='index.html'), name='index'),  # 主页，自然排序
    url(r'^link/$', LinkView, name='link'),     # 申请友情链接
    url(r'^category/message/$', MessageView, name='message'),
    url(r'^category/about/$', AboutView, name='about'),
    url(r'^category/donate/$', DonateView, name='donate'),
    url(r'^category/exchange/$', ExchangeView, name='exchange'),
    url(r'^category/project/$', ProjectView, name='project'),
    url(r'^category/question/$', QuestionView, name='question'),
    # 分类页面
    path('category/<slug:bigslug>', IndexView.as_view(template_name='content.html'), name='bigcategory'),
    path('category/<slug:bigslug>/<slug:slug>', IndexView.as_view(template_name='content.html'), name='category'),
    # 归档页面
    url(r'^date/(?P<year>\d+)/(?P<month>\d+)/$', IndexView.as_view(template_name='archive.html'), name='date'),
    # 标签页面
    url(r'^tag/(?P<tag>.*?)/$', IndexView.as_view(template_name='content.html'), name='tag'),
    # 文章详情页面
    url(r'^article/(?P<slug>.*?)/$', DetailView.as_view(), name='article'),
    # 全文搜索
    url(r'^search/$', MySearchView.as_view(), name='search'),
    # 喜欢
    url(r'^love/$', LoveView, name='love'),
]