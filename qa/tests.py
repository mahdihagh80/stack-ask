from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from .models import Question, Tag

User = get_user_model()

class QuestionTestCase(APITestCase):
    def setUp(self):
        user1_information = {'username': 'user1',
                             'password': 'password1'}
        self.user1 = User.objects.create_user(**user1_information)
        self.user1_token = Token.objects.create(user=self.user1)

        user2_information = {'username': 'user2',
                             'password': 'password2'}
        self.user2 = User.objects.create_user(**user2_information)
        self.user2_token = Token.objects.create(user=self.user2)

        self.q1 = Question.objects.create(owner=self.user1, title='title1', description='description1')
        tag1 = Tag.objects.create(name='tag1')
        tag2 = Tag.objects.create(name='tag2')
        self.q1.tags.add(tag1, tag2)

    def test_question_creation(self):
        data = {'title': 'title',
                'description': 'description',
                'tags': ['tag1', 'tag2']}

        response = self.client.post(reverse('qa:question-list'),
                                    data=data,
                                    format='json',
                                    headers={'AUTHORIZATION': f'Token {self.user1_token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        question_id = response.data.pop('id')
        self.assertEqual(response.data, data)

        try:
            question = Question.objects.get(pk=question_id)
            tags = question.tags.values_list('name', flat=True).all()
            self.assertEqual(list(tags), data.get('tags'))
            self.assertEqual(question.title, data.get('title'))
            self.assertEqual(question.description, data.get('description'))
        except Question.DoesNotExist:
            self.fail('question does not create in database')

    def test_question_retrieval(self):
        expected_data = {'title': 'title1',
                         'description': 'description1',
                         'tags': ['tag1', 'tag2']}
        response = self.client.get(reverse('qa:question-detail', kwargs={'pk': self.q1.id}))
        response.data.pop('id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_question_delete(self):
        response = self.client.delete(reverse('qa:question-detail', kwargs={'pk': self.q1.id}),
                                      headers={'AUTHORIZATION': f'Token {self.user1_token}'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = Question.objects.filter(pk=self.q1.id).count()
        self.assertEqual(count, 0)

    def test_question_update(self):
        data = {'title': 'new_title1',
                'description': 'new_description1',
                'tags': ['new_tag1', 'new_tag2']}

        response = self.client.put(reverse('qa:question-detail', kwargs={'pk': self.q1.id}),
                                   data=data,
                                   format='json',
                                   headers={'AUTHORIZATION': f'Token {self.user1_token}'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        self.assertEqual(response.data, data)

        question = Question.objects.get(pk=self.q1.id)
        tags = question.tags.values_list('name', flat=True).all()
        self.assertEqual(list(tags), data.get('tags'))
        self.assertEqual(question.title, data.get('title'))
        self.assertEqual(question.description, data.get('description'))

        data = {'title': 'new_title11'}
        response = self.client.patch(reverse('qa:question-detail', kwargs={'pk': self.q1.id}),
                                     data=data,
                                     format='json',
                                     headers={'AUTHORIZATION': f'Token {self.user1_token}'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), data.get('title'))

        title = Question.objects.values('title').get(pk=self.q1.id).get('title')
        self.assertEqual(title, data.get('title'))


        # TODO : writing test to check permissions for unsafe methods










