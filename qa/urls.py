from rest_framework.routers import DefaultRouter
from qa.views import QuestionViewSet, AnswerViewSet
from django.urls import path

app_name = 'qa'

router = DefaultRouter()
router.register('question', QuestionViewSet, basename='question')
router.register('answer', AnswerViewSet, basename='answer')
urlpatterns = router.urls
