from django.core.mail import send_mail


def email_user(user, token):
    send_mail(
        'Yambd. Confirmation code',
        token.make_token(user),
        'registration@yambd.com',
        (user.email,),
        fail_silently=False,
    )
