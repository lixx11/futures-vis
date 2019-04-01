from django.urls import path

from . import views

urlpatterns = [
    path('', views.overview),
    path('overview/', views.overview),
    path('exchange/<str:exchange>/', views.exchange_view),
    path('instruments_data/<str:exchange>/', views.instruments_data),
    path('major_instruments/', views.major_instruments_view),
    path('major_instruments_data/<str:code>/<str:plot_type>', views.major_instruments_data),
    path('basis', views.basis_view)
]