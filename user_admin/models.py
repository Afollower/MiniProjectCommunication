from django.db import models

# Create your models here.


# 用户：登录注册， 以及后面项目组成员
class MPC_User_ud(models.Model):
    # 用户
    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    # 基本信息
    user_id = models.CharField(verbose_name="用户ID", max_length=32, unique=True)
    user_email = models.EmailField(verbose_name="邮箱", unique=True)
    password = models.CharField(verbose_name="密码", max_length=32)
    user_name = models.CharField(verbose_name="用户名", max_length=32)
    user_profile = models.CharField(verbose_name="个人签名", max_length=32, default='')
    user_sex = models.CharField(verbose_name="性别", max_length=32, choices=gender, default='男')
    user_company = models.CharField(verbose_name="单位", max_length=128)
    user_position = models.CharField(verbose_name="职位", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = 'MPC_User_ud'
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户基础信息'


# 用户状态信息
class MPC_User_state_ud(models.Model):
    user_id = models.CharField(verbose_name="用户ID", max_length=32, unique=True)
    project_id = models.CharField(verbose_name="当前项目ID", max_length=32, unique=True)
    pg_uc_id = models.CharField("用户等级", max_length=32)

    def __str__(self):
        return self.user_id

    class Meta:
        db_table = 'MPC_User_state_ud'
        verbose_name = '用户状态记录'
        verbose_name_plural = '用户状态信息'
