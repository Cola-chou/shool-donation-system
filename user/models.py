import os
import shutil

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db.models import Sum


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

    ROLE_CHOICES = [
        ('0', '学生'),
        ('1', '教师'),
        ('2', '其他工作人员'),
        ('3', '社会人士'),
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

    def get_donations_for_project(self, project_id):
        '''获取一个字典：用户在某捐赠项目中捐赠的总价值和物品列表'''
        donations = self.donation_records.filter(donation_project_id=project_id)
        total_amount = donations.aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        items = []
        for donation in donations:
            items.extend(list(donation.donation_items.filter(status__in=['1', '2'])))
        return {'total_amount': total_amount, 'items': items}

    def get_all_donations(self):
        '''获取一个字典：用户参与的所有捐赠项目中捐赠的总价值和物品列表'''
        donations = self.donation_records.all()
        total_amount = donations.aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        items = []
        for donation in donations:
            items.extend(list(donation.donation_items.filter(status__in=['1', '2'])))
        return {'total_amount': total_amount, 'items': items}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
