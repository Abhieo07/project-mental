from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('profile', views.profile,name='profile'),
    path('setting', views.setting, name='setting'),
    path('logout', views.logout, name='logout')
]