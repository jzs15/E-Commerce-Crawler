from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^products_filter/([\u4e00-\u9fa5]+)$', views.products_filter, name='products_filter'),
    url(r'^detail/([a-f\d]{24})$', views.products_detail, name='products_detail'),
]
