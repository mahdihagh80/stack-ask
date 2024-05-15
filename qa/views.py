from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from qa.models import Question, Answer
from qa.serializers import QuestionSerializer, AnswerSerializer
from qa.permissions import IsOwnerOrReadOnly


class QuestionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'answers':
            return AnswerSerializer
        return QuestionSerializer

    def get_queryset(self):
        if self.action == 'answers':
            return Answer.objects.all()
        return Question.objects.all()

    @action(detail=True, methods=['get'])
    def answers(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(question=kwargs['pk'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # just owner of question can use this action
    @action(detail=True, methods=['post'])
    def mark_as_correct(self, request, *args, **kwargs):
        question_id = request.data.get('question')
        if not question_id:
            return Response({'detail': 'question field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.only('owner').get(pk=question_id)
        except Question.DoesNotExist:
            raise Http404('No Question matches the given query.')

        if question.owner_id != request.user.id:
            return Response({'detail': 'You aren\'t the owner of the specified question.'},
                            status=status.HTTP_400_BAD_REQUEST)

        answer = self.get_object()
        if answer.question_id != question_id:
            return Response(
                {'detail': 'This answer isn\'t related to this specific question.'},
                status=status.HTTP_400_BAD_REQUEST)

        answer.is_correct = True
        answer.save()
        return Response(self.get_serializer(answer).data)


        # from rest_framework.generics import get_object_or_404
        # question = get_object_or_404(Question, pk=question_id)
        # try:
        #     question = Question.objects.get(pk=question_id)
        # except Question.DoesNotExist:
        #     from django.http import Http404
        #     raise Http404("No question matches the given query.")
        # print(question.owner_id == request.user.id)


        # serializer = self.get_serializer(data=request.data, partial=True)



        return Response("test", status=status.HTTP_200_OK)

# class AnswerGenericView(
#     CreateModelMixin,
#     UpdateModelMixin,
#     DestroyModelMixin,
#     RetrieveModelMixin,
#     GenericAPIView
# ):
#
#     lookup_url_kwarg = 'answer_id'
#     serializer_class = AnswerSerializer
#     permission_classes = []
#
#     def get_queryset(self):
#         # return Answer.objects.filter(question_id=self.kwargs['question_id'])
#         return Answer.objects.all()
#
#     # def get_serializer(self, *args, **kwargs):
#     #     serializer_class = self.get_serializer_class()
#     #     kwargs.setdefault('context', self.get_serializer_context())
#     #     return serializer_class(*args, **kwargs)
#
#     def get(self, request, *args, **kwargs):
#         if kwargs.get('answer_id', None):
#             return self.retrieve(request, *args, **kwargs)
#
#         return self.list(request, *args, **kwargs)
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         from django.forms.models import model_to_dict
#         print(model_to_dict(instance))
#
#         # serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         # serializer.is_valid(raise_exception=True)
#         # self.perform_update(serializer)
#         #
#         # if getattr(instance, '_prefetched_objects_cache', None):
#         #     # If 'prefetch_related' has been applied to a queryset, we need to
#         #     # forcibly invalidate the prefetch cache on the instance.
#         #     instance._prefetched_objects_cache = {}
#
#         # return Response(serializer.data)
#         return Response('teset deone', status=status.HTTP_200_OK)
#     def perform_update(self, serializer):
#         serializer.save()
#
#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def patch(self, request, *args, **kwargs):
#         # print(args)
#         # print(kwargs)
#         return self.partial_update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
#
#
#
#
#
#
#
#
#
#
#
#
