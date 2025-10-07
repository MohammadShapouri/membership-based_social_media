from django.contrib import admin
from .models import Plan
# Register your models here.

class PlanAdmin(admin.ModelAdmin):
    list_display = ('user_account', 'name', 'price', 'discount_percent', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('user_account__username', 'user_account__email', 'name')
    ordering = ('-creation_date',)


admin.site.register(Plan, PlanAdmin)
