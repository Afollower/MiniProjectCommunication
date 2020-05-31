from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import response
from . import models
from project_admin.models import MPC_Level_pj_pd, MPC_Project_pd, MPC_Schedule_pd
from project_member_admin.models import MPC_Category_pg_pmd, MPC_Member_pg_pmd
from user_admin.models import MPC_User_ud
from system_communication_home.models import MPC_problem_sch, MPC_Problem_communication_sch
from django.db.models import Max, Min, Count
import json
# Django自带分页[数据分页]
from django.core.paginator import Paginator
# Create your views here.


def all_problem_statistics_show(request):
    project_id = request.session.get('now_project_id', None)
    user_id = request.session.get('user_id', None)

    schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)

    all_problem = MPC_problem_sch.objects.filter(project_id=project_id)
    resolved_problem = MPC_problem_sch.objects.filter(project_id=project_id, pp_state='已解决')
    unresolved_problem = MPC_problem_sch.objects.filter(project_id=project_id).exclude(pp_state='已解决')
    schedule_all_problem = all_problem.values('schedule_id').annotate(pp_sum=Count('schedule_id')).order_by()
    schedule_resolved_problem = resolved_problem.values('schedule_id').annotate(pp_sum=Count('schedule_id')).order_by()
    schedule_unresolved_problem = unresolved_problem.values('schedule_id').annotate(pp_sum=Count('schedule_id')).order_by()
    max_scid = schedule.aggregate(Max('schedule_id'))['schedule_id__max']
    title = []
    title_id = []
    for sc in schedule:
        title_id.append(sc.schedule_id)
        title.append(sc.schedule_name)

    all_problem = []
    unresolved_problem = []
    resolved_problem = []
    completion = []
    uncompletion = []
    for i in range(int(max_scid)):
        resolved_problem.append(0)
        unresolved_problem.append(0)
        all_problem.append(0)
        completion.append(0)
        uncompletion.append(0)
    for i in range(int(max_scid)):
        for ok in schedule_resolved_problem:
            if title_id[i] == ok['schedule_id']:
                resolved_problem[i] = int(ok['pp_sum'])

    for i in range(int(max_scid)):
        for un in schedule_unresolved_problem:
            if title_id[i] == un['schedule_id']:
                unresolved_problem[i] = int(un['pp_sum'])
                uncompletion[i] = 1
    for i in range(int(max_scid)):
        for al in schedule_all_problem:
            if title_id[i] == al['schedule_id']:
                all_problem[i] = int(al['pp_sum'])

    for i in range(int(max_scid)):
        for re in schedule_resolved_problem:
            if title_id[i] == re['schedule_id']:
                for al in schedule_all_problem:
                    if re['schedule_id'] == al['schedule_id']:
                        if re['pp_sum'] != 0:
                            completion[i] = round(re['pp_sum'] / al['pp_sum'], 2)
    # 折线图数据round(a/b,2)
    for i in range(int(max_scid)):
        uncompletion[i] = 1
    print(completion)
    # 饼图数据
    pie_data = [0, 0]
    for i in range(int(max_scid)):
        pie_data[0] += resolved_problem[i]
        pie_data[1] += unresolved_problem[i]

    jsondata = {
        "title": title,
        "resolved": resolved_problem,
        "unresolved": unresolved_problem,
        "all": all_problem,
        "completion": completion,
        "uncompletion": uncompletion,
        "pie_data": pie_data
    }
    # 项目基础信息
    members = MPC_Member_pg_pmd.objects.filter(pg_id=project_id)
    member = []
    for i in members:
        member.append(i.user_id)
    member_information = MPC_User_ud.objects.filter(user_id__in=member)
    problem_level = MPC_Level_pj_pd.objects.filter(project_id=project_id)
    all_schedule = MPC_Schedule_pd.objects.filter(project_id=project_id)
    # 交流信息
    all_pp_com = MPC_Problem_communication_sch.objects.filter(project_id=project_id)
    end_communication_information = all_pp_com.values('pp_id').annotate(pp_endtime=Max('ppc_time')).order_by()

    schedule_has_problem = []
    for i in schedule_all_problem:
        if i['pp_sum'] > 0:
            schedule_has_problem.append(i['schedule_id'])
    show_schedule_id = schedule_has_problem[0]
    if request.method == 'POST':
        todo = request.POST['todo']
        print(todo)
        if todo == '2':
            show_schedule_id = request.POST['schedule_id']
            print(show_schedule_id)
            if show_schedule_id not in schedule_has_problem:
                show_schedule_id = schedule_has_problem[0]
        elif todo == '1':
            show_pp_id = request.POST['pp_id']
            show_problem = MPC_problem_sch.objects.get(pp_id=show_pp_id, project_id=project_id)
            all_pp_com = MPC_Problem_communication_sch.objects.filter(project_id=project_id, pp_id=show_pp_id)

            return render(request, 'problem/show.html', {
                "show_problem": show_problem, "pp_communication": all_pp_com,
                "end_pp_communication": end_communication_information, "all_schedule": all_schedule,
                "problem_level": problem_level, "member_information": member_information
            })
        else:
            return HttpResponseRedirect('/statistics/')



    show_schedule_resolved_problem = MPC_problem_sch.objects.filter(
        project_id=project_id, schedule_id=show_schedule_id, pp_state='已解决')
    show_schedule_unresolved_problem = MPC_problem_sch.objects.filter(
        project_id=project_id, schedule_id=show_schedule_id).exclude(pp_state='已解决')
    show_schedule = MPC_Schedule_pd.objects.get(project_id=project_id, schedule_id=show_schedule_id)

    limit = 4
    # 数据分页
    my_problem_pages = Paginator(show_schedule_resolved_problem, limit)
    if my_problem_pages.num_pages <= 1:
        problem_list1 = show_schedule_resolved_problem
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
    to_my_problem_pages = Paginator(show_schedule_unresolved_problem, limit)
    if to_my_problem_pages.num_pages <= 1:
        problem_list2 = show_schedule_unresolved_problem
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

    return render(request, 'statistics/all_show.html', {
        "resolved_problem": show_schedule_resolved_problem, "unresolved_problem": show_schedule_unresolved_problem,
        "member_information": member_information, "problem_level": problem_level,
        "communication_information": end_communication_information,
        "all_schedule": all_schedule, "data1": data1, "show_schedule": show_schedule, "data2": data2,
        "jsondata": json.dumps(jsondata)
    })
