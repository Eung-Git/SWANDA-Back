from django.urls import path

from . import views
from .views import *


urlpatterns = [
    # path("", views.index, name="index"),
    path('question_create/', QuestionView.as_view(), name='create-question'),
    path('answer_create/', AnswerView.as_view(), name='create-answer'),
    path('reply_create/', ReplyView.as_view(), name='create-reply'),
    path('adopt/', AdoptView.as_view(), name='adopt-answer'),
    path('questions/', QuestionViewSet.as_view(), name='question-list'),
    path('likes/', LikeView.as_view(), name='likes'),
    path('scrap/', ScrapView.as_view(), name='scrap'),
    path('questions/<int:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('answers/<int:question_id>/', AnswerViewSet.as_view(), name='answer-list'),
    path('answers/<int:question_id>/<int:sequence_id>/', AnswerDetailView.as_view(), name='answer-detail'),
    path('replies/<int:question_id>/<int:sequence_id>/', ReplyViewSet.as_view(), name='reply-list'),
    path('replies/<int:question_id>/<int:answer_sequence_id>/<int:reply_sequence_id>/', ReplyDetailView.as_view(), name='reply-detail'),
    path('answers/<int:question_id>/<int:answer_sequence_id>/like/', AnswerLikeView.as_view(), name='like-answer'),

]
