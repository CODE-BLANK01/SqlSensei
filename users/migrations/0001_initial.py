# Generated by Django 4.2.20 on 2025-04-11 09:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('username', models.EmailField(max_length=255, unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='active', max_length=50)),
                ('role', models.CharField(choices=[('Instructor', 'Instructor'), ('Student', 'Student')], max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'Users',
            },
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'EmailVerificationCodes',
            },
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('instructor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('about_me', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'Instructors',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('grade_level', models.CharField(choices=[('UnderGraduate', 'UnderGraduate'), ('Graduate', 'Graduate')], max_length=50)),
                ('last_active_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Students',
            },
        ),
    ]
