from django.db import models
from django.conf import settings
from courses.models import Course


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_popup = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.receiver or 'All'} on {self.date_sent}"


class ChatGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Group: {self.group_name} ({self.course})"
