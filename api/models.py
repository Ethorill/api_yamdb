import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Avg

from .managers import UserManager


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    role = models.CharField(
        max_length=10,
        choices=(
            ('user', 'user'),
            ('moderator', 'moderator'),
            ('admin', 'admin'),
        ),
        default='user',
        verbose_name='Роль',
    )
    email = models.EmailField(unique=True, verbose_name='Почта')
    username = models.SlugField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Имя пользователя',
    )

    objects = UserManager()

    def __str__(self):
        return self.username or self.email


class Category(models.Model):
    name = models.CharField(
        max_length=15, verbose_name='Название категории', unique=True
    )
    slug = models.SlugField(max_length=15, unique=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('slug',)


class TitleGenre(models.Model):
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('title', 'genre')
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'


class Genre(models.Model):
    name = models.CharField(
        max_length=15, verbose_name='Имя жанра', unique=True
    )
    slug = models.SlugField(max_length=15, unique=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('slug',)


class Title(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        null=True,
        blank=True,
        validators=(MaxValueValidator(datetime.date.today().year),),
    )
    rating = models.FloatField(verbose_name='Рейтинг', null=True, blank=True,)
    description = models.TextField(
        verbose_name='Описание', blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre, related_name='genres', through=TitleGenre,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id',)


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка', choices=[(r, r) for r in range(1, 11)],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата оценки', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        score_avg = Review.objects.filter(title_id=self.title).aggregate(
            Avg('score')
        )
        self.title.rating = score_avg['score__avg']
        self.title.save()

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-score',)
        unique_together = ('author', 'title')


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
