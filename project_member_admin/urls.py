from django.urls import path
from project_member_admin import views


urlpatterns = [
    path('admin/', views.member_admin),
    path('join_admin/', views.join_admin),
]