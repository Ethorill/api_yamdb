from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def _create_user(self, email, **fields):

        if not email:
            raise ValueError('email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **fields)
        if fields.get('password'):
            user.set_password(fields.get('password'))
        user.save()

        return user

    def create_user(self, email, **fields):
        fields.setdefault('is_superuser', False)
        return self._create_user(email, **fields)

    def create_superuser(self, email, username, password, **fields):
        fields.setdefault('is_superuser', True)
        fields.setdefault('is_staff', True)
        fields.setdefault('role', 'admin')

        if fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            email, username=username, password=password, **fields
        )
