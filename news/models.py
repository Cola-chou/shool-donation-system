import os
import shutil

from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.utils.html import format_html

from apps.donation.models import DonationProject
from apps.user.models import MyUser


class PublishedManageer(models.Manager):
    def get_queryset(self):
        # 返回处于发布态的新闻查询集
        return super(PublishedManageer, self).get_queryset().filter(status='1')


class News(models.Model):
    # 自定义新闻图片存储路径方法
    def newsImage_directory_path(instance, filename):
        times = instance.created_time
        times = f'{times.year}_{times.month}_{times.day}'
        dirs = f'news_image/{times}/{instance.title}/'
        dirs = os.path.join(settings.MEDIA_ROOT, dirs)
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        # 文件将被上传到 news_image/x年_x月_x日/文件夹中
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

    # 自定义admin状态显示方法
    def Status(self):
        if self.status == '1':
            format_td = format_html('<span style="padding:2px;background-color:red;color:white">发布</span>')
        elif self.status == '0':
            format_td = format_html('<span style="padding:2px;background-color:blue;color:white">编辑</span>')
        return format_td

    Status.short_description = "物品状态"

    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = '新闻'
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("news:news_detail", args=[self.id])

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


class PublishedAnnouncementManageer(models.Manager):
    def get_queryset(self):
        # 返回处于发布状态的公告查询集
        return super(PublishedAnnouncementManageer, self).get_queryset().filter(status='published')


class Announcement(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '发布'),
    )
    title = models.CharField('公告标题', max_length=100)
    content = models.TextField('公告内容')
    status = models.CharField('状态', max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    created_time = models.DateTimeField('创建时间',
                                        auto_now_add=True)
    modify_time = models.DateTimeField('更新时间',
                                       auto_now=True)
    author = models.ForeignKey(MyUser, verbose_name='发布者',
                               related_name='announcements',
                               on_delete=models.CASCADE)

    objects = models.Manager()  # 默认管理器
    published = PublishedAnnouncementManageer()  # 自定义管理器

    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    class CommentModel(models.Model):
        no_comment = models.TextField()
        aaa = models.IntegerField(default=0, help_text="test default")
        help_text = models.CharField(max_length=40,
                                     help_text="this is help text")

        class Meta:
            app_label = 'tests'
            db_table = 'comment_model'
            verbose_name = '这是表注释'
