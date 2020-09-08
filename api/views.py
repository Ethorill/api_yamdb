from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from pylint.reporters.ureports.nodes import Title
from rest_framework import generics, mixins, request, status, views, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    ConfirmationSerializer,
    CreateTitleSerializer,
    CreateUserSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserMeSerializer,
    UserSerializer,
)
from .tokens import ConfirmationTokenGenerator
from .utils import email_user

User = get_user_model()

confirmation_token = ConfirmationTokenGenerator()


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdmin,)
    search_fields = ('username',)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        email_user(user, confirmation_token)


class TokenGiver(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        if serializer.is_valid():

            user = User.objects.filter(
                email=serializer.validated_data['email']
            ).first()
            if user is None:
                return Response(
                    {'email': 'no user with such email'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if confirmation_token.check_token(
                    user, serializer.validated_data['confirmation_code']
            ):
                user.is_active = True
                user.last_login = timezone.now()
                user.save()
                token = RefreshToken.for_user(user).access_token
                return Response({'token': str(token)}, status.HTTP_200_OK)
            return Response(
                {'confirmation_code': 'wrong code'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfo(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = UserMeSerializer(user, data=request.data)
        if serializer.is_valid():
            if (
                    serializer.validated_data.get('role')
                    and user.role != 'admin'
                    and user.role != serializer.validated_data['role']
            ):
                return Response(
                    {'role': 'you have no rigths to change this field'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            send_mail = False
            if (
                    serializer.validated_data.get('email')
                    and user.email != serializer.validated_data['email']
            ):
                send_mail = True
            serializer.save()
            if send_mail:
                email_user(user, confirmation_token)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        return review.comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)

    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class BaseMixViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('=name',)


class CategoryViewSet(BaseMixViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(BaseMixViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializer
        return CreateTitleSerializer
