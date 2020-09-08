from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        required=False,
        validators=(UniqueValidator(queryset=Category.objects.all()),),
    )

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        required=False,
        validators=(UniqueValidator(queryset=Genre.objects.all()),),
    )

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class CreateTitleSerializer(TitleSerializer):
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )


class FromContext(object):
    requires_context = True

    def __init__(self, base):
        self.base = base

    def __call__(self, serializer_field):
        return self.base(serializer_field.context)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
    )
    title = serializers.ReadOnlyField(
        default=FromContext(
            lambda context: context.get('view').kwargs['title_id']
        )
    )

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result.popitem('title')
        return result

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        validators = (
            UniqueTogetherValidator(
                queryset=Review.objects.all(), fields=('author', 'title')
            ),
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
        )


class UserMeSerializer(UserSerializer):
    email = serializers.EmailField(
        validators=(UniqueValidator(queryset=User.objects.all()),),
        required=False,
    )


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)


class ConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(max_length=30, required=True)
