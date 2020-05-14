from django.db import models

# Create your models here.


# 项目组:
class MPC_Project_group_pmd(models.Model):
    pg_id = models.CharField(verbose_name="项目组ID", max_length=32, unique=True)
    # 默认"0" 为申请状态， 其他为加入状态
    pg_name = models.CharField(verbose_name="项目组名", max_length=128)
    # 引用外键 project/Project
    project_id = models.CharField(verbose_name="项目ID", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pg_id

    class Meta:
        db_table = 'MPC_Project_group_pmd'
        ordering = ['pg_id']
        verbose_name = '项目组'
        verbose_name_plural = '项目组信息'


# 项目组成员表:
class MPC_Member_pg_pmd(models.Model):
    pg_id = models.CharField(verbose_name="项目组ID", max_length=32)
    pg_category_id = models.CharField(verbose_name="项目组成员分类ID", max_length=32)
    # 引用外键 user_admin/User
    user_id = models.CharField(verbose_name="用户ID", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pg_id

    class Meta:
        db_table = 'MPC_Member_pg_pmd'
        ordering = ['pg_id']
        verbose_name = '项目组成员'
        verbose_name_plural = '项目组成员信息'


# 组成员分类
class MPC_Category_pg_pmd(models.Model):
    pg_category_id = models.CharField(verbose_name="项目组成员分类ID", max_length=32)
    pg_category_name = models.CharField(verbose_name="项目组名", max_length=32)
    pg_category_describe = models.CharField(verbose_name="描述", max_length=128)
    # 引用外键 project_member_admin/Project_Group
    pg_id = models.CharField(verbose_name="项目组ID", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pg_category_id

    class Meta:
        db_table = 'MPC_Category_pg_pmd'
        ordering = ['pg_category_id']
        verbose_name = '项目组成员分类'
        verbose_name_plural = '项目组成员分类信息'
