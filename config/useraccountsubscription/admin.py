from django.contrib import admin
from .models import Subscription
# Register your models here.

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_account', 'plan', 'start_date', 'end_date', 'is_subscription_active', 'payment_method', 'amount_paid', 'currency', 'creation_date')
    list_filter = ('creation_date', 'is_subscription_active')
    search_fields = ('user_account__username', 'user_account__email', 'plan__title')
    ordering = ('-creation_date',)


admin.site.register(Subscription, SubscriptionAdmin)
