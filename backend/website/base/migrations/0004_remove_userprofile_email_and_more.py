# Generated by Django 4.2.7 on 2023-11-24 18:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("base", "0003_userprofile_groups_userprofile_is_active_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="email",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="groups",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="is_staff",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="last_login",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="last_name",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="password",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="permissions",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="user_permissions",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="user_type",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="username",
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("username", models.CharField(max_length=100, unique=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "user_type",
                    models.CharField(
                        choices=[
                            ("normal", "Normal"),
                            ("author", "Author"),
                            ("admin", "Admin"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        related_name="custom_user_groups", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        related_name="custom_user_permissions", to="auth.permission"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="authorprofile",
            name="banned_users",
            field=models.ManyToManyField(
                blank=True, related_name="iam_banned_by_authors", to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="authorprofile",
            name="followers",
            field=models.ManyToManyField(
                blank=True, related_name="user_following_authors", to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="authorprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="readinghistory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="friends",
            field=models.ManyToManyField(
                blank=True, related_name="user_friends", to="base.customuser"
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="base.customuser"
            ),
        ),
    ]
