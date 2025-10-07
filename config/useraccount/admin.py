from django.contrib import admin
from .models import UserAccount
from django.contrib.admin import ModelAdmin
# Register your models here.

class UserAccountAdmin(ModelAdmin):
    list_display = ('full_name', 'username', 'email', 'is_account_verified', 'creation_date', 'update_date')
    list_filter = ('is_account_verified', 'creation_date', 'update_date')
    search_fields = ('full_name', 'username', 'email')

admin.site.register(UserAccount, UserAccountAdmin)
