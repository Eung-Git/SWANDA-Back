

from rest_framework import serializers
from .models import Question, Answer, Reply

class QuestionSerializer(serializers.ModelSerializer):
    answer_ids = serializers.SerializerMethodField()
    has_accepted_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'answer_ids', 'has_accepted_answer']

    def get_answer_ids(self, obj):
        # 해당 질문에 연결된 모든 답변의 고유 ID 목록 반환
        return list(obj.answers.values_list('id', flat=True))

    def get_has_accepted_answer(self, obj):
        # 해당 질문에 채택된 답변이 있는지 여부 확인
        return obj.answers.filter(is_adopted=True).exists()

class AnswerSerializer(serializers.ModelSerializer):
    reply_ids = serializers.SerializerMethodField()
    is_accepted = serializers.BooleanField(source='is_adopted', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'question','sequence_id', 'content', 'created_at', 'updated_at', 'reply_ids', 'is_accepted']

    def get_reply_ids(self, obj):
        # 해당 답변에 연결된 모든 대댓글의 ID 목록 반환
        return list(obj.replies.values_list('id', flat=True))



class ReplySerializer(serializers.ModelSerializer):
    question = serializers.IntegerField(source='answer.question.id', read_only=True)
    class Meta:
        model = Reply
        fields = ['id','question','answer', 'reply_sequence_id', 'content', 'created_at', 'updated_at']