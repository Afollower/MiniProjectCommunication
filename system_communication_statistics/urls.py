from django.contrib import admin
from django.urls import path, include
from system_communication_statistics import views

urlpatterns = [
    path('', views.all_problem_statistics_show),
]