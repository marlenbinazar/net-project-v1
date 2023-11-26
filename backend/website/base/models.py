from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.contrib.auth.password_validation import get_default_password_validators
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.utils import timezone
from django.utils.text import slugify


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        UnicodeUsernameValidator()(username)

        for validator in get_default_password_validators():
            validator.validate(password)

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        profile = UserProfile.objects.create(user=user)
        profile.first_name = user.first_name
        profile.last_name = user.last_name
        profile.username = user.username
        profile.email = user.email
        profile.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(email, username, password, **extra_fields)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions"
    )
    user_type = models.CharField(
        max_length=20,
        choices=[("normal", "Normal"), ("author", "Author"), ("admin", "Admin")],
    )
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    profile_info = models.TextField(null=True, blank=True)
    following_authors = models.ManyToManyField(
        "AuthorProfile", related_name="author_followers", blank=True
    )
    friends = models.ManyToManyField(
        CustomUser, related_name="user_friends", blank=True
    )
    banned_by_authors = models.ManyToManyField(
        "AuthorProfile", related_name="author_banned_users", blank=True
    )


class AuthorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    profile_info = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField(
        CustomUser, related_name="user_following_authors", blank=True
    )
    cooperated_authors = models.ManyToManyField("self", blank=True)
    social_links = models.URLField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    banned_users = models.ManyToManyField(
        CustomUser, related_name="iam_banned_by_authors", blank=True
    )


class Content(models.Model):
    content_type = models.CharField(
        max_length=20,
        choices=[
            ("book", "Book"),
            ("manga", "Manga"),
            ("comic", "Comic"),
            ("ranobe", "Ranobe"),
        ],
    )
    created_by = models.ForeignKey(AuthorProfile, on_delete=models.CASCADE)
    chapters = models.ManyToManyField(
        "Chapter", blank=True, related_name="content_chapters"
    )
    original_author = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    date_of_publish = models.DateField()
    publish_status = models.CharField(
        max_length=20,
        choices=[
            ("ongoing", "Ongoing"),
            ("stopped", "Stopped"),
            ("announced", "Announced"),
            ("finished", "Finished"),
            ("paused", "Paused"),
        ],
    )
    comments = models.ManyToManyField(
        "Comment", blank=True, related_name="content_comments"
    )
    overall_rating = models.FloatField(default=0.0)
    genre = models.CharField(max_length=50)

    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_reading_now = models.BooleanField(default=False)
    last_updated = models.DateField()
    author_recommendation = models.TextField(null=True, blank=True)
    is_recommended = models.BooleanField(default=False)
    week_top = models.BooleanField(default=False)

    slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        # Auto-generate a slug when saving the object
        self.slug = slugify(self.original_name)
        super().save(*args, **kwargs)


class Chapter(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    chapter_number = models.IntegerField()
    volume_number = models.IntegerField()
    pages = models.ManyToManyField("Page", blank=True)
    date_of_publish = models.DateField()
    title = models.CharField(max_length=255)

    chapter_type = models.CharField(
        max_length=20,
        choices=[
            ("prologue", "Prologue"),
            ("epilogue", "Epilogue"),
            ("normal", "Normal"),
            ("one-shot", "One-shot"),
        ],
        default="normal",
    )

    def __str__(self):
        return self.title


class Page(models.Model):
    image = models.ImageField(upload_to="content_pages/")
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering"]


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    text = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    is_spoiler = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("denied", "Denied"),
        ],
    )
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Set the created_at field to the current timestamp when saving the object
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(
        max_length=20, choices=[("unread", "Unread"), ("read", "Read")]
    )
    created_at = models.DateTimeField(default=timezone.now)


class ReadingHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    last_read_chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True
    )
    last_read_page = models.ForeignKey(
        Page, on_delete=models.CASCADE, null=True, blank=True
    )
