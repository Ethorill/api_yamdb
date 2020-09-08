from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenresViewSet,
    ReviewViewSet,
    TitleViewSet,
    TokenGiver,
    UserCreate,
    UserInfo,
    UserList,
    UserViewSet,
)

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenresViewSet, basename='genres')
router.register('categories', CategoryViewSet, basename='categories')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)


urlpatterns = [
    path('v1/auth/email/', UserCreate.as_view(), name='create_user'),
    path('v1/auth/token/', TokenGiver.as_view(), name='get_token'),
    path('v1/users/me/', UserInfo.as_view(), name='get_user'),
    path('v1/users/', UserList.as_view(), name='get_users'),
    path('v1/', include(router.urls)),
]

handler400 = 'rest_framework.exceptions.bad_request'
