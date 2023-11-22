from django.contrib.auth.models import BaseUserManager, User
from django.contrib.auth.password_validation import get_default_password_validators
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from firebase_admin import auth, db


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
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        UnicodeUsernameValidator()(username)

        for validator in get_default_password_validators():
            validator.validate(password)

        return self.create_user(email, username, password, **extra_fields)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=[("normal", "Normal"), ("author", "Author"), ("admin", "Admin")],
    )
    permissions = models.TextField()
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    profile_info = models.TextField(null=True, blank=True)
    following_authors = models.ManyToManyField(
        "AuthorProfile", related_name="author_followers", blank=True
    )
    friends = models.ManyToManyField(User, related_name="friends", blank=True)
    banned_by_authors = models.ManyToManyField(
        "AuthorProfile", related_name="author_banned_users", blank=True
    )

    objects = CustomUserManager()

    def set_password(self, raw_password):
        # Implement your custom password validation here before setting the password
        # You can use Django's built-in validators or add your own logic
        # Example: validate_password(raw_password)
        for validator in get_default_password_validators():
            validator.validate(raw_password)
        super().set_password(raw_password)

    def change_password(self, new_password):
        # Implement logic to change user's password
        self.set_password(new_password)
        self.save()

    def reset_password(self):
        # Implement logic for password reset through email recovery
        # You may use Django's built-in password reset functionality
        pass

    @receiver(post_save, sender=User)
    def sync_user_data_to_firebase(sender, instance, created, **kwargs):
        if created:
            # Create a new Firebase user and update their data
            firebase_user = auth.create_user(instance.email, instance.password)
            uid = firebase_user.uid

            # Update user data in Firebase
            db.ref(f"users/{uid}").set(
                {
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "username": instance.username,
                    "email": instance.email,
                }
            )


@receiver(post_save, sender=UserProfile)
def update_author_profile_in_firebase(sender, instance, **kwargs):
    if instance.user_type == "author":
        # Update author profile data in Firebase
        db.ref(f"authors/{instance.user.id}").set(
            {
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "profile_picture": instance.profile_picture.url
                if instance.profile_picture
                else None,
                "profile_info": instance.profile_info,
                "social_links": instance.social_links,
                "is_verified": instance.is_verified,
            }
        )


@receiver(post_save, sender=UserProfile)
def sync_user_profile_updates_to_firebase(sender, instance, **kwargs):
    # Update user data in Firebase
    db.ref(f"users/{instance.user.id}").update(
        {
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "username": instance.username,
            "email": instance.email,
        }
    )


@receiver(post_delete, sender=UserProfile)
def delete_user_data_from_firebase(sender, instance, **kwargs):
    # Delete the corresponding Firebase user
    uid = instance.id
    if uid:
        auth.delete_user(uid)


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    profile_info = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField(
        User, related_name="user_following_authors", blank=True
    )
    cooperated_authors = models.ManyToManyField("self", blank=True)
    social_links = models.URLField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    banned_users = models.ManyToManyField(
        User, related_name="iam_banned_by_authors", blank=True
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(
        max_length=20, choices=[("unread", "Unread"), ("read", "Read")]
    )
    created_at = models.DateTimeField(default=timezone.now)


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    last_read_chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True
    )
    last_read_page = models.ForeignKey(
        Page, on_delete=models.CASCADE, null=True, blank=True
    )
