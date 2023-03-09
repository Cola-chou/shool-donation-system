from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Group




class MyUser(AbstractUser, PermissionsMixin):
    STUDENT = '0'
    TEACHER = '1'
    OTHER_STAFF = '2'
    NON_STAFF = '3'
    ROLE_CHOICES = [
        (STUDENT, '学生'),
        (TEACHER, '教师'),
        (OTHER_STAFF, '其他工作人员'),
        (NON_STAFF, '社会人士'),
    ]
    role = models.CharField('人群', max_length=20,
                            choices=ROLE_CHOICES,
                            null=True)
    mobile = models.CharField('手机号码',
                              max_length=11,
                              null=True,
                              unique=True)
    address = models.CharField('地址', max_length=100,
                            blank=True,
                            null=True)
    weChat = models.CharField('微信账号', max_length=100,
                              blank=True,
                              null=True)



    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class CustomGroup(Group):
    class Meta:
        proxy = True
        verbose_name = '分组'
        verbose_name_plural = '分组'
