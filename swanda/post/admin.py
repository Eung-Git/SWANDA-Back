from django.contrib import admin
from .models import *

admin.site.register(Post)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'created_at', 'updated_at', 'has_accepted_answer')
    exclude = ('answer_ids',)  # 관리자 페이지에서 숨김
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'sequence_id', 'is_adopted', 'created_at', 'updated_at')
    exclude = ('reply_ids',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'reply_sequence_id', 'content', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


