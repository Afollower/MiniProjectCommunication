from django.urls import path
from project_admin import views


urlpatterns = [
    # 项目设定
    path('created/', views.project_create),
    path('information/', views.project_information),
    path('schedule/', views.set_project_schedule),
    # 项目成员分类设置
    path('problem_level/', views.set_project_pl),
    # 项目成员权限设置
    path('member_category/', views.set_project_group),

    # 已加入项目
    path('join/', views.project_join),
    path('my/', views.project_for_me),


]
