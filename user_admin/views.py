from django.shortcuts import render, redirect
from django.db.models import Q
from .models import MPC_User_ud, MPC_User_state_ud
from project_admin.models import MPC_Project_pd
from project_member_admin.models import MPC_Member_pg_pmd
# Create your views here.


# 用户名登录
def login(request):
    # 不允许重复登录
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == "POST":
        # login_form = UserForm(request.POST)
        user_id = request.POST['user_id']
        password = request.POST['password']
        agree = request.POST.get('agree')

        if agree:
            print(agree)
        else:
            print("没勾选，不保存")
        message = "请检查填写的内容！"
        if user_id and password:
            try:
                user = MPC_User_ud.objects.get(user_id=user_id)
                if user.password == password:
                    # 往session字典内写入用户状态和数据
                    request.session['is_login'] = True
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.user_name
                    request.session['user_company'] = user.user_company
                    request.session['user_position'] = user.user_position
                    try:
                        user_state = MPC_User_state_ud.objects.get(user_id=user.user_id)
                        request.session['now_project_id'] = user_state.project_id
                        request.session['now_project_uc_id'] = user_state.pg_category_id
                        try:
                            pj = MPC_Project_pd.objects.get(project_id=user_state.project_id)
                            request.session['now_project_name'] = pj.project_name
                        except:
                            request.session['now_project_name'] = "尚未参加任何项目"
                    except:
                        message = 'MySQLdb error: MPC_user_state_ud lose user information'
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())
    return render(request, 'login/login.html', locals())


# 邮箱登录
def login_email(request):
    # 不允许重复登录
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == "POST":
        # login_form = UserForm(request.POST)
        user_email = request.POST['email']
        password = request.POST['password']
        agree = request.POST.get('agree')

        if agree:
            print(agree)
        else:
            print("没勾选，不保存")  # 后面实现保持账户密码功能
        message = "请检查填写的内容！"
        if user_email and password:
            try:
                user = MPC_User_ud.objects.get(email=user_email)
                print(user.user_name)
                if user.password == password:
                    # 往session字典内写入用户状态和数据
                    request.session['is_login'] = True
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.user_name
                    request.session['user_company'] = user.user_company
                    request.session['user_position'] = user.user_position
                    try:
                        user_state = MPC_User_state_ud.objects.get(user_id=user.user_id)
                        request.session['now_project_id'] = user_state.project_id
                        request.session['now_project_uc_id'] = user_state.pg_category_id
                        try:
                            pj = MPC_Project_pd.objects.get(project_id=user_state.project_id)
                            request.session['now_project_name'] = pj.project_name
                        except:
                            request.session['now_project_name'] = "尚未参加任何项目"
                    except:
                        message = 'MySQLdb error: MPC_user_state_ud lose user information'

                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "邮箱未注册！"
        return render(request, 'login/login_email.html', locals())
    return render(request, 'login/login_email.html', locals())


# 登出
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/user/login/")
    user_id = request.session.get('user_id', None)
    pg_uc = request.session.get('now_project_uc_id', None)
    now_project_id = request.session.get('now_project_id', None)
    try:
        user_state = MPC_User_state_ud.objects.get(user_id=user_id)
        if now_project_id != '':
            user_state.project_id = now_project_id
            user_state.pg_category_id = pg_uc
            # else:
            #     try:
            #         pg_member = MPC_member_pg_pmd.objects.get(pg_id=now_project_id, user_id=user_id)
            #         user_state.pg_category_id = pg_member.pg_category_id
            #     except:
            #         message = 'MySQLdb error: MPC_member_pg_pmd lose user information'
            user_state.save()
    except:
        message = 'MySQLdb error: MPC_user_state_ud lose user information'
    request.session.flush()     # 清除
    return redirect("/user/login/")


# 注册
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。
        return redirect("/index/")
    if request.method == "POST":
        user_id = request.POST['user_id']
        user_email = request.POST['user_email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_name = request.POST['user_name']
        user_sex = request.POST['user_sex']
        user_company = request.POST['user_company']
        user_position = request.POST['user_position']
        message = "请检查填写的内容！"
        if user_id and user_email and password1:  # 判断是否为空
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_id = MPC_User_ud.objects.filter(user_name=user_name)
                if same_name_id:  # 用户名唯一
                    message = '账户已经存在！'
                    return render(request, 'login/register.html', locals())
                same_email = MPC_User_ud.objects.filter(user_email=user_email)
                if same_email:  # 邮箱地址唯一
                    message = '该邮箱已注册！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                # 创建用户表
                new_user = MPC_User_ud.objects.create()
                # 账户/邮箱 及 密码
                new_user.user_id = user_id
                new_user.user_email = user_email
                new_user.password = password1
                # 基础信息 ： 姓名 性别 单位 职位
                new_user.user_name = user_name
                new_user.user_sex = user_sex
                new_user.user_company = user_company
                new_user.user_position = user_position
                new_user.save()

                # 创建状态表
                new_user_state = MPC_User_state_ud.objects.create()
                new_user_state.user_id = user_id
                new_user_state.project_id = ''
                new_user_state.pg_category_id = '-1'
                new_user_state.save()
                return redirect('/user/login/')  # 自动跳转到登录页面
    return render(request, 'login/register.html', locals())


# 个人信息
def show_information(request):
    user_id = request.session.get('user_id', None)
    if request.method == "POST":
        user_email = request.POST['user_email']
        user_name = request.POST['user_name']
        user_sex = request.POST['user_sex']
        user_company = request.POST['user_company']
        user_position = request.POST['user_position']
        user_profile = request.POST['user_profile']
        user = MPC_User_ud.objects.get(user_id=user_id)
        user.user_email = user_email
        user.user_name = user_name
        user.user_sex = user_sex
        user.user_company = user_company
        user.user_position = user_position
        user.user_profile = user_profile
        user.save()
        message = '修改成功！'
        return render(request, 'index/index.html', locals())
    now_user = MPC_User_ud.objects.get(user_id=user_id)
    return render(request, 'user/information.html', {"user": now_user})


# 修改密码
def change_password(request):
    if request.method == "POST":
        old_password = request.POST['old_password']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_id = request.session.get('user_id', None)
        user = MPC_User_ud.objects.get(user_id=user_id)
        if user.password == old_password:
            if password1 == password2:
                user.password = password1
                user.save()
                message = '密码修改成功！'
                return redirect('/index/')
            else:
                message = '请确认新密码是否输入出错！'
        else:
            message = '请输入正确的旧密码！'
            return render(request, 'user/change_password.html', locals())
    return render(request, 'user/change_password.html')
