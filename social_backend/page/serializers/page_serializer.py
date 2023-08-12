from rest_framework import serializers

from ..models import Page, Tag

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