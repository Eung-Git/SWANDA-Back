from django.urls import path

from . import views
from .views import *


urlpatterns = [
    # path("", views.index, name="index"),
    path('question_create/', QuestionView.as_view(), name='create-question'),
    path('answer_create/', AnswerView.as_view(), name='create-answer'),
]