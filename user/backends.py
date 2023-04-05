from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class CustomModelBackend(ModelBackend):
    """
    自定义用户验证模板
    """
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
