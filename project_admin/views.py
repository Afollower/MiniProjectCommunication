from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Max
from .models import MPC_Project_pd, MPC_Level_pj_pd
from project_member_admin.models import MPC_Project_group_pmd, MPC_Member_pg_pmd, MPC_Category_pg_pmd
from user_admin.models import MPC_User_state_ud, MPC_User_ud
import random
import string

# Create your views here.


# 创建项目界面
def project_create(request):
    if request.method == "POST":
        # 基础信息
        project_name = request.POST['project_name']
        project_creator_id = request.session.get('user_id', None)
        project_code1 = request.POST['project_code1']
        project_code2 = request.POST['project_code2']
        # 不输入邀请码，自动生成6位
        if project_code1 == '':
            random_str = random.sample('abcdefghijklmeopqrstuvwxyz', 6)
            project_code1 = 'Code_'
            for i in random_str:
                project_code1 = project_code1 + i
            project_code2 = project_code1
        print(project_code1)
        project_td = request.POST['project_td']
        # 创建项目ID MPC + 年月日 + 项目序号（从01开始99结束）
        create_time_y = timezone.now().year
        create_time_m = timezone.now().month
        create_time_d = timezone.now().day
        data_time = 'mpc' + str(create_time_y) + \
                    str(create_time_m).rjust(2, '0') + str(create_time_d).rjust(2, '0')
        # max_id 是以字典类型存储 键值： project_id__max
        max_id = MPC_Project_pd.objects.all().aggregate(Max('project_id'))
        if max_id['project_id__max']:
            # 存在已有项目时，提取字典中的值
            max_pj_id = str(max_id['project_id__max'])
            if data_time == max_pj_id[0:11]:
                if max_pj_id[11:] == '99':
                    print("单日创建达到最大限制")
                else:
                    print("准备新建立")
                    print(int(max_pj_id[11:]))
                    pj_id = data_time + str(int(max_pj_id[11:]) + 1).rjust(2, '0')
            else:
                pj_id = data_time + '01'
        else:
            pj_id = data_time + '01'  # 第一个项目创建时会用到

        # 成员分组信息  :  pg_category_sum -> 判断添加了几个div
        pgc_id = []
        pgc_name = []
        pgc_describe = []
        pg_category_sum = request.POST['pg_category_sum']
        for i in range(1, int(pg_category_sum) + 1):
            pgc_id.append(request.POST['pg_category_id' + str(i)])
            pgc_name.append(request.POST['pg_category_name' + str(i)])
            pgc_describe.append(request.POST['pg_category_describe' + str(i)])
            print(pgc_id[i-1], pgc_name[i-1], pgc_describe[i-1])

        # 问题级别设定
        pl_id = []
        pl_name = []
        pl_describe = []
        pl_sum = request.POST['pl_sum']
        for i in range(1, int(pl_sum) + 1):
            pl_id.append(request.POST['pl_id' + str(i)])
            pl_name.append(request.POST['pl_name' + str(i)])
            pl_describe.append(request.POST['pl_describe' + str(i)])
            print(pl_id[i - 1], pl_name[i - 1], pl_describe[i - 1])

        if project_name and project_code1:
            if project_code1 == project_code2:
                # 创建项目
                new_pj = MPC_Project_pd.objects.create()
                new_pj.project_id = pj_id
                new_pj.project_creator_id = project_creator_id
                new_pj.project_name = project_name
                new_pj.project_code = project_code1
                new_pj.project_td = project_td
                new_pj.save()

                # 创建项目组
                new_pg = MPC_Project_group_pmd.objects.create()
                new_pg.pg_id = pj_id
                new_pg.pg_name = project_name + '项目组'
                new_pg.project_id = pj_id
                new_pg.save()

                # 创建项目组成员分类信息
                for i in range(int(pg_category_sum)):
                    new_pgc = MPC_Category_pg_pmd.objects.create()
                    new_pgc.pg_category_id = pgc_id[i]
                    new_pgc.pg_category_name = pgc_name[i]
                    new_pgc.pg_category_describe = pgc_describe[i]
                    new_pgc.pg_id = pj_id
                    new_pgc.save()

                # 创建问题级别信息
                for i in range(int(pl_sum)):
                    new_pl = MPC_Level_pj_pd.objects.create()
                    new_pl.pl_id = pl_id[i]
                    new_pl.pl_name = pl_name[i]
                    new_pl.pl_describe = pl_describe[i]
                    new_pl.project_id = pj_id
                    new_pl.save()

                # 添加成员（创造者）
                new_member_pg = MPC_Member_pg_pmd.objects.create()
                new_member_pg.pg_id = pj_id
                new_member_pg.pg_category_id = pgc_id[0]      # 默认管理员
                new_member_pg.user_id = project_creator_id
                new_member_pg.save()

                # 更新当前项目为新建项目：后续 是创建特定列
                user_state = MPC_User_state_ud.objects.get(user_id=project_creator_id)
                user_state.project_id = pj_id
                user_state.pg_category_id = '1'
                user_state.save()

                request.session['now_project_id'] = pj_id
                request.session['now_project_name'] = project_name
                request.session['now_project_uc_id'] = '1'  # '1'管理员等级
                return redirect('/index/')
            else:
                message = '请确认项目邀请码'
        else:
            message = '请确认项目名称或邀请码是否填写正确'

        return render(request, 'project/create.html')
    return render(request, 'project/create.html')


# 项目信息显示[修改未完成]
def project_information(request):
    now_project_id = request.session.get('now_project_id', None)
    now_project_uc_id = request.session.get('now_project_uc_id', None)
    try:
        now_project = MPC_Project_pd.objects.get(project_id=now_project_id)
        # 获取项目负责人信息
        project_creator = MPC_User_ud.objects.get(user_id=now_project.project_creator_id)
        # 获取项目基础设定信息
        now_project_uc = MPC_Category_pg_pmd.objects.filter(pg_id=now_project_id)
        now_project_problem_level = MPC_Level_pj_pd.objects.filter(project_id=now_project_id)
        if request.method == "POST":
            project_name = request.POST['project_name']
            project_code = request.POST['project_code1']
            now_project.project_name = project_name
            now_project.project_code = project_code
            project_name.save()
            message = '项目信息修改成功！'
            return render(request, 'index/index.html', locals())
        return render(request, 'project/information.html', {"project": now_project,
                                                            "project_creator": project_creator,
                                                            "project_uc": now_project_uc,
                                                            "project_problem_level": now_project_problem_level})
    except:
        message = '请先加入或选择项目组'
        return render(request, 'user/index.html')


# 项目日程管理[未完成]
def set_project_schedule(request):
    pass
    return render(request, 'project/create.html')


# 设置项目问题等级
def set_project_pl(request):
    user_category = request.session.get('now_project_uc_id', None)
    if user_category == '1':
        project_id = request.session.get('now_project_id', None)
        project_pl = MPC_Level_pj_pd.objects.filter(project_id=project_id)
        old = 0
        for i in project_pl:
            print(i.pl_id)
            old += 1
        if request.method == "POST":
            # 问题级别设定
            pl_id = []
            pl_name = []
            pl_describe = []
            pl_sum = request.POST['pl_sum']
            for i in range(1, int(pl_sum) + 1):
                pl_id.append(request.POST['pl_id' + str(i)])
                pl_name.append(request.POST['pl_name' + str(i)])
                pl_describe.append(request.POST['pl_describe' + str(i)])
                print(pl_id[i - 1], pl_name[i - 1], pl_describe[i - 1])
            # 更新问题级别信息
            if old <= int(pl_sum):
                for i in range(int(pl_sum)):
                    try:
                        new_pl = MPC_Level_pj_pd.objects.get(pl_id=pl_id[i], project_id=project_id)
                        new_pl.pl_name = pl_name[i]
                        new_pl.pl_describe = pl_describe[i]
                        new_pl.save()
                    except:
                        new_pl = MPC_Level_pj_pd.objects.create()
                        new_pl.pl_id = pl_id[i]
                        new_pl.pl_name = pl_name[i]
                        new_pl.pl_describe = pl_describe[i]
                        new_pl.project_id = project_id
                        new_pl.save()
            else:
                # int(pl_sum)
                for i in range(old):
                    if i < int(pl_sum):
                        new_pl = MPC_Level_pj_pd.objects.get(pl_id=pl_id[i], project_id=project_id)
                        new_pl.pl_name = pl_name[i]
                        new_pl.pl_describe = pl_describe[i]
                        new_pl.save()
                    else:
                        MPC_Level_pj_pd.objects.get(pl_id=str(i+1), project_id=project_id).delete()
            message = '修改成功'
            return redirect('/project/information/')
        return render(request, 'project/problem_level.html', {
            "project_pl": project_pl
        })
    elif user_category > 1 or user_category <= 4:
        message = '您的权限不足！'
        return render(request, 'index/index.htm', locals())
    else:
        message = '请先创建项目！'
        return render(request, 'index/index.htm', locals())


# 项目分组信息设定
def set_project_group(request):
    user_category = request.session.get('now_project_uc_id', None)
    if user_category == '1':
        project_id = request.session.get('now_project_id', None)
        pg_category = MPC_Category_pg_pmd.objects.filter(pg_id=project_id)
        old_pgc = pg_category.aggregate(Max('pg_category_id'))
        old = int(old_pgc['pg_category_id__max'])
        print("type:{}, value:{}", type(old), old)
        if request.method == "POST":
            # 成员分组信息  :  pg_category_sum -> 判断添加了几个div
            pgc_id = []
            pgc_name = []
            pgc_describe = []
            pg_category_sum = request.POST['pg_category_sum']
            for i in range(1, int(pg_category_sum) + 1):
                pgc_id.append(request.POST['pg_category_id' + str(i)])
                pgc_name.append(request.POST['pg_category_name' + str(i)])
                pgc_describe.append(request.POST['pg_category_describe' + str(i)])
                if pgc_name[i-1] == '' or pgc_describe == '':
                    message = '请检查表单填写情况！'
                    return redirect('/project/member_category/')
                print(pgc_id[i - 1], pgc_name[i - 1], pgc_describe[i - 1])
                # 创建项目组成员分类信息
            if int(pg_category_sum) >= old:
                for i in range(1, int(pg_category_sum)):
                    print("增加或者不变")
                    try:
                        new_pgc = MPC_Category_pg_pmd.objects.get(pg_category_id=pgc_id[i], pg_id=project_id)
                        new_pgc.pg_category_name = pgc_name[i]
                        new_pgc.pg_category_describe = pgc_describe[i]
                        new_pgc.save()
                    except:
                        new_pgc = MPC_Category_pg_pmd.objects.create()
                        new_pgc.pg_category_id = pgc_id[i]
                        new_pgc.pg_category_name = pgc_name[i]
                        new_pgc.pg_category_describe = pgc_describe[i]
                        new_pgc.pg_id = project_id
                        new_pgc.save()
            else:
                print("减少")
                for i in range(old):
                    print("old:{}", old)
                    print(int(pg_category_sum))
                    if i < int(pg_category_sum):
                        new_pgc = MPC_Category_pg_pmd.objects.get(pg_category_id=pgc_id[i], pg_id=project_id)
                        new_pgc.pg_category_name = pgc_name[i]
                        new_pgc.pg_category_describe = pgc_describe[i]
                        new_pgc.save()
                    else:
                        # 列表中只存储了部分等级信息，需要删除全部等级信息，加之i = 0~old-1  pgc_id 1~odl  有对应关系
                        MPC_Category_pg_pmd.objects.get(pg_category_id=str(i+1), pg_id=project_id).delete()
            message = '修改成功'
            return redirect('/index/')
        return render(request, 'project/member_category.html', {"project_member_category": pg_category})
    elif user_category > 1 or user_category <= 4:
        message = '您的权限不足！'
        return render(request, 'index/index.htm', locals())
    else:
        message = '请先创建项目！'
        return render(request, 'index/index.htm', locals())


# 加入项目 [待验证]
def project_join(request):
    user_id = request.session.get('user_id', None)
    try:
        # 加入了部分项目,其中包括申请，已加入，和退出的
        all_pg = MPC_Member_pg_pmd.objects.filter(user_id=user_id)
        projects = []
        print("加入了部分项目")
        for pj in all_pg:
            projects.append(pj.pg_id)
        in_projects = MPC_Project_pd.objects.exclude(project_id__in=projects)
        max_in_projects = in_projects.aggregate(Max('project_id'))
        show_pg_id = max_in_projects['project_id__max']
        if show_pg_id:
            print("project_admin/views.y/project_join: 有项目未加入")
        else:
            print("project_admin/views.y/project_join: 加入了所有项目，直接结束")
            # 加入了所有项目，直接结束
            message = '你已经加入所有项目！'
            return render(request, 'index/index.html', locals())
    except:
        # 没加入过项目
        print("project_admin/views.y/project_join: 没加入项目")
        in_projects = MPC_Project_pd.objects.all()
    # 项目创建者信息
    creators = []
    for pj in in_projects:
        creators.append(pj.project_creator_id)
    creators_information = MPC_User_ud.objects.filter(user_id__in=creators)
    # 展示项目信息
    show_project = MPC_Project_pd.objects.get(project_id=show_pg_id)
    show_pg_category = MPC_Category_pg_pmd.objects.filter(pg_id=show_pg_id)
    if request.method == "POST":
        # 点击右侧项目信息，接收点击的项目ID
        todo = request.POST['todo']
        # 加入申请
        if todo == '1':
            project_id = request.POST['project_id']
            project_code = request.POST['project_code']
            pg_category_id = request.POST['pg_category_id']
            project = MPC_Project_pd.objects.get(project_id=project_id)
            # 验证用户是否加入
            try:
                check_user = MPC_Member_pg_pmd.objects.get(pg_id=project_id, user_id=user_id)
                if check_user.pg_category_id != '10':
                    print("你已经加入项目，或在申请名单中")
                    message = '你已经加入了项目，或在申请名单中！'
                    return render(request, 'project/join.html', locals())
                else:
                    # 被删除或者退出后重新加入
                    check_user.pg_category_id = '0'
                    check_user.save()
                    message = '申请成功，请等待管理员通过'
                    return render(request, 'index/index.html', locals())
            except:
                if project_code != project.project_code:
                    pg_category_id = '0'
                    message = '申请成功，请等待管理员通过！'
                else:
                    message = '加入成功！'
                new_member = MPC_Member_pg_pmd.objects.create()
                new_member.pg_id = project_id
                new_member.pg_category_id = pg_category_id
                new_member.user_id = user_id
                new_member.save()
                return render(request, 'index/index.html', locals())
        # 切换显示项目
        show_pg_id = request.POST['project_id']
        show_pg_category = MPC_Category_pg_pmd.objects.filter(pg_id=show_pg_id)
        show_project = MPC_Project_pd.objects.get(project_id=show_pg_id)
    return render(request, 'project/join.html', {
        "show_project": show_project, "show_pg_category": show_pg_category,
        "all_project": in_projects, "user_information": creators_information
    })


# 我的项目
def project_for_me(request):
    user_id = request.session.get('user_id', None)
    if request.method == "POST":
        todo = request.POST['todo']
        project_id = request.POST['project_id']
        project = MPC_Project_pd.objects.get(project_id=project_id)
        pg_information = MPC_Member_pg_pmd.objects.get(pg_id=project_id, user_id=user_id)
        if todo == '1':
            # 切换当前项目
            request.session['now_project_id'] = project_id
            request.session['now_project_name'] = project.project_name
            request.session['now_project_uc_id'] = pg_information.pg_category_id
            return redirect('/project/my/')
        else:
            # 退出项目
            pg_information.pg_category_id = '10'    # 存储在历史记录中
            pg_information.save()
            return redirect('/project/my/')
    else:
        # 获取我加入的项目
        in_pg_category = ['1', '2', '3', '4']  # 默认最多4个分类
        # 判断是否加入或创建过项目
        try:
            my_pgs = MPC_Member_pg_pmd.objects.filter(user_id=user_id, pg_category_id__in=in_pg_category)
        except:
            message = '请先加入或创建项目！'
            return render(request, 'index/index.html', locals())
        project_ids = []
        for pj in my_pgs:
            project_ids.append(pj.pg_id)
        my_projects = MPC_Project_pd.objects.filter(project_id__in=project_ids)
        return render(request, 'project/my_projects.html', {
            "my_projects": my_projects, "my_pgs": my_pgs
        })



