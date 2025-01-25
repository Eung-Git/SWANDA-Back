

from rest_framework import serializers
from .models import Question, Answer, Reply

class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'answer_ids', 'has_accepted_answer']
        # read_only_fields = ['answer_ids', 'has_accepted_answer']


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id', 'question','sequence_id', 'content', 'created_at', 'updated_at', 'reply_ids', 'is_adopted']
        read_only_fields = ['reply_ids', 'is_adopted']



class ReplySerializer(serializers.ModelSerializer):
    question = serializers.ReadOnlyField(source='question.id', read_only=True)
    answer_sequence_id = serializers.IntegerField(source='answer.sequence_id', read_only=True)  # 답변의 sequence_id 추가

    class Meta:
        model = Reply
        fields = ['id', 'question', 'answer', 'answer_sequence_id', 'reply_sequence_id', 'content', 'created_at', 'updated_at']