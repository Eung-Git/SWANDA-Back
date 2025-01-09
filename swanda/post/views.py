import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *


# Create your views here.
class QuestionView(APIView):
    def post(self, request):
        try:
            title = request.data.get('title')
            content = request.data.get('content')
            file = request.FILES.get('file')
            
            if not title or not content:
                return Response({'error': 'Title or content are required'}, status=status.HTTP_400_BAD_REQUEST)

            new_question = Question.objects.create(
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
            