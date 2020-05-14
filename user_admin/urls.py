from django.urls import path, include
from user_admin import views


urlpatterns = [
    path('login/', views.login),
    path('login2/', views.login_email),
    path('register/', views.register),
    path('logout/', views.logout),
    path('information/', views.show_information),
    path('change_password/', views.change_password),
]