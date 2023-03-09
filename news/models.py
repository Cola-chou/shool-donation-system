import os
import shutil

from django.conf import settings
from django.db import models
from django.utils.html import format_html

from apps.donation.models import DonationProject


# Create your models here.
class PublishedManageer(models.Manager):
    def get_queryset(self):
        return super(PublishedManageer, self).get_queryset().filter(status='1')


class News(models.Model):
    def newsImage_directory_path(instance, filename):
        times = instance.created_time
        times = f'{times.year}_{times.month}_{times.day}'
        dirs = f'news_image/{times}/{instance.title}/'
        dirs = os.path.join(settings.MEDIA_ROOT, dirs)
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        # 文件将被上传到 MEDIA_ROOT/user_<id>/<filename> 文件夹中
        return 'news_image/{}/{}/{}'.format(times,
                                            instance.title,
                                            filename)

    status_choice = [
        ('0', '编辑'),
        ('1', '发布'),
    ]
    title = models.CharField('标题', max_length=50)
    status = models.CharField('状态', choices=status_choice, max_length=5)
    body = models.TextField('正文')
    created_time = models.DateTimeField('创建时间',
                                        auto_now_add=True)
    image = models.ImageField('新闻图片',
                              upload_to=newsImage_directory_path)
    modified_time = models.DateTimeField('修改时间')

    objects = models.Manager()  # 默认管理器
    published = PublishedManageer()  # 自定义管理器

    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = '新闻'
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    # 这里要使用format_html
    # 才可以在后台显示图片
    def image_img(self):
        return format_html(
            '<img src="{}" width="100px"/>',
            self.image.url,
        )

    image_img.short_description = '图片'
    # 图片是否显示
    image_img.allow_tags = True
