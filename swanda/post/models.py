from django.db import models
from django.contrib.auth import get_user_model
from datetime import *
from django.conf import settings  # User 모델 참조
User = settings.AUTH_USER_MODEL


User = get_user_model()

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    likes = models.ManyToManyField(User, related_name='q_likes', blank=True)
    has_accepted_answer = models.BooleanField(default=False)
    answer_ids = models.JSONField(default=list, blank=True, null=True)
    scrap = models.ManyToManyField(User, related_name='scrap', blank=True)
    file = models.FileField(upload_to='Questionfile/', null=True, blank=True)

    def update_answer_info(self):
        """답변 정보를 갱신하는 메서드"""
        self.answer_ids = list(self.answers.values_list('id', flat=True))
        self.has_accepted_answer = self.answers.filter(is_adopted=True).exists()
        self.save()




class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    sequence_id = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(max_length=1000)
    is_adopted = models.BooleanField(default=False)
    reply_ids = models.JSONField(default=list, blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_answers', blank=True)
    def toggle_like(self, user):
        """좋아요를 토글하는 메서드 (추가/취소)"""
        if user in self.likes.all():
            self.likes.remove(user)
            return False  # 좋아요 취소됨
        else:
            self.likes.add(user)
            return True  # 좋아요 추가됨

    def like_count(self):
        """현재 좋아요 개수 반환"""
        return self.likes.count()
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reply')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='replies')
    reply_sequence_id = models.PositiveIntegerField(editable=False)  # 답변별 고유 ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(max_length=800)
    question_id = models.PositiveIntegerField(blank=True, null=True, editable=False)  # 필수 입력 해제

    class Meta:
        unique_together = ('answer', 'reply_sequence_id')  # 답변 내에서 고유 ID 보장

    def save(self, *args, **kwargs):
        """저장 시 관련 질문 ID 및 sequence ID 자동 설정"""
        if self.reply_sequence_id is None:  # 기존에 값이 없을 경우
            last_reply = Reply.objects.filter(answer=self.answer).order_by('reply_sequence_id').last()
            self.reply_sequence_id = (last_reply.reply_sequence_id + 1) if last_reply else 1

        if self.question_id is None:  # question_id가 없는 경우 자동 설정
            self.question_id = self.answer.question.id

        super().save(*args, **kwargs)

    @property
    def question(self):
        return self.answer.question  # answer 관계를 통해 question 접근

    def __str__(self):
        return f"Reply to answer {self.answer.id} with sequence {self.reply_sequence_id}"