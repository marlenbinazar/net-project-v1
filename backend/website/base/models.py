from django.contrib.auth.models import BaseUserManager, User
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
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
        "AuthorProfile", related_name="followers", blank=True
    )
    friends = models.ManyToManyField(User, related_name="friends", blank=True)
    banned_from_authors = models.ManyToManyField(
        "AuthorProfile", related_name="banned_users", blank=True
    )

    objects = CustomUserManager()

    def set_password(self, raw_password):
        # Implement your custom password validation here before setting the password
        # You can use Django's built-in validators or add your own logic
        # Example: validate_password(raw_password)
        super().set_password(raw_password)

    def change_password(self, new_password):
        # Implement logic to change user's password
        self.set_password(new_password)
        self.save()

    def reset_password(self):
        # Implement logic for password reset through email recovery
        # You may use Django's built-in password reset functionality
        pass


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    profile_info = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField(
        User, related_name="following_authors", blank=True
    )
    cooperated_authors = models.ManyToManyField("self", blank=True)
    social_links = models.URLField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    banned_users = models.ManyToManyField(
        User, related_name="banned_by_authors", blank=True
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
    chapters = models.ManyToManyField("Chapter", blank=True)
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
    comments = models.ManyToManyField("Comment", blank=True)
    overall_rating = models.FloatField(default=0.0)
    genre = models.CharField(max_length=50)
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_reading_now = models.BooleanField(default=False)
    last_updated = models.DateField()
    author_recommendation = models.TextField(null=True, blank=True)
    is_recommended = models.BooleanField(default=False)
    week_top = models.BooleanField(default=False)


class Chapter(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    chapter_number = models.IntegerField()
    volume_number = models.IntegerField()
    pages = models.ManyToManyField("Page", blank=True)
    date_of_publish = models.DateField()


class Page(models.Model):
    image = models.ImageField(upload_to="content_pages/")


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


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(
        max_length=20, choices=[("unread", "Unread"), ("read", "Read")]
    )


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    last_read_chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, null=True, blank=True
    )
    last_read_page = models.ForeignKey(
        Page, on_delete=models.CASCADE, null=True, blank=True
    )
