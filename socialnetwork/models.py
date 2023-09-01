from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Comment(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="commenter")
    time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'id={self.id}, text="{self.text}"'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    userID = models.IntegerField()
    username = models.CharField(blank=True, max_length=200)
    email = models.CharField(blank=True, max_length=200)
    first_name = models.CharField(blank=True, max_length=200)
    last_name = models.CharField(blank=True, max_length=200)
    
    bio = models.CharField(max_length=200, default='')
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    followed_users = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    
    def __str__(self):
        return f'id={self.id}'

class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="poster")
    time = models.DateTimeField(default=timezone.now)
    user_profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="posterprofile")

    related_comments = models.ManyToManyField(Comment, related_name='comment')

    def __str__(self):
        return f'id={self.id}, text="{self.text}"'