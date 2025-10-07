from django.db import models
from django.conf import settings
from django.utils import timezone

class FollowingFollower(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following_set',
        on_delete=models.CASCADE,
        verbose_name="Follower"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower_set',
        on_delete=models.CASCADE,
        verbose_name="Following"
    )
    is_accepted    = models.BooleanField(default=False, verbose_name="Is request accepted?")
    acception_date = models.DateTimeField(blank=True, null=True, verbose_name="Acception Date")
    creation_date  = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending"
        return f"{self.follower} -> {self.following} ({status})"



class BlockList(models.Model):
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocked_set',
        on_delete=models.CASCADE,
        verbose_name="Blocker"
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocker_set',
        on_delete=models.CASCADE,
        verbose_name="Blocked"
    )
    creation_date  = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
