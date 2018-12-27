from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.overview),
    path('overview/', views.overview),
    path('exchange/<str:exchange>/', views.exchange_view),
    path('instruments_data/<str:exchange>/', views.instruments_data),
]