

from rest_framework import serializers
from .models import Question, Answer, Reply

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'created_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'sequence_id', 'content', 'created_at', 'question']

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['id', 'reply_sequence_id', 'content', 'created_at', 'answer']