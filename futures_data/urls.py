from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.overview, name='overview'),
    path('overview/', views.overview, name='overview'),
    path('SHFE/', views.SHFE_view, name='SHFE_view'),
    path('DCE/', views.DCE_view, name='DCE_view'),
    path('CZCE/', views.CZCE_view, name='CZCE_view'),
    path('CFFEX/', views.CFFEX_view, name='CFFEX_view'),
    path('INE/', views.INE_view, name='INE_view'),
]