from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from neighbourhood.models import Token

User = get_user_model()


def make_token_for_user(user, domain="user", obj=None):
    generator = PasswordResetTokenGenerator()
    token = generator.make_token(user)
    t = Token.objects.create(token=token, domain=domain, user_id=user.pk)
    if obj is not None:
        t.domain_id = obj.pk
        t.save()

    return t


def get_user_for_token(token):
    try:
        t = Token.objects.get(token=token)
    except Token.DoesNotExist:
        return None, None

    user = User.objects.get(pk=t.user_id)
    return t, user
