from django.contrib import admin
from .models import MPC_Category_pg_pmd, MPC_Member_pg_pmd, MPC_Project_group_pmd
# Register your models here.


class pgAdmin(admin.ModelAdmin):
    search_fields = ('project_id', 'pg_name')
    list_display = ('project_id', 'pg_name', 'c_time')


class memberAdmin(admin.ModelAdmin):
    search_fields = ('pg_id', 'user_id')
    list_display = ('pg_id', 'user_id', 'pg_category_id')


class categoryAdmin(admin.ModelAdmin):
    search_fields = ('pg_id', 'pg_category_id')
    list_display = ('pg_id', 'pg_category_id', 'pg_category_name', 'c_time')


admin.site.register(MPC_Project_group_pmd, pgAdmin)
admin.site.register(MPC_Member_pg_pmd, memberAdmin)
admin.site.register(MPC_Category_pg_pmd, categoryAdmin)
