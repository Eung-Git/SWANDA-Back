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


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)
    # likes = models.ManyToManyField() // 추후 유저 추가한 뒤
    is_adopted = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question.title} at {self.created_at}"

class AnswersAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=800)
    # likes = models.ManyToManyField() // 추후 유저 추가한 뒤

    def __str__(self):
        return f"Reply to {self.answer.id} at {self.created_at}"