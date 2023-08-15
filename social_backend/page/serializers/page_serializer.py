from rest_framework import serializers

from ..models import Page, Tag, Post, Comment

class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields =    "__all__"

class CreateOrUpdatePageSerializer(serializers.ModelSerializer):
    #tags = TagListSerializer(many=True)

    class Meta:
        model = Page
        fields = ['name', 'description', 'tags', 'is_private', 'image']

    def create(self, validated_data):
        # Логика для добавление тегов на страницу
        # пользователь добавляет тег в форму
        # проходит проверка есть ли он БД
        # если нету - добавляем в БД
        # добавляем все вписанные теги на страницу
        # 
        # Не знаю как это сейчас проверить, в браузере пишет, что
        # не поддерживает формы HTML, или что-то такое
        # Можно будет проверить прикрутив это к фронту
        # 
        # Мб ты подскажешь как сделать правильнее)) бо я пока на этом остановился
        # ---->
        # tags_data = validated_data.pop('tags', [])
        # page = Page.objects.create(**validated_data)
        # for tag_data in tags_data:
        #     tag, created = Tag.objects.get_or_create(name=tag_data['name'])
        #     page.tags.add(tag)
        # ---->

        validated_data['owner'] = self.context['request'].user  # Set page owner
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'content', 'created_date', 'post']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields =    "__all__"


class CreateOrUpdatePostSerializer(serializers.ModelSerializer):
    page_name = serializers.CharField(source='page.name', read_only=True)
    post_comments = CommentSerializer(many=True, read_only=True, source='comments')

    likes = serializers.CharField(source='get_likes_count', read_only=True)
    dislikes = serializers.CharField(source='get_dislikes_count', read_only=True)
    class Meta:
        model = Post
        fields = ['page', 'page_name', 'content', 'file', 'comments', 'created_at', 'updated_at', 'likes', 'dislikes', 'post_comments']

