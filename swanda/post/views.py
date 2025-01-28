import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *



# Create your views here.
class QuestionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            title = request.data.get('title')
            content = request.data.get('content')
            file = request.FILES.get('file')
            if not title or not content:
                return Response({'error': 'Title or content are required'}, status=status.HTTP_400_BAD_REQUEST)

            new_question = Question.objects.create(
                user = user,
                title = title,
                content = content,
                file = file
            )
            
            return Response({
                'message': 'Data received successfully',
                'title': new_question.title,
                'content': new_question.content,
                'file': new_question.file.url if new_question.file else None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdoptView(APIView):
    def apdopt(self, request, question=None, answer=None):
        try:
            question = Question.objects.get(id = question)
            
            question.adopt = 1
            question.save()
            
            # 해당 댓글을 채택한 댓글로 지정
            
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

class AnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = json.loads(request.body)
            content = data.get('content')
            question_id = data.get('question')

            if not content:
                return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.get(id=question_id)

            new_answer = Answer.objects.create(
                user = user,
                question=question,
                content=content
            )

            return Response({
                'message': 'Answer created successfully',
                'question': question.title,
                'content': new_answer.content,
                # 'likes': new_answer.likes,
                'is_adopted': new_answer.is_adopted
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = json.loads(request.body)
            content = data.get('content')
            answer_id = data.get('answer')

            if not content:
                return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not answer_id:
                return Response({'error': 'Answer ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                answer = Answer.objects.get(id=answer_id)
            except Answer.DoesNotExist:
                return Response({'error': 'Parent answer not found'}, status=status.HTTP_404_NOT_FOUND)

            reply = Reply.objects.create(
                user = user,
                answer=answer,
                content=content
            )
            return Response({
                'message': 'Reply created successfully',
                'reply': {
                    'id': reply.id,
                    'answer_id': reply.answer.id,
                    'content': reply.content,
                    #'likes': reply.likes,
                    'created_at': reply.created_at,
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionViewSet(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionDetailView(APIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question, context={'request': request})

            # 기존 직렬화 데이터 가져오기
            data = serializer.data

            # 해당 질문에 대한 모든 답변의 대댓글 ID 목록 추가
            data['reply_ids'] = list(
                Reply.objects.filter(answer__question=question)
                .values_list('id', flat=True)
            )

            return Response(data, status=status.HTTP_200_OK)

        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # updated_at 필드가 자동으로 갱신됨
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

class AnswerViewSet(APIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            answers = question.answers.all()  # related_name='answers'
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

class AnswerDetailView(APIView):
    def get(self, request, question_id, sequence_id):
        try:
            answer = Answer.objects.get( question_id=question_id, sequence_id= sequence_id)
            serializer = AnswerSerializer(answer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, question_id, sequence_id):
        try:
            answer = Answer.objects.get(question__id=question_id, sequence_id=sequence_id)
            serializer = AnswerSerializer(answer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # updated_at 필드 자동 갱신
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

class ReplyViewSet(APIView):
    def get(self, request, question_id, sequence_id,):
        try:
            answer = Answer.objects.get(question_id=question_id, sequence_id=sequence_id)
            replies = answer.replies.all()  # related_name='replies'
            serializer = ReplySerializer(replies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
            return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

class ReplyDetailView(APIView):
    def get(self, request, question_id, answer_sequence_id, reply_sequence_id):
        try:
            # `question_id`와 `answer_sequence_id`를 통해 Reply를 가져옴
            reply = Reply.objects.get(
                answer__question__id=question_id,  # `Question`의 `id` 참조
                answer__sequence_id=answer_sequence_id,  # `Answer`의 `sequence_id` 참조
                reply_sequence_id=reply_sequence_id  # `Reply`의 `reply_sequence_id` 참조
            )
            serializer = ReplySerializer(reply)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reply.DoesNotExist:
            return Response({'error': 'Reply not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, question_id, answer_sequence_id, reply_sequence_id):
        try:
            reply = Reply.objects.get(
                answer__question__id=question_id,
                answer__sequence_id=answer_sequence_id,
                reply_sequence_id=reply_sequence_id
            )

            serializer = ReplySerializer(reply, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # updated_at 필드 자동 갱신
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Reply.DoesNotExist:
            return Response({'error': 'Reply not found'}, status=status.HTTP_404_NOT_FOUND)

