from django.db import models
from datetime import *

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    # likes = models.ManyToManyField() // 추후 유저 추가한 뒤
    has_accepted_answer = models.BooleanField(default=False)
    answer_ids = models.JSONField(default=[])
    scrap = models.IntegerField(default=0)
    file = models.FileField(upload_to='Questionfile/', null=True, blank=True)

    def update_answer_info(self):
        """답변 정보를 갱신하는 메서드"""
        self.answer_ids = list(self.answers.values_list('id', flat=True))
        self.has_accepted_answer = self.answers.filter(is_adopted=True).exists()
        self.save()




class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    sequence_id = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(max_length=1000)
    # likes = models.ManyToManyField() // 추후 유저 추가한 뒤
    is_adopted = models.BooleanField(default=False)
    reply_ids = models.JSONField(default=[])

    def update_reply_info(self):
        """대댓글 정보를 업데이트하는 메서드"""
        self.reply_ids = list(self.replies.values_list('id', flat=True))
        self.save()
    class Meta:
        unique_together = ('question_id', 'sequence_id')  # 질문 내에서 고유 ID 보장

    def save(self, *args, **kwargs):
        if not self.sequence_id:
            last_answer = Answer.objects.filter(question=self.question).order_by('sequence_id').last()
            self.sequence_id = last_answer.sequence_id + 1 if last_answer else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to {self.question.title} with sequence {self.sequence_id}"


class Reply(models.Model):
    id = models.AutoField(primary_key=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='replies')
    reply_sequence_id = models.PositiveIntegerField(editable=False)  # 답변별 고유 ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(max_length=800)
    question_id = models.PositiveIntegerField(default=1, blank=True)

    def save(self, *args, **kwargs):
        """저장 시 관련 질문 ID를 자동 업데이트"""
        self.question_id = self.answer.question.id
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('answer', 'reply_sequence_id')  # 답변 내에서 고유 ID 보장

    def save(self, *args, **kwargs):
        if not self.reply_sequence_id:
            last_reply = Reply.objects.filter(answer=self.answer).order_by('reply_sequence_id').last()
            self.reply_sequence_id = last_reply.sequence_id + 1 if last_reply else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reply to answer {self.reply_sequence_id} with sequence {self.reply_sequence_id}"