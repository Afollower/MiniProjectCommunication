from django.contrib import admin
from .models import MPC_problem_sch, MPC_Problem_communication_sch

# Register your models here.


class problemAdmin(admin.ModelAdmin):
    search_fields = ('pp_id', 'pp_name', 'project_id')
    list_display = ('project_id', 'pp_id', 'pp_title')


class ppcAdmin(admin.ModelAdmin):
    search_fields = ('project_id', 'pp_id', 'pp_com_id')
    list_display = ('project_id', 'pp_id', 'pp_com_id', 'ppc_describe')


admin.site.register(MPC_problem_sch, problemAdmin)
admin.site.register(MPC_Problem_communication_sch, ppcAdmin)
