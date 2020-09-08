from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_admin(user):
    return user.role == 'admin' or user.is_superuser


def is_moderator(user):
    return user.role == 'moderator'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and is_admin(user)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or user.is_authenticated
            and is_admin(user)
        )


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or obj.author == user
            or is_admin(user)
            or is_moderator(user)
        )
