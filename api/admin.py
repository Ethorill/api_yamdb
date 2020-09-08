from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Category, Comment, Genre, Review, Title, TitleGenre

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'first_name', 'last_name')
    empty_value_display = '---'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'text', 'author', 'pub_date')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '---'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title_id', 'text', 'author', 'score', 'pub_date')
    search_fields = ('text',)
    empty_value_display = '---'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    empty_value_display = '---'


class TitleGenreAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(TitleGenre, TitleGenreAdmin)
admin.site.register(User, UserAdmin)

