from django.db import models
from django.apps import apps
from unidecode import unidecode
from django.utils import timezone
from django.template import defaultfilters
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from extentions.validators.ASCII_username_validator import ASCIIUsernameValidator
# Create your models here.



class CustomUserManager(BaseUserManager):
    def _create_user(self, full_name, username, email, password, **extra_fields):
        """
        Create and save a user with the given full name, username, email, and password.
        """
        if not full_name:
            raise ValueError("The given full name must be set")
        if not username:
            raise ValueError("The given username must be set")
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(full_name=full_name, username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    

    def create_user(self, full_name, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(full_name, username, email, password, **extra_fields)
    

    def create_superuser(self, full_name, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_account_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(full_name, username, email, password, **extra_fields)



def define_profile_picture_directory(instance, filename):
    file_date_time = timezone.now().strftime('%Y%m%d%h%m%s')
    slug = defaultfilters.slugify(unidecode(instance.username))
    return "images/profile_picture/{0}/{1}_{2}".format(slug, file_date_time, filename)

def define_background_picture_directory(instance, filename):
    file_date_time = timezone.now().strftime('%Y%m%d%h%m%s')
    slug = defaultfilters.slugify(unidecode(instance.username))
    return "images/backgound_picture/{0}/{1}_{2}".format(slug, file_date_time, filename)


class UserAccount(AbstractUser):
    first_name              = None
    last_name               = None
    full_name               = models.CharField(max_length=50, verbose_name='Name', blank=False, null=False)
    username                = models.CharField(max_length=50, verbose_name='Username', blank=False, null=False, unique=True, validators=[ASCIIUsernameValidator])
    email                   = models.EmailField(unique=True, blank=False, null=False, verbose_name='Email')
    new_email               = models.EmailField(unique=True, blank=True, null=True, verbose_name='New Email')
    is_account_verified     = models.BooleanField(default=False, verbose_name='Is Account Verified?')
    is_new_email_verified   = models.BooleanField(default=True, verbose_name='Is New Email Verified?')
    otp_object              = models.ForeignKey('otp.OTPCode', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='OTP Code Object')
    profile_picture         = models.ImageField(upload_to=define_profile_picture_directory, blank=True, null=True, verbose_name='Profile Picture')
    background_picture      = models.ImageField(upload_to=define_background_picture_directory, blank=True, null=True, verbose_name='Background Picture')
    is_private              = models.BooleanField(default=False, verbose_name="Is Account Private?")
    following               = models.ManyToManyField("self", related_name="follower", through="useraccountconnection.FollowingFollower")
    blocking                = models.ManyToManyField("self", related_name="blocked_by", through="useraccountconnection.BlockList")
    subscriptions           = models.ManyToManyField("plan.Plan", through='useraccountsubscription.Subscription', related_name='subscribed_users')
    creation_date           = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    update_date             = models.DateTimeField(auto_now=True, verbose_name='Update Date')


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name', 'email']

    objects = CustomUserManager()

    class Meta:
        db_table = 'useraccount'
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'


    def __str__(self):
        return str(self.username)
