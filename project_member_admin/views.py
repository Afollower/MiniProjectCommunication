from django.shortcuts import render, redirect
from .models import MPC_Project_group_pmd, MPC_Member_pg_pmd, MPC_Category_pg_pmd
from user_admin.models import MPC_User_ud
from project_admin.models import MPC_Project_pd, MPC_Level_pj_pd
from django.db.models import Max

# Create your views here.


# 成员管理[未完成]
def member_admin(request):
    pass
    return render(request, 'project_member/admin.html')


# 成员申请管理[未完成]  分组1-5预设为用户自定义； 设置分组：0申请名单 ， 10历史名单[退出项目后保存记录]
def join_admin(request):
    project_id = request.session.get('now_project_id', None)
    user_category = request.session.get('now_project_uc_id', None)
    if user_category == '1':
        pg_category = MPC_Category_pg_pmd.objects.filter(pg_id=project_id)
        # 获取申请名单
        member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id, pg_category_id=0)
        # 获取申请人员信息
        members = []
        for i in member:
            members.append(member.user_id)
        member_information = MPC_User_ud.objects.filter(user_id__in=members)
        if request.method == "POST":
            todo = request.POST['todo']
            user_id = request.POST['user_id']
            user_pgc = request.POST['member_pgc']
            if todo == '1':
                change_member = MPC_Member_pg_pmd.objects.get(user_id=user_id, pg_id=project_id)
                change_member.pg_category_id = user_pgc
                change_member.save()
            else:
                MPC_Member_pg_pmd.objects.get(user_id=user_id, pg_id=project_id).delete()
            return redirect('/project_member/join_admin/')
        return render(request, 'project_member/join_admin.html', {"member_information": member,
                                                           "pg_category": pg_category})
    else:
        message = '你不是当前项目管理员！请联系项目管理员。'
    return render(request, 'project_member/join_admin.html', locals())


