from django.db import models

# Create your models here.
class PostLike(models.Model):
    post = models.ForeignKey(
        "post.Post",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="liked_post",
        verbose_name="Post"        
    )
    user_account =  models.ForeignKey(
        "useraccount.UserAccount", 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_who_liked",
        verbose_name="User"
    )

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    update_date = models.DateTimeField(auto_now=True, verbose_name="Update Date")

    class Meta:
        unique_together = ("post", "user_account")  # prevent duplicate subscriptions for same period
        ordering = ["-creation_date"]
        verbose_name = "Like"
        verbose_name_plural = "Likes"