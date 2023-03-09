import os
import shutil

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


class MyUser(AbstractUser, PermissionsMixin):
    def userAvatars_directory_path(instance, filename):
        dirs = f'user_avatar' \
               f'/{instance.username}'
        dirs = os.path.join(settings.MEDIA_ROOT, dirs)
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        # 文件将被上传到 MEDIA_ROOT/user_<id>/<filename> 文件夹中
        return 'user_avatar/' \
               '{}/{}'.format(instance.username,
                              filename)

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
    email = models.EmailField('邮件', null=True, unique=True)
    avatar = models.ImageField('头像', upload_to=userAvatars_directory_path,
                               blank=True,
                               null=True)

    role = models.CharField('人群', max_length=20,
                            choices=ROLE_CHOICES,
                            null=True)
    mobile = models.CharField('手机号码',
                              max_length=11,
                              null=True,
                              blank=True)
    address = models.CharField('地址', max_length=100,
                               blank=True,
                               null=True)
    weChat = models.CharField('微信账号', max_length=100,
                              blank=True,
                              null=True)

    def save(self, *args, **kwargs):
        # # 创建以用户名为名的文件夹
        # user_folder = os.path.join(settings.AVATAR_ROOT, self.username)
        # os.makedirs(user_folder, exist_ok=True)
        # # 生成头像文件路径
        # avatar_path = os.path.join(user_folder, str(self.avatar))
        # # 调用父类的save方法，保存头像文件
        super().save(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class Announcement(models.Model):
    title = models.CharField('公告标题', max_length=100)
    content = models.TextField('公告内容')
    created_time = models.DateTimeField('创建时间',
                                        auto_now_add=True)
    modify_time = models.DateTimeField('更新时间',
                                       auto_now=True)

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'

    def __str__(self):
        return self.title
