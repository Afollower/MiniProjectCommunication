from django.urls import path
from project_admin import views


urlpatterns = [
    # 项目设定
    path('created/', views.project_create),
    path('member_admin/', views.member_admin),
    path('information/', views.project_information),
    path('schedule/', views.add_project_schedule),
    path('problem_level/', views.set_project_pl),
    # 项目成员分类设置
    path('member_category/', views.set_project_group),
    # 项目成员权限设置

]
