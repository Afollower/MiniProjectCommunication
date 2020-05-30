from django.db import models

# Create your models here.


# 项目：问题  项目ID对应项目组，且可根据项目ID显示问题
class MPC_problem_sch(models.Model):
    pp_id = models.CharField(verbose_name="问题ID", max_length=32)
    pp_title = models.CharField(verbose_name="标题", max_length=32)
    pp_author = models.CharField(verbose_name="作者", max_length=32)
    pp_information = models.CharField(verbose_name="问题详情", max_length=255)
    pp_state = models.CharField(verbose_name="问题状态", max_length=25, default="进行中")
    pp_to_user = models.CharField(verbose_name="处理者", max_length=32)
    c_time = models.DateTimeField(auto_now_add=True)
    pp_time = models.CharField(verbose_name="预计结束时间", max_length=20, default='0')
    # 引用外键 project/Project_group->获取问题级别ID【项目ID可来自系统主页正在使用的项目】
    project_id = models.CharField(verbose_name="项目ID", max_length=32)
    pl_id = models.CharField(verbose_name="问题级别ID", max_length=32)
    schedule_id = models.CharField(verbose_name="日程阶段ID", max_length=12)


    def __str__(self):
        return self.pp_id

    class Meta:
        db_table = 'MPC_problem_sch'
        ordering = ['pp_id']
        verbose_name = '项目问题'
        verbose_name_plural = '项目问题信息'


class MPC_Problem_communication_sch(models.Model):
    pp_com_id = models.CharField(verbose_name="交谈次数ID", max_length=10)
    ppc_user_id = models.CharField(verbose_name="创建者", max_length=32)
    ppc_describe = models.CharField(verbose_name="回复", max_length=255)
    ppc_time = models.DateTimeField(auto_now_add=True)
    # 引用外键
    pp_id = models.CharField(verbose_name="问题ID", max_length=32)
    project_id = models.CharField(verbose_name="项目ID", max_length=32)

    def __str__(self):
        return self.pp_id

    class Meta:
        db_table = 'MPC_Problem_complete_sch'
        ordering = ['pp_id']
        verbose_name = '问题进度'
        verbose_name_plural = '项目问题进度信息'
