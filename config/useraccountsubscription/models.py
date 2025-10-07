from django.db import models
from django.utils import timezone
import uuid

class Subscription(models.Model):
    user_account = models.ForeignKey(
        "useraccount.UserAccount", 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="subscription_user",
        verbose_name="User"
    )
    plan = models.ForeignKey(
        "plan.Plan", 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="subscription_plan",
        verbose_name="Plan"
    )

    # Subscription info
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")  # 30 days after start
    is_subscription_active = models.BooleanField(default=False, verbose_name="Is Active")

    # Payment info (for crypto)
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Payment ID")
    payment_method = models.CharField(
        max_length=50, 
        choices=[("crypto", "Crypto"), ("fiat", "Fiat")],
        default="crypto",
        verbose_name="Payment Method"
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount Paid")
    currency = models.CharField(max_length=10, default="USD", verbose_name="Currency")
    payment_status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending",
        verbose_name="Payment Status"
    )

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    update_date = models.DateTimeField(auto_now=True, verbose_name="Update Date")

    class Meta:
        unique_together = ("user_account", "plan", "start_date")  # prevent duplicate subscriptions for same period
        ordering = ["-start_date"]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def save(self, *args, **kwargs):
        # Automatically set end_date to 30 days after start_date if not set
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_account.username} -> {self.plan.name} ({self.start_date.date()} - {self.end_date.date()})"

    def is_expired(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
