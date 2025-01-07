from django.urls import path

from . import views
from .views import QuestionView


urlpatterns = [
    # path("", views.index, name="index"),
    path('create/', QuestionView.as_view(), name='create-question'),
]