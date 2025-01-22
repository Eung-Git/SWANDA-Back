

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
        # read_only_fields = ['reply_ids', 'is_accepted']



class ReplySerializer(serializers.ModelSerializer):
    # question_id = serializers.IntegerField(source='answer.question.id', read_only=True)

    class Meta:
        model = Reply
        fields = ['id','question_id','answer', 'reply_sequence_id', 'content', 'created_at', 'updated_at']