from django.contrib import admin
from .models import MPC_Level_pj_pd, MPC_Project_pd, MPC_Schedule_pd
# Register your models here.


class projectAdmin(admin.ModelAdmin):
    search_fields = ('project_id', 'project_name')
    list_display = ('project_id', 'project_name', 'project_td')


class plAdmin(admin.ModelAdmin):
    search_fields = ('pl_name', 'project_id')
    list_display = ('project_id', 'pl_id', 'pl_name', 'pl_describe')


class scheduleAdmin(admin.ModelAdmin):
    search_fields = ('project_id', 'schedule_name')
    list_display = ('project_id', 'schedule_id', 'schedule_name')


admin.site.register(MPC_Project_pd, projectAdmin)
admin.site.register(MPC_Level_pj_pd, plAdmin)
admin.site.register(MPC_Schedule_pd, scheduleAdmin)
