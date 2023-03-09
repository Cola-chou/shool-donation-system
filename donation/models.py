from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

import apps.item
from apps.user.models import MyUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class PublishedProjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(project_status__in=['1', '2', '3'])


class DonationProject(models.Model):
    status_choice = [
        ('0', '编辑'),
        ('1', '发起'),
        ('2', '完成'),
        ('3', '截止'),
    ]
    project_name = models.CharField('捐赠项目', max_length=100)
    project_desc = models.CharField('项目介绍', max_length=200)
    project_news = models.ForeignKey('news.News',
                                     verbose_name='捐赠新闻',
                                     related_name='project',
                                     blank=True,
                                     null=True,
                                     on_delete=models.SET_NULL)
    project_status = models.CharField('项目状态', max_length=10,
                                      choices=status_choice)
    start_time = models.DateTimeField('发起时间', auto_now_add=True)
    deadline = models.DateTimeField('截止时间')
    get_donation_amount = models.DecimalField('当前筹集金额', max_digits=10,
                                              decimal_places=2,
                                              default=0,
                                              blank=True)
    donation_amount = models.DecimalField('目的捐赠价值',
                                          max_digits=10,
                                          decimal_places=2,
                                          default=0.01,
                                          blank=True,
                                          validators=[MinValueValidator(0.01, message="价值必须大于0.01")])

    objects = models.Manager()  # 默认管理器
    published = PublishedProjectManager()  # 自定义管理器

    def save(self, *args, **kwargs):
        print('model.save')
        # # 计算目标捐赠价格
        all_price = 0
        from apps.item.models import RequestItem
        for item in RequestItem.objects.filter(donation_project__id=self.id):
            all_price += item.all_price
        self.donation_amount = all_price
        print('self.donation_amount =', all_price)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '捐赠项目'
        verbose_name_plural = '捐赠项目'

    def __str__(self):
        return f'{self.project_name}'


class DonationRecord(models.Model):
    status_choice = [
        ('0', '审核'),
        ('1', '暂存'),
        ('2', '完成'),
    ]
    donation_user = models.ForeignKey(MyUser,
                                      verbose_name='捐赠者',
                                      related_name='donation_records',
                                      on_delete=models.CASCADE)
    donation_project = models.ForeignKey(DonationProject,
                                         verbose_name='所属捐赠项目',
                                         related_name='donation_records',
                                         on_delete=models.CASCADE)
    donation_time = models.DateTimeField('捐赠时间', auto_now_add=True)
    donation_amount = models.DecimalField('捐赠价值', max_digits=10,
                                          decimal_places=2,
                                          null=False,
                                          default=0)
    status = models.CharField('捐赠状态',
                              max_length=10,
                              choices=status_choice)

    def save(self, *args, **kwargs):
        print('donationRecord。save（）')
        # 保存捐赠物品时，自动更新物品价值
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '捐赠记录'
        verbose_name_plural = '捐赠记录'

    def __str__(self):
        return f'{self.donation_project}_donation_record_{self.pk}'


# @receiver(post_save, sender=DonationRecord)
# def update_donation_project(sender, instance, **kwargs):
#     print('hello')
#     project = instance.donation_project
#     amount = project.donation_records.aggregate(Sum('donation_amount'))['donation_amount__sum']
#     project.get_donation_amount = amount
#     project.save()