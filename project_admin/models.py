from django.db import models

# Create your models here.


# 创建项目
class MPC_Project_pd(models.Model):
    project_id = models.CharField(verbose_name="项目ID", max_length=32, unique=True)
    project_creator_id = models.CharField(verbose_name="负责人", max_length=32)
    project_name = models.CharField(verbose_name="项目名称", max_length=128)
    project_code = models.CharField(verbose_name="邀请码", max_length=32)
    project_td = models.CharField(verbose_name="项目说明", max_length=255)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_id

    class Meta:
        db_table ='MPC_Project_pd'
        ordering = ['project_id']
        verbose_name = '项目'
        verbose_name_plural = '项目基础信息'


# 对应问题等级设定
class MPC_Level_pj_pd(models.Model):
    pl_id = models.CharField(verbose_name="问题级别ID", max_length=32)
    pl_name = models.CharField(verbose_name="问题级别名称", max_length=128)
    pl_describe = models.CharField(verbose_name="问题级别描述", max_length=255)
    pl_color = models.CharField(verbose_name="问题色别", max_length=2)
    # 引用外键project_admin/Project
    project_id = models.CharField(verbose_name="项目ID", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pl_id

    class Meta:
        db_table = 'MPC_Level_pj_pd'
        ordering = ['pl_id']
        verbose_name = '问题级别'
        verbose_name_plural = '问题级别信息'


# 项目日程表
class MPC_Schedule_pd(models.Model):
    project_id = models.CharField(verbose_name="项目ID", max_length=32)
    schedule_id = models.CharField(verbose_name="日程阶段", max_length=12)
    schedule_name = models.CharField(verbose_name="阶段名称", max_length=64)
    start_time = models.CharField(verbose_name="阶段开始时间", max_length=12)
    end_time = models.CharField(verbose_name="阶段结束时间", max_length=12)
    schedule_td = models.CharField(verbose_name="阶段事项", max_length=255)
    schedule_speed = models.CharField(verbose_name="阶段完成度", max_length=12, default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_id

    class Meta:
        db_table ='MPC_Schedule_pd'
        ordering = ['project_id']
        verbose_name = '项目日程'
        verbose_name_plural = '项目日程信息'
