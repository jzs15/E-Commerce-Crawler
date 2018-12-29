from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search$', views.search, name='search'),
    url(r'^products_filter/([\u4e00-\u9fa5]{2,4})$', views.products_filter, name='products_filter'),
    url(r'^compare/([a-f\d]{24})$', views.compare, name='compare')
]
