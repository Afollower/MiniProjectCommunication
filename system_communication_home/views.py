from django.shortcuts import render, redirect, HttpResponseRedirect
from . import models
from project_admin.models import MPC_Level_pj_pd, MPC_Project_pd, MPC_Schedule_pd
from project_member_admin.models import MPC_Category_pg_pmd, MPC_Member_pg_pmd
from user_admin.models import MPC_User_ud
from .models import MPC_problem_sch, MPC_Problem_communication_sch
from django.db.models import Max, Min, Count
# 将查询到的数据转换为json
import json
from django.core import serializers
# Django自带分页[数据分页]
from django.core.paginator import Paginator
# 获取时间
from django.utils import timezone
# Create your views here.


# 系统主页
def index(request):
    user_id = request.session.get('user_id', None)
    project_id = request.session.get('now_project_id', None)
    # 获取当前时间/ 更新问题状态
    all_problem = MPC_problem_sch.objects.filter(project_id=project_id)
    now_time_y = timezone.now().year
    now_time_m = timezone.now().month
    now_time_d = timezone.now().day
    for problem in all_problem:
        if problem.pp_state == '进行中':
            if int(now_time_y) < int(problem.pp_time[0:4]):
                print("year same")
            elif int(now_time_y) == int(problem.pp_time[0:4]):
                if int(now_time_m) < int(problem.pp_time[5:7]):
                    print("year/month same")
                elif int(now_time_m) == int(problem.pp_time[5:7]):
                    if int(now_time_d) <= int(problem.pp_time[8:10]):
                        print("nochange")
                    else:
                        print("dtime out")
                        test = 1
                        problem.pp_state = '已超时'
                        problem.save()
                else:
                    print("mtime out")
                    test = 1
                    problem.pp_state = '已超时'
                    problem.save()
            else:
                print("ytime out")
                test = 1
                problem.pp_state = '已超时'
                problem.save()
        elif problem.pp_state == '已超时':
            if int(now_time_y) < int(problem.pp_time[0:4]):
                print("state change")
                problem.pp_state = '进行中'
                problem.save()
            elif int(now_time_y) == int(problem.pp_time[0:4]):
                if int(now_time_m) < int(problem.pp_time[5:7]):
                    print("state change")
                    problem.pp_state = '进行中'
                    problem.save()
                elif int(now_time_m) == int(problem.pp_time[5:7]):
                    if int(now_time_d) <= int(problem.pp_time[8:10]):
                        print("state change")
                        problem.pp_state = '进行中'
                        problem.save()

    # 获取项目成员信息
    pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
    author = []
    for i in pg_member:
        author.append(i.user_id)
    author_information = MPC_User_ud.objects.filter(user_id__in=author)
    # 项目基础设定信息
    schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
    problem_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)

    # 所有问题
    my_problem = MPC_problem_sch.objects.filter(project_id=project_id, pp_author=user_id)
    to_my_problem = MPC_problem_sch.objects.filter(project_id=project_id, pp_to_user=user_id).exclude(pp_state='已解决')
    all_problem = MPC_problem_sch.objects.filter(project_id=project_id)

    all_pp_com = MPC_Problem_communication_sch.objects.filter(project_id=project_id)
    end_communication_information = all_pp_com.values('pp_id').annotate(pp_endtime=Max('ppc_time')).order_by()
    print(end_communication_information)

    limit = 4
    # 数据分页
    my_problem_pages = Paginator(my_problem, limit)
    if my_problem_pages.num_pages <= 1:
        problem_list1 = my_problem
        data1 = ''
    else:
        page = int(request.GET.get('page_mp', 1))
        problem_list1 = my_problem_pages.page(page)
        # 表单默认设置【初始】
        left = []  # 当前页左边连续的页码号，初始值为空
        right = []  # 当前页右边连续的页码号，初始值为空
        left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False  # 标示最后一页页码前是否需要显示省略号
        first = False  # 标示是否需要显示第 1 页的页码号。
        last = False  # 标示是否需要显示最后一页的页码号。
        total_pages = my_problem_pages.num_pages  # 总页数
        page_range = my_problem_pages.page_range
        if page == 1:  # 如果请求第1页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                right_has_more = True
            if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
                last = True
        elif page == total_pages:  # 如果请求最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            # 页数不确定
            if left[0] > 2:
                left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                first = True
        else:  # 如果请求的页码既不是第一页也不是最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        data1 = {  # 将数据包含在data字典中
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
            'total_pages': total_pages,
            'page': page
        }
    # 数据分页
    to_my_problem_pages = Paginator(to_my_problem, limit)
    if to_my_problem_pages.num_pages <= 1:
        problem_list2 = to_my_problem
        data2 = ''
    else:
        page = int(request.GET.get('page_tmp', 1))
        problem_list2 = to_my_problem_pages.page(page)
        # 表单默认设置【初始】
        left = []  # 当前页左边连续的页码号，初始值为空
        right = []  # 当前页右边连续的页码号，初始值为空
        left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False  # 标示最后一页页码前是否需要显示省略号
        first = False  # 标示是否需要显示第 1 页的页码号。
        last = False  # 标示是否需要显示最后一页的页码号。
        total_pages = to_my_problem_pages.num_pages  # 总页数
        page_range = to_my_problem_pages.page_range
        if page == 1:  # 如果请求第1页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                right_has_more = True
            if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
                last = True
        elif page == total_pages:  # 如果请求最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            # 页数不确定
            if left[0] > 2:
                left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                first = True
        else:  # 如果请求的页码既不是第一页也不是最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        data2 = {  # 将数据包含在data字典中
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
            'total_pages': total_pages,
            'page': page
        }
    # 数据分页
    all_problem_pages = Paginator(all_problem, limit)
    if all_problem_pages.num_pages <= 1:
        problem_list3 = all_problem
        data3 = ''
    else:
        page = int(request.GET.get('page_ap', 1))
        problem_list3 = all_problem_pages.page(page)
        # 表单默认设置【初始】
        left = []  # 当前页左边连续的页码号，初始值为空
        right = []  # 当前页右边连续的页码号，初始值为空
        left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False  # 标示最后一页页码前是否需要显示省略号
        first = False  # 标示是否需要显示第 1 页的页码号。
        last = False  # 标示是否需要显示最后一页的页码号。
        total_pages = all_problem_pages.num_pages  # 总页数
        page_range = all_problem_pages.page_range
        if page == 1:  # 如果请求第1页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                right_has_more = True
            if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
                last = True
        elif page == total_pages:  # 如果请求最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            # 页数不确定
            if left[0] > 2:
                left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                first = True
        else:  # 如果请求的页码既不是第一页也不是最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        data3 = {  # 将数据包含在data字典中
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
            'total_pages': total_pages,
            'page': page
        }
    return render(request, 'index/index.html', {
        "my_problem": problem_list1, "to_my_problem": problem_list2,
        "author_information": author_information, "all_problem": problem_list3,
        "schedule": schedule, "problem_level": problem_level,
        "end_communication_information": end_communication_information,
        'data1': data1, 'data2': data2, 'data3': data3
    })


# 提出问题
def problem_proposed(request):
    message = ''
    user_pgc = int(request.session.get('now_project_uc_id', None))
    print(user_pgc)
    # 判断是否加入项目[双重保险]
    if user_pgc in range(1, 5):
        project_id = request.session.get('now_project_id', None)
        user_id = request.session.get('user_id', None)
        if request.method == "POST":
            max_pp_id = MPC_problem_sch.objects.filter(project_id=project_id).aggregate(Max('pp_id'))
            # 问题ID ：取最大值+1（第一个问题为 1）
            if max_pp_id['pp_id__max']:
                pp_id = str(int(max_pp_id['pp_id__max']) + 1)
            else:
                pp_id = '1'
            pp_title = request.POST['pp_title']
            pp_author = user_id
            pp_information = request.POST['pp_information']
            pp_to_user = request.POST['pp_to_user']
            pp_schedule_id = request.POST['schedule_id']
            if pp_to_user == '':
                pp_state = '待指派'
            else:
                pp_state = '进行中'
            pp_time = request.POST['pp_time']
            pl_id = request.POST['pl_id']
            if pp_title != '' and pp_information != '':
                new_pp = MPC_problem_sch.objects.create()
                new_pp.pp_id = pp_id
                new_pp.pp_title = pp_title
                new_pp.pp_author = pp_author
                new_pp.pp_information = pp_information
                # 状态、预设结束时间、处理人
                new_pp.pp_state = pp_state
                new_pp.pp_time = pp_time
                new_pp.pp_to_user = pp_to_user
                # 级别和阶段信息
                new_pp.pl_id = pl_id
                new_pp.schedule_id = pp_schedule_id
                new_pp.project_id = project_id

                # 当前项目用户提交问题个数+1
                change_member = MPC_Member_pg_pmd.objects.get(user_id=user_id, pg_id=project_id)
                change_member.submit_sum += 1

                # 添加第一条交流信息：提交问题，请尽快处理。
                new_pp_communication = MPC_Problem_communication_sch.objects.create()
                new_pp_communication.pp_com_id = '1'
                new_pp_communication.pp_user_id = user_id
                new_pp_communication.ppc_describe = '问题已提交，请尽快处理！'
                new_pp_communication.pp_id = pp_id
                new_pp_communication.project_id = project_id
                # save放到最后
                new_pp.save()
                change_member.save()
                new_pp_communication.save()
                return HttpResponseRedirect('/index/')
            else:
                message = '请检查填写是否完整。'
        else:
            try:
                project_pl = MPC_Level_pj_pd.objects.filter(project_id=project_id)
                pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
                schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
                # 获取项目中所有成员信息
                # 由于数据库原因：需要以user_id连接查询MPC_User_ud和MPC_Member_pg_pmd
                # 但是不知道如何连接查询，暂时用一下方法
                members = []
                for i in pg_member:
                    members.append(i.user_id)
                pg_member_information = MPC_User_ud.objects.filter(user_id__in=members)
                return render(request, 'problem/propose.html', {
                    "project_pl": project_pl, "pg_member": pg_member_information,
                    "message": message, "schedule": schedule
                })
            except:
                message = "请先加入或选择项目，再进行问题提交"
                return render(request, 'index/index.html', locals())
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())


# 我提出的问题记录
def my_problem_list(request):
    message = ''
    user_pgc = int(request.session.get('now_project_uc_id', None))
    # 判断是否加入项目[双重保险]
    if user_pgc in range(1, 5):
        user_id = request.session.get('user_id', None)
        project_id = request.session.get('now_project_id', None)
        try:
            all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
            project_pl = MPC_Level_pj_pd.objects.filter(project_id=project_id)
            # 获取项目中所有成员信息
            pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
            pj_schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
            to_user = []
            for i in pg_member:
                to_user.append(i.user_id)
            pg_member_information = MPC_User_ud.objects.filter(user_id__in=to_user)
            if request.method == "POST":
                todo = request.POST['todo']
                show_pp_id = request.POST['pp_id']
                # 当todo=2 只是查看，下面if直接跳过
                # 当todo=1 说明存在修改
                # 当todo=3 删除
                print(todo)
                if todo == '1':
                    pp_title = request.POST['pp_title']
                    pl_id = request.POST['pl_id']
                    pp_information = request.POST['pp_information']
                    pp_state = request.POST['pp_state']
                    pp_to_user = request.POST['pp_to_user']
                    pp_time = request.POST['pp_time']
                    print("test")
                    schedule_id = request.POST['schedule_id']
                    print(pp_information)
                    print(show_pp_id)
                    print(pp_time)
                    if pp_to_user == '':
                        pp_state = '待指派'
                    new_pp = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                    new_pp.pp_title = pp_title
                    new_pp.pp_information = pp_information
                    new_pp.pp_state = pp_state
                    new_pp.pp_time = pp_time
                    new_pp.pp_to_user = pp_to_user
                    new_pp.schedule_id = schedule_id
                    new_pp.pl_id = pl_id
                    new_pp.save()
                    # 存储补充说明
                    ppc_describe = request.POST['ppc_describe']
                    if ppc_describe != '':
                        try:
                            all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                                 project_id=project_id)
                            max_communication_hst = all_communication_hst.aggregate(Max('pp_com_id'))
                            max_pp_com_id = str(max_communication_hst['pp_com_id__max'])
                            new_pp_com_id = str(int(max_pp_com_id) + 1)
                        except:
                            new_pp_com_id = '1'
                        new_pp_com = MPC_Problem_communication_sch.objects.create()
                        new_pp_com.pp_com_id = new_pp_com_id
                        new_pp_com.ppc_user_id = user_id
                        new_pp_com.ppc_describe = ppc_describe
                        new_pp_com.project_id = project_id
                        new_pp_com.pp_id = show_pp_id
                        new_pp_com.save()
                    message = '修改成功！'
                    return HttpResponseRedirect('/index/my_problem/')
                    all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
                if todo == '3':
                    del_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                    del_problem_com = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                   project_id=project_id)
                    if del_problem.pp_state == "已解决":
                        message = '当前问题已被处理，无法删除记录'
                        print(message)
                    elif del_problem:
                        message = '当前问题正在处理，无法删除记录'
                        print(message)
                    else:
                        del_problem.delete()
                        # 当前项目用户提交问题个数-1
                        change_member = MPC_Member_pg_pmd.objects.get(user_id=user_id)
                        change_member.submit_sum -= 1
                        change_member.save()
                        # 删除后显示另一个问题信息
                        all_problem = MPC_problem_sch.objects.filter(pp_author=user_id, project_id=project_id)
                        max_pp = all_problem.aggregate(Max('pp_id'))
                        if max_pp['pp_id__max']:
                            show_pp_id = max_pp['pp_id__max']
                        else:
                            message = '请先提交问题'
                            return render(request, 'index/index.html', locals())
                show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                     project_id=project_id)
                # 直接return 传数据到前端
                return render(request, 'problem/propose_list.html', {
                    "project_pl": project_pl, "show_problem": show_problem,
                    "all_problem": all_problem, "pg_member_information": pg_member_information,
                    "schedule": pj_schedule, "all_pp_communication": all_communication_hst, "message": message
                })
            max_problem_id = all_problem.aggregate(Max('pp_id'))
            show_pp_id = str(max_problem_id['pp_id__max'])
            show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
            all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                 project_id=project_id)
            return render(request, 'problem/propose_list.html', {
                "project_pl": project_pl, "show_problem": show_problem,
                "all_problem": all_problem, "pg_member_information": pg_member_information,
                "schedule": pj_schedule, "all_pp_communication": all_communication_hst, "message": message
            })
        except:
            message = '尚未在该项目提出建议'
            return render(request, 'index/index.html', locals())
    else:
        message = "请先加入或选择项目，再进行问题提交"
        return render(request, 'index/index.html', locals())


# 待处理问题【未完成，提交修改状态】
# 当前进度：05/18 修改警报信息，前三个权限管理当前界面已完成
def problem_solve(request):
    message = ''
    user_pgc = int(request.session.get('now_project_uc_id', None))
    # 判断是否加入项目[双重保险]
    if user_pgc in range(1, 5):
        project_id = request.session.get('now_project_id', None)
        user_id = request.session.get('user_id', None)
        # 获取数据
        # 获取未解决的问题
        all_problem = MPC_problem_sch.objects.filter(pp_to_user=user_id, project_id=project_id).\
            exclude(pp_state='已解决').order_by("pp_id")
        # 获取项目日程
        all_schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
        # 设置默认显示问题信息ID，但是对应界面为：点击出现界面，
        max_pp = all_problem.aggregate(Max('pp_id'))
        if max_pp['pp_id__max']:
            show_pp_id = max_pp['pp_id__max']
        else:
            message = '当前项目无需要处理问题！'
            return render(request, 'index/index.html', locals())
        # 获取项目级别信息
        pj_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
        # 获取项目成员信息
        pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
        all_creator = []
        for i in pg_member:
            all_creator.append(i.user_id)
        all_pg_member = MPC_User_ud.objects.filter(user_id__in=all_creator)
        # 历史记录
        all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                             project_id=project_id)
        # 数据分页
        limit = 5
        pages = Paginator(all_problem, limit)
        if pages.num_pages <= 1:
            problem_list = all_problem
            data = ''
        else:
            page = int(request.GET.get('page', 1))
            problem_list = pages.page(page)
            # 表单默认设置【初始】
            left = []  # 当前页左边连续的页码号，初始值为空
            right = []  # 当前页右边连续的页码号，初始值为空
            left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
            right_has_more = False  # 标示最后一页页码前是否需要显示省略号
            first = False  # 标示是否需要显示第 1 页的页码号。
            last = False  # 标示是否需要显示最后一页的页码号。
            total_pages = pages.num_pages  # 总页数
            page_range = pages.page_range
            if page == 1:  # 如果请求第1页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                    # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                    right_has_more = True
                if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                    # 所以需要显示最后一页的页码号，通过 last 来指示
                    last = True
            elif page == total_pages:  # 如果请求最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                # 页数不确定
                if left[0] > 2:
                    left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
                if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                    first = True
            else:  # 如果请求的页码既不是第一页也不是最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                if left[0] > 2:
                    left_has_more = True
                if left[0] > 1:
                    first = True
                if right[-1] < total_pages - 1:
                    right_has_more = True
                if right[-1] < total_pages:
                    last = True
            data = {  # 将数据包含在data字典中
                'left': left,
                'right': right,
                'left_has_more': left_has_more,
                'right_has_more': right_has_more,
                'first': first,
                'last': last,
                'total_pages': total_pages,
                'page': page
            }
        # 点击操作
        if request.method == "POST":
            todo = request.POST['todo']
            if todo == '1':
                show_pp_id = request.POST['pp_id']
            elif todo == '2':
                show_pp_id = request.POST['pp_id']
                show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                try:
                    all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                         project_id=project_id)
                    return render(request, 'problem/solve1.html', {
                        "show_problem": show_problem, "all_pg_member": all_pg_member,
                        "pj_level": pj_level, "all_pp_communication": all_communication_hst,
                        "all_schedule": all_schedule, "message": message
                    })
                except:
                    return render(request, 'problem/solve1.html', {
                        "show_problem": show_problem, "all_pg_member": all_pg_member,
                        "pj_level": pj_level, "all_pp_communication": '', "all_pp_communication": all_communication_hst,
                        "all_schedule": all_schedule, "message": message
                    })
            elif todo == '3':
                ppc_describe = request.POST['ppc_describe']
                pp_state = request.POST['pp_state']
                if pp_state == '已解决':
                    show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                    print(show_problem.pp_title)
                    show_problem.pp_state = '已解决'
                    show_problem.save()
                    message = '本问题已回复解决！'
                else:
                    message = '已回复，请继续跟进！'
                try:
                    all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                         project_id=project_id)
                    max_communication_hst = all_communication_hst.aggregate(Max('pp_com_id'))
                    max_pp_com_id = str(max_communication_hst['pp_com_id__max'])
                    new_pp_com_id = str(int(max_pp_com_id) + 1)
                except:
                    new_pp_com_id = '1'
                new_pp_com = MPC_Problem_communication_sch.objects.create()
                new_pp_com.pp_com_id = new_pp_com_id
                new_pp_com.ppc_user_id = user_id
                new_pp_com.ppc_describe = ppc_describe
                new_pp_com.project_id = project_id
                new_pp_com.pp_id = show_pp_id
                new_pp_com.save()
                # 更新历史记录
                all_communication_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                     project_id=project_id)
                return HttpResponseRedirect('/index/problem_solve/')
        # 获取显示问题信息，放在这里方便切换显示功能实现
        show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)

        return render(request, 'problem/solve.html', {
            "all_problem": problem_list, "all_pg_member": all_pg_member, "pj_level": pj_level,
            "show_problem": show_problem, "data": data, "all_schedule": all_schedule,
            "all_pp_communication": all_communication_hst, "message": message
        })
    else:
        message = "请先加入或选择项目，再查看待处理问题。"
        return render(request, 'index/index.html', locals())


# 已处理问题
def problem_resolved(request):
    message = ''
    user_pgc = int(request.session.get('now_project_uc_id', None))
    # 判断是否加入项目[双重保险]
    if user_pgc in range(1, 5):
        project_id = request.session.get('now_project_id', None)
        user_id = request.session.get('user_id', None)
        # 获取已解决问题并验证
        all_problem = MPC_problem_sch.objects.filter(pp_to_user=user_id, project_id=project_id, pp_state='已解决')
        show_pp_id = all_problem.aggregate(Max('pp_id'))['pp_id__max']
        if show_pp_id:
            show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
        else:
            message = '暂无处理完成的问题记录'
            return render(request, 'index/index.html', {"message": message})
        # 数据分页
        limit = 5
        pages = Paginator(all_problem, limit)
        if pages.num_pages <= 1:
            problem_list = all_problem
            data = ''
        else:
            page = int(request.GET.get('page', 1))
            problem_list = pages.page(page)
            # 表单默认设置【初始】
            left = []   # 当前页左边连续的页码号，初始值为空
            right = []  # 当前页右边连续的页码号，初始值为空
            left_has_more = False   # 标示第 1 页页码后是否需要显示省略号
            right_has_more = False  # 标示最后一页页码前是否需要显示省略号
            first = False   # 标示是否需要显示第 1 页的页码号。
            last = False    # 标示是否需要显示最后一页的页码号。
            total_pages = pages.num_pages   # 总页数
            page_range = pages.page_range
            if page == 1:  # 如果请求第1页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                print(total_pages)
                if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                    # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                    right_has_more = True
                if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                    # 所以需要显示最后一页的页码号，通过 last 来指示
                    last = True
            elif page == total_pages:  # 如果请求最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                # 页数不确定
                if left[0] > 2:
                    left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
                if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                    first = True
            else:  # 如果请求的页码既不是第一页也不是最后一页
                left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
                right = page_range[page:page + 2]  # 获取右边连续号码页
                if left[0] > 2:
                    left_has_more = True
                if left[0] > 1:
                    first = True
                if right[-1] < total_pages - 1:
                    right_has_more = True
                if right[-1] < total_pages:
                    last = True
            data = {  # 将数据包含在data字典中
                'left': left,
                'right': right,
                'left_has_more': left_has_more,
                'right_has_more': right_has_more,
                'first': first,
                'last': last,
                'total_pages': total_pages,
                'page': page
            }
        # 获取项目级别信息
        pj_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
        # 获取项目阶段信息
        all_schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
        # 获取项目成员信息
        pg_member = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
        all_creator = []
        for i in pg_member:
            all_creator.append(i.user_id)
        pg_member_information = MPC_User_ud.objects.filter(user_id__in=all_creator)
        # 获取查询的数据
        if request.method == "POST":
            todo = request.POST['todo']
            if todo == '1':
                show_pp_id = request.POST['pp_id']
                show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
                show_problem_com_hst = MPC_Problem_communication_sch.objects.filter(pp_id=show_pp_id,
                                                                                    project_id=project_id)
                max_pp_com_id = show_problem_com_hst.aggregate(Max('pp_com_id'))['pp_com_id__max']
                end_information = MPC_Problem_communication_sch.objects.get(pp_id=show_pp_id, pp_com_id=max_pp_com_id,
                                                                            project_id=project_id)
                problem_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
                return render(request, 'problem/resolved_show.html', {
                    "show_problem": show_problem, "all_pp_communication": show_problem_com_hst,
                    "end_information": end_information, "all_schedule": all_schedule,
                    "problem_level": problem_level, "member_information": pg_member_information,
                    "message": message
                })
            elif todo == '2':
                return HttpResponseRedirect('/index/problem_resolved')
            elif todo == '3':
                1
        return render(request, 'problem/resolved.html', {
            "all_problem": problem_list, "data": data,
            "member_information": pg_member_information, "pj_level": pj_level, "message": message
        })
    else:
        message = "请先加入或选择项目，再查看处理问题记录。"
        return render(request, 'index/index.html', {"message": message})
