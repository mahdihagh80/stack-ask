from rest_framework import serializers
from qa.models import Question, Tag, Answer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'tags']

    def to_internal_value(self, data):
        tag_list = data.pop('tags', None)
        if tag_list:
            tags = [{"name": tag} for tag in tag_list]
            data['tags'] = tags
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = [tag['name'] for tag in representation['tags']]
        return representation

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        q = Question.objects.create(**validated_data, owner=self.context['request'].user)
        tags_obj_list = []
        for tag in tags:
            t, _ = Tag.objects.get_or_create(name=tag['name'])
            tags_obj_list.append(t)

        q.tags.add(*tags_obj_list)
        return q

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags:
            tags_obj_list = []
            for tag in tags:
                t, _ = Tag.objects.get_or_create(name=tag['name'])
                tags_obj_list.append(t)

            instance.tags.set(*tags_obj_list, clear=True)
        return super().update(instance, validated_data)


class AnswerSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data['owner'] = self.context.get('request').user.id
        return super().to_internal_value(data)

    class Meta:
        model = Answer
        fields = ['id', 'question', 'owner', 'description', 'is_correct']
        read_only_fields = ['is_correct']
