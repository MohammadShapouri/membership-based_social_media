from django.db import models

# Create your models here.

class UserAccountSettings(models.Model):
    user_account                         = models.OneToOneField("useraccount.UserAccount", on_delete=models.CASCADE, related_name="settings", verbose_name="User Account")
    send_notification_email              = models.BooleanField(default=False, verbose_name="Notifying user by sending email")
    new_follower_notification            = models.BooleanField(default=False, verbose_name="Notifying new follower")
    subscription_expiration_notification = models.BooleanField(default=False, verbose_name="Notifying subscription expiration")
    creation_date                        = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    update_date                          = models.DateTimeField(auto_now=True, verbose_name="Update Date")

    class Meta:
        verbose_name = "User Account Settings"
        verbose_name_plural = "User Account Settings"

    def __str__(self):
        return str(self.user_account) + "'s Settings"
