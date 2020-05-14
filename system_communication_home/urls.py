from django.urls import path, include
from system_communication_home import views


urlpatterns = [
    path('', views.index),
    path('problem_proposed/', views.problem_proposed),
    path('my_problem/', views.my_problem_list),
    path('problem_solve/', views.problem_solve),
    path('problem_resolved/', views.problem_resolved),

]