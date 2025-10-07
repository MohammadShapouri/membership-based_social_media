from django.db import models
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
from useraccountsubscription.models import Subscription
from post.models import Post
# Create your models here.

class Plan(models.Model):
    name = models.CharField(max_length=250, verbose_name="Title")
    user_account = models.ForeignKey("useraccount.UserAccount", on_delete=models.CASCADE, related_name="plans", verbose_name="User Account")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    discount_percent = models.PositiveIntegerField(blank=True, null=True, verbose_name="Discount percent")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    update_date = models.DateTimeField(auto_now=True, verbose_name="Update date")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(discount_percent__isnull=True) | (Q(discount_percent__gte=0) & Q(discount_percent__lte=100)),
                name="discount_percent_range_constraint",
                # Only in Django 5.0+
                violation_error_message="Discount percent can not be greater than 100.00 or less than 0.00"
            )
        ]

    @property
    def effective_price(self) -> Decimal:
        output: Decimal = Decimal(self.price) or Decimal("0")
        if self.discount_percent is not None:
            output = max(Decimal("0.00"), Decimal(self.price)-((Decimal(self.price)*Decimal(self.discount_percent))/Decimal("100")))
        return output.quantize(Decimal("0.01"))

    @property
    def subscribers_count(self):
        now = timezone.now()
        return Subscription.objects.filter(Q(plan=self) & Q(start_date__lte=now) & Q(end_date__gte=now)).count() or 0

    @property
    def posts_count(self):
        return Post.objects.filter(Q(plan=self)).count() or 0
