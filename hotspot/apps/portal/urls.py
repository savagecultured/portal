from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<uuid:token_id>/', views.activate_token, name='activate_token'),
]