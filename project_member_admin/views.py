from django.shortcuts import render, redirect
from .models import MPC_Project_group_pmd, MPC_Member_pg_pmd, MPC_Category_pg_pmd

# Create your views here.


# 成员管理[未完成]
def member_admin(request):
    pass
    return render(request, 'project/member_admin.html')


# 成员申请管理[未完成]  分组1-5预设为用户自定义； 设置分组：0申请名单 ， 10历史名单[退出项目后保存记录]
def join_admin(request):
    project_id = request.session.get('now_project_id', None)
    user_category = request.session.get('now_project_uc_id', None)
    if user_category == '1':
        member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id, pg_uc_id=0)
        member_id = []
        for i in member:
            member_id.append(member.user_id)

        return render(request, 'project/join_admin.html', {})
    else:
        message = '你不是当前项目管理员！请联系项目管理员。'
    return render(request, 'project/join_admin.html')

