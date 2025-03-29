from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('full_name', 'role', 'status', 'about_me', 'average_feedback', 'grade_level', 'last_active_date')}),
    )

admin.site.register(User, CustomUserAdmin)
