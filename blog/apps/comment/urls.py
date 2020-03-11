from django.conf.urls import url
from .views import AddcommentView

app_name ='[comment]'
urlpatterns = [
    url(r'^add/$', AddcommentView, name='add_comment'),
]