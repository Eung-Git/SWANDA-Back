from django.db import models
from datetime import *

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    # likes = models.ManyToManyField() // 추후 유저 추가한 뒤
    adopt = models.BooleanField(default=False)
    scrap = models.IntegerField(default=0)
    file = models.FileField(upload_to='Questionfile/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} at {self.created_at}"