from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html

from apps.user.models import MyUser

from multiupload.fields import MultiFileField


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
                                      choices=status_choice,
                                      default='0')
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

    def Speed(self):
        count = round(self.get_donation_amount / self.donation_amount * 100)
        print(self.get_donation_amount, self.donation_amount, f'{count}%')
        return format_html('<progress max="100" value="{}"></progress> {}%', count, count)

    Speed.short_description = "当前进度"

    # 自定义admin状态显示方法
    def Status(self):
        if self.project_status == '0':
            format_td = format_html('<span style="padding:2px;background-color:gray;color:white">编辑</span>')
        elif self.project_status == '1':
            format_td = format_html('<span style="padding:2px;background-color:blue;color:white">发起</span>')
        elif self.project_status == '2':
            format_td = format_html('<span style="padding:2px;background-color:green;color:white">完成</span>')
        elif self.project_status == '3':
            format_td = format_html('<span style="padding:2px;background-color:red;color:white">未完成</span>')
        return format_td

    Status.short_description = "当前状态"

    def save(self, *args, **kwargs):
        print('DonationProject.save（）')
        # # 计算目标捐赠价格
        request_all_price = 0
        donation_all_price = 0
        from apps.item.models import RequestItem, DonationItem
        for item in RequestItem.objects.filter(donation_project__id=self.id):
            request_all_price += item.all_price
        self.donation_amount = request_all_price
        print(f'DonationProject.{self.id}.donation_amount =', request_all_price)
        for item in DonationItem.published.filter(donation_record__donation_project_id=self.id):
            donation_all_price += item.all_price
        self.get_donation_amount = donation_all_price
        print(f'DonationProject.{self.id}.get_donation_amount =', donation_all_price)
        if self.donation_amount <= self.get_donation_amount and self.project_status != '3' and self.get_donation_amount != 0:
            print('项目筹集完毕 目的金额：{} 实际金额：{} 项目状态：（{}）->（完成）'.format(self.donation_amount, self.get_donation_amount, self.get_project_status_display()))
            self.project_status = '2'
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '捐赠项目'
        verbose_name_plural = '捐赠项目'
        ordering = ['-start_time', '-deadline']

    def __str__(self):
        return f'{self.project_name}'


class DonationRecord(models.Model):
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

    def save(self, *args, **kwargs):
        print('donationRecord。save（）')
        # 保存捐赠物品时，自动更新物品价值
        # # 计算目标捐赠价格
        all_price = 0
        from apps.item.models import DonationItem
        for item in DonationItem.published.filter(donation_record_id=self.id):
            all_price += item.all_price
        self.donation_amount = all_price
        print(f'DonationRecord.{self.id}.donation_amount =', all_price)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = '捐赠记录'
        verbose_name_plural = '捐赠记录'
        ordering = ['donation_user', '-donation_amount']

    def __str__(self):
        return f'#{self.pk}_[{self.donation_project}]@{self.donation_user}'


# 保存记录对象后自动删除空对象会引发 提交捐赠物品清单的保存错误
# @receiver(post_save, sender=DonationRecord)
# def del_empty_record(sender, instance, **kwargs):
#     '''捐赠记录保存时自动删除空record'''
#     items = instance.donation_items.all()
#     if not items:
#         print('删除空record')
#         record = DonationRecord.objects.get(id=instance.id)
#         record.delete()


# class Client(models.Model):
#     name = models.CharField(verbose_name='委托人姓名', max_length=50)
#     contact = models.CharField(verbose_name='委托人联系方式', max_length=20)
#     address = models.CharField(verbose_name='委托人地址', max_length=100)
#     proofs = MultiFileField(validators=[FileExtensionValidator(['pdf', 'docx', 'jpg'])], label='证明文件')
#
#     # Additional fields for organization donors
#     is_organization = models.BooleanField(verbose_name='是否为慈善机构', default=False)
#     organization_name = models.CharField(verbose_name='机构名称', max_length=50, blank=True, null=True)
#
#     def __str__(self):
#         return self.name
