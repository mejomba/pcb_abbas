from rest_framework import serializers
from .models import Post, BlogCategory


class GuidPostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    category_name = serializers.CharField(source='category.title', read_only=True)
    breadcrumb = serializers.SerializerMethodField()
    reading_time = serializers.ReadOnlyField(source='reading_time_minutes')
    is_public = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'slug',
            'content',
            'guid_content',
            'excerpt',
            'thumbnail',
            'tags',
            'category',
            'category_name',
            'status',
            'publish_at',
            'view_count',
            'is_featured',
            'reading_time',
            'is_public',
            'seo_title',
            'seo_description',
            'created_at',
            'updated_at',
            'breadcrumb',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_breadcrumb(self, obj):
        return {cat.title: cat.slug for cat in obj.category.get_ancestors(include_self=True)}


class GuidPostMiniSerializer(GuidPostSerializer):
    posts = serializers.SerializerMethodField()

    class Meta(GuidPostSerializer.Meta):
        fields = ['id', 'title', 'slug', 'category_name', 'breadcrumb', 'posts']

    def get_posts(self, obj):
        qs = Post.objects.filter(category=obj.category).exclude(id=obj.id).values('id', 'title', 'slug')
        return list(qs)


class GuidPostContentSerializer(GuidPostSerializer):
    class Meta(GuidPostSerializer.Meta):
        fields = ['category', 'breadcrumb', 'content']

    # def get_posts(self):
    #     pass


class BlogCategorySerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = [
            'id', 'title', 'slug', 'child', 'level',
        ]

    def get_child(self, obj):
        """
        فقط اولین زیرشاخه در مسیر تا برگ را برمی‌گرداند
        (مسیر یکتا از ریشه تا برگ)
        """
        children = obj.get_children()
        if not children.exists():
            return None

        child = children.all()
        return BlogCategorySerializer(child, many=True).data
