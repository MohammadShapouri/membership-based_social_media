from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserAccount
from useraccountsettings.models import UserAccountSettings


@receiver(post_save, sender=UserAccount)
def create_useraccount_settings(sender, instance, created, **kwargs):
    if created:
        UserAccountSettings.objects.create(user_account=instance)