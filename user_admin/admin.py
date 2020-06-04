from django.contrib import admin
from .models import MPC_User_ud
# Register your models here.


class userAdmin(admin.ModelAdmin):
    search_fields = ('user_id', 'user_name', 'user_email')
    list_display = ('user_id', 'user_name', 'user_company', 'user_position', 'user_profile')


admin.site.register(MPC_User_ud, userAdmin)
