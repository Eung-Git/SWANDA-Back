from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=Answer)
def update_question_on_answer_change(sender, instance, **kwargs):
    """답변이 추가/수정될 때 질문의 필드를 업데이트"""
    instance.question.update_answer_info()

@receiver(post_save, sender=Reply)
@receiver(post_delete, sender=Reply)
def update_answer_on_reply_change(sender, instance, **kwargs):
    """답변이 추가되거나 삭제될 때 Answer 모델의 reply_ids 업데이트"""
    instance.answer.update_reply_info()