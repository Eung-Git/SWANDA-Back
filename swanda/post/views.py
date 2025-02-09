import json
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from user.models import User
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated  # 로그인한 사용자만 가능
from rest_framework import status
from .models import Answer

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
    def put(self, request):
        try:
            question_id = request.data.get('question_id')
            answer_sequence_id = request.data.get('answer_sequence_id')

            if not question_id or not answer_sequence_id:
                return Response({'error': 'Question ID and Answer Sequence ID are required'}, status=status.HTTP_400_BAD_REQUEST)

            # question_id를 정수로 변환
            try:
                question_id = int(question_id)
                answer_sequence_id = int(answer_sequence_id)
            except ValueError:
                return Response({'error': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

            # 질문 가져오기
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # 답변 가져오기
            try:
                answer = Answer.objects.get(question=question, sequence_id=answer_sequence_id)
            except Answer.DoesNotExist:
                return Response({'error': f'Answer with Sequence ID {answer_sequence_id} for Question {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # 기존 채택된 답변이 있는지 확인 후 초기화
            previous_accepted_answer = Answer.objects.filter(question=question, is_adopted=True).first()
            if previous_accepted_answer:
                previous_accepted_answer.is_adopted = False
                previous_accepted_answer.save()

            # 새 답변 채택
            answer.is_adopted = True
            answer.save()

            # 질문 업데이트 (채택된 답변이 있는지 표시)
            question.has_accepted_answer = True
            question.save()

            return Response({
                'message': 'Answer accepted successfully',
                'question_id': question.id,
                'accepted_answer_id': answer.sequence_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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

            # question_id를 정수로 변환 (문자열로 들어오는 경우 대비)
            try:
                question_id = int(question_id)
            except ValueError:
                return Response({'error': 'Invalid question ID format'}, status=status.HTTP_400_BAD_REQUEST)

            # 질문이 존재하는지 확인
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # 답변 생성
            new_answer = Answer.objects.create(
                user = user,
                question=question,
                content=content
            )

            return Response({
                'message': 'Answer created successfully',
                'question': question.title,
                'content': new_answer.content,
                'is_adopted': new_answer.is_adopted
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReplyView(APIView):
    permission_classes = [IsAuthenticated]
  
    def post(self, request):
        try:
            user = request.user
            question_id = request.data.get('question_id')
            answer_sequence_id = request.data.get('answer_sequence_id')
            content = request.data.get('content')
            if not question_id or not answer_sequence_id or not content:
                return Response({'error': 'Question ID, Answer Sequence ID, and Content are required'}, status=status.HTTP_400_BAD_REQUEST)

            # ID 값을 정수로 변환
            try:
                question_id = int(question_id)
                answer_sequence_id = int(answer _sequence_id)
            except ValueError:
                return Response({'error': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

            # 질문 가져오기
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # 답변 가져오기 (`answer_id` 대신 `answer_sequence_id` 사용)
            try:
                answer = Answer.objects.get(question=question, sequence_id=answer_sequence_id)
            except Answer.DoesNotExist:
                return Response({'error': f'Answer with Sequence ID {answer_sequence_id} for Question {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # 마지막 대댓글의 sequence_id 찾기
            last_reply = Reply.objects.filter(answer=answer).order_by('reply_sequence_id').last()
            reply_sequence_id = (last_reply.reply_sequence_id + 1) if last_reply else 1

            # 대댓글 생성
            new_reply = Reply.objects.create(
                user = user,
                answer=answer,
                reply_sequence_id=reply_sequence_id,
                content=content
            )

            return Response({
                'message': 'Reply created successfully',
                'reply': {
                    'id': new_reply.id,
                    'question_id': question.id,
                    'answer_sequence_id': answer.sequence_id,
                    'reply_sequence_id': new_reply.reply_sequence_id,
                    'content': new_reply.content,
                    'created_at': new_reply.created_at
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        question_id = request.data.get('question')
        answer_id = request.data.get('answer')
        
        if question_id:
            question = get_object_or_404(Question, id=question_id)
            
            if user in question.likes.all():
                question.likes.remove(user)
                return Response({"detail": "좋아요 삭제"}, status=status.HTTP_200_OK)
            
            else:
                question.likes.add(user)
                return Response({"detail": "좋아요 추가"}, status=status.HTTP_200_OK)
            
        else:
            answer = get_object_or_404(Answer, id=answer_id)
            
            if user in answer.likes.all():
                answer.likes.remove(user)
                return Response({"detail": "좋아요 삭제"}, status=status.HTTP_200_OK)
            
            else:
                answer.likes.add(user)
                return Response({"detail": "좋아요 추가"}, status=status.HTTP_200_OK)
           
class ScrapView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        question_id = request.data.get('question')
        
        question = get_object_or_404(Question, id=question_id)
        
        if user in question.scrap.all():
            question.scrap.remove(user)
            user.scrap_question(question)
            return Response({"detail": "스크랩 삭제"}, status=status.HTTP_200_OK)
        else:
            question.scrap.add(user)
            user.scrap_question(question)
            return Response({"detail": "스크랩 추가"}, status=status.HTTP_200_OK)

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
          
