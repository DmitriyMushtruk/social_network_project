from rest_framework import serializers

from ..models import Page, Tag, Post, Comment

class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, required=False)
    page_name = serializers.CharField(source='page.name', read_only=True)

    likes = serializers.CharField(source='get_likes_count', read_only=True)
    dislikes = serializers.CharField(source='get_dislikes_count', read_only=True)
    read_only_fields = ['page']

    class Meta:
        model = Post
        fields =    "__all__"

    def create(self, validated_data):
        return Post.objects.create(**validated_data)


class PageSerializer(serializers.ModelSerializer):
    #tags = TagListSerializer(many=True)
    posts = PostSerializer(many=True, required=False) 

    class Meta:
        model = Page
        fields =    "__all__"


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