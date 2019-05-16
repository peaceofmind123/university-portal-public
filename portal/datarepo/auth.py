# This is a custom authentication backend page where we downcast user types after default authentication
# This is because during Login authentication that is common for all 3 user types, we get back
# a User instance but we need AdminUser/TeacherUser/StudentUser instance

from django.contrib.auth.backends import ModelBackend
from .models import accounts


class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        return self.downcast_usertype(super().authenticate(request,username,password,**kwargs))

    def get_user(self, user_id):
        return self.downcast_usertype(super().get_user(user_id))

    def downcast_usertype(self,user):
        if user:
            try:
                customUser = accounts.AdminUser.objects.get(pk=user.pk)
                return customUser
            except accounts.AdminUser.DoesNotExist:
                pass

            try:
                customUser = accounts.TeacherUser.objects.get(pk=user.pk)
                return customUser
            except accounts.TeacherUser.DoesNotExist:
                pass

            try:
                customUser = accounts.StudentUser.objects.get(pk=user.pk)
                return customUser
            except accounts.StudentUser.DoesNotExist:
                pass

        return user
