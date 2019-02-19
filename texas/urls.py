# from django.conf.urls import url, include
# from django.contrib import admin
from . import views
# from django.urls import path
from django.conf.urls import url, include
from tastypie.api import Api
from resources import TexasResource

version_api = Api(api_name='v0')
version_api.register(TexasResource())

urlpatterns = [
    url('^index/$', views.index),
    url(r'^api/', include(version_api.urls))
]