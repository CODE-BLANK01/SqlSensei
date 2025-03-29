from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, full_name, password=None, role='Student', status='active'):
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(
            username=self.normalize_email(username),
            full_name=full_name,
            role=role,
            status=status,
            is_active=True
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, full_name, password):
        user = self.create_user(username, full_name, password, role='Instructor')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    user_id = models.BigAutoField(primary_key=True)
    username = models.EmailField(unique=True, max_length=255)  # becomes the login field
    full_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="active")
    role = models.CharField(max_length=50, choices=[('Instructor', 'Instructor'), ('Student', 'Student')])

    # Optional: if you don't want username+email confusion
    first_name = None
    last_name = None
    email = None

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    class Meta:
        db_table = 'Users'


class Instructor(models.Model):
    instructor = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    about_me = models.TextField(blank=True)

    class Meta:
        db_table = 'Instructors'


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    grade_level = models.CharField(
        max_length=50,
        choices=[('UnderGraduate', 'UnderGraduate'), ('Graduate', 'Graduate')]
    )
    last_active_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Students'
