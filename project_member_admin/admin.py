from django.contrib import admin
from .models import MPC_Category_pg_pmd, MPC_Member_pg_pmd, MPC_Project_group_pmd
# Register your models here.


admin.site.register(MPC_Project_group_pmd)
admin.site.register(MPC_Member_pg_pmd)
admin.site.register(MPC_Category_pg_pmd)
