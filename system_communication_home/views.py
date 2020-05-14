from django.shortcuts import render, redirect
from . import models
from project_admin.models import MPC_Level_pj_pd, MPC_Project_pd
from project_member_admin.models import MPC_Category_pg_pmd, MPC_Member_pg_pmd
from user_admin.models import MPC_User_ud
from .models import MPC_problem_sch, MPC_Problem_complete_sch
from django.db.models import Max, Min

# Create your views here.


def index(request):
    user_id = request.session.get('user_id', None)
    project_id = request.session.get('now_project_id', None)
    my_problem = MPC_problem_sch.objects.filter(project_id=project_id, pp_author=user_id)
    to_my_problem = MPC_problem_sch.objects.filter(project_id=project_id, pp_to_user=user_id).exclude(pp_state='已解决')
    # 获取项目成员信息
    pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
    author = []
    for i in pg_member:
        author.append(i.user_id)
    author_information = MPC_User_ud.objects.filter(user_id__in=author)
    # 所有问题
    all_problem = MPC_problem_sch.objects.filter(project_id=project_id)
    return render(request, 'index/index.html', {
        "my_problem": my_problem, "to_my_problem": to_my_problem,
        "author_information": author_information, "all_problem": all_problem
    })


# 提出问题
def problem_proposed(request):
    if request.session.get('now_project_id', None) != '':
        project_id = request.session.get('now_project_id')
        if request.method == "POST":
            max_pp_id = MPC_problem_sch.objects.filter(project_id=project_id).aggregate(Max('pp_id'))
            # 问题ID ：取最大值+1（第一个问题为 1）
            if max_pp_id['pp_id__max']:
                pp_id = str(int(max_pp_id['pp_id__max']) + 1)
            else:
                pp_id = '1'
            pp_title = request.POST['pp_title']
            pp_author = request.session.get('user_id', None)
            pp_information = request.POST['pp_information']
            pp_to_user = request.POST['pp_to_user']
            if pp_to_user == '':
                pp_state = '待指派'
            else:
                pp_state = '进行中'
            pp_time = request.POST['pp_time']
            pl_id = request.POST['pl_id']
            if pp_title and pp_information:
                new_pp = MPC_problem_sch.objects.create()
                new_pp.pp_id = pp_id
                new_pp.pp_title = pp_title
                new_pp.pp_author = pp_author
                new_pp.pp_information = pp_information
                new_pp.pp_state = pp_state
                new_pp.pp_time = pp_time
                new_pp.pp_to_user = pp_to_user
                new_pp.project_id = project_id
                new_pp.pl_id = pl_id
                print(1)
                new_pp.save()
                return redirect('/index/')
            else:
                message = '请检查填写是否完整。'
                return render(request, 'problem/propose.html')
        else:
            try:
                project_pl = MPC_Level_pj_pd.objects.filter(project_id=project_id)
                pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
                # 获取项目中所有成员信息
                # 由于数据库原因：需要以user_id连接查询MPC_User_ud和MPC_Member_pg_pmd
                # 但是不知道如何连接查询，暂时用一下方法
                members = []
                for i in pg_member:
                    members.append(i.user_id)
                pg_member_information = MPC_User_ud.objects.filter(user_id__in=members)
                for i in pg_member_information:
                    print(i.user_name)
                return render(request, 'problem/propose.html', {"project_pl": project_pl, "pg_member": pg_member_information})
            except:
                message = "请先加入或选择项目，再进行问题提交"
                return render(request, 'index/index.html', locals())
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())


# 我提出的问题记录
def my_problem_list(request):
    if request.session.get('now_project_id', None) != '':
        user_id = request.session.get('user_id', None)
        project_id = request.session.get('now_project_id', None)
        try:
            all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
            project_pl = MPC_Level_pj_pd.objects.filter(project_id=project_id)
            # 获取项目中所有成员信息
            pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
            to_user = []
            for i in pg_member:
                to_user.append(i.user_id)
            pg_member_information = MPC_User_ud.objects.filter(user_id__in=to_user)
            if request.method == "POST":
                todo = request.POST['todo']
                show_pp_id = request.POST['pp_id']
                print("show_pp_id:")
                print(show_pp_id)
                # 当todo=2 只是查看，下面if直接跳过
                # 当todo=1 说明存在修改
                # 当todo=3 删除
                if todo == '1':
                    pp_title = request.POST['pp_title']
                    pl_id = request.POST['pl_id']
                    pp_information = request.POST['pp_information']
                    pp_state = request.POST['pp_state']
                    pp_to_user = request.POST['pp_to_user']
                    pp_time = request.POST['pp_time']
                    if pp_to_user == '':
                        pp_state = '待指派'
                    new_pp = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                    new_pp.pp_title = pp_title
                    new_pp.pp_information = pp_information
                    new_pp.pp_state = pp_state
                    new_pp.pp_time = pp_time
                    new_pp.pp_to_user = pp_to_user
                    new_pp.pl_id = pl_id
                    new_pp.save()
                    message = '修改成功！'
                    all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
                if todo == '3':
                    MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id).delete()
                    all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
                    max_pp = all_problem.aggregate(Max('pp_id'))
                    if max_pp['pp_id__max']:
                        show_pp_id = max_pp['pp_id__max']
                    else:
                        message = '请先提交问题'
                        return render(request, 'index/index.html', locals())
                show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                # 直接return 传数据到前端
                return render(request, 'problem/propose_list.html', {
                    "project_pl": project_pl, "show_problem": show_problem,
                    "all_problem": all_problem, "pg_member": pg_member_information})
            max_problem_id = all_problem.aggregate(Max('pp_id'))
            show_problem = MPC_problem_sch.objects.get(pp_id=str(max_problem_id['pp_id__max']), project_id=project_id)
            return render(request, 'problem/propose_list.html', {
                "project_pl": project_pl, "show_problem": show_problem,
                "all_problem": all_problem, "pg_member": pg_member_information })
        except:
            message = '尚未在该项目提出建议'
            return render(request, 'index/index.html', locals())
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())


# 待处理问题
def problem_solve(request):
    if request.session.get('now_project_id', None) != '':
        project_id = request.session.get('now_project_id', None)
        user_id = request.session.get('user_id', None)
        all_problem = MPC_problem_sch.objects.filter(pp_to_user=user_id, project_id=project_id).exclude(pp_state='已解决')
        # 获取项目级别信息
        pj_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
        # 获取作者信息
        all_creator = []
        for i in all_problem:
            all_creator.append(i.pp_author)
        all_creator_information = MPC_User_ud.objects.filter(user_id__in=all_creator)
        return render(request, 'problem/solve.html', {
            "all_problem": all_problem, "author": all_creator_information, "pj_level": pj_level})
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())


# 已处理问题
def problem_resolved(request):
    if request.session.get('now_project_id', None) != '':
        project_id = request.session.get('now_project_id', None)
        user_id = request.session.get('user_id', None)
        all_problem = MPC_problem_sch.objects.filter(pp_to_user=user_id, project_id=project_id).exclude(pp_state='进行中')
        # 获取项目级别信息
        pj_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
        # 获取作者信息
        all_creator = []
        for i in all_problem:
            all_creator.append(i.pp_author)
        all_creator_information = MPC_User_ud.objects.filter(user_id__in=all_creator)
        return render(request, 'problem/resolved.html', {
            "all_problem": all_problem, "author": all_creator_information, "pj_level": pj_level})
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())