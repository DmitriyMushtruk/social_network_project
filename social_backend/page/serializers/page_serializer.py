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

class PageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = TagListSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields =    "__all__"

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        page = Page.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data['name'])
            page.tags.add(tag)
        return super().create(validated_data)