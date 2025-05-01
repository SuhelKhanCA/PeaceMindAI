from django.db import models
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# 1. Chat History Table
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField(null=False)
    response = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - User: {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# 2. Feedback Table
class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - {self.user.username} - {self.rating}⭐"


# 3. Mental Health Resources Table
class Resource(models.Model):
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('exercise', 'Exercise'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=255)
    type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.type})"
