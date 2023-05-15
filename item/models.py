import os
import shutil
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_delete, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.html import format_html

from ..donation.models import DonationRecord, DonationProject
from ..user.models import MyUser


class Category(models.Model):
    """
    目录模型
    """
    name = models.CharField('物品种类', max_length=50,
                            db_index=True)
    slug = models.SlugField('物品种类slug', max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '目录'
        verbose_name_plural = '目录'

    def __str__(self):
        return self.name


class RequestItem(models.Model):
    # 自定义请求物资图片路径方法
    def itemImage_directory_path(instance, filename):
        dirs = f'requestItems_image/{instance.donation_project.id}/{instance.id}'
        dirs = os.path.join(settings.MEDIA_ROOT, dirs)
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        # 文件将被上传到 MEDIA_ROOT/user_<id>/<filename> 文件夹中
        return 'requestItems_image/{}/{}/{}'.format(instance.donation_project.id,
                                                    instance.id,
                                                    filename)

    donation_project = models.ForeignKey(DonationProject,
                                         verbose_name='所属捐赠项目',
                                         related_name='request_items',
                                         on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 verbose_name='物品类别',
                                 related_name='request_items',
                                 on_delete=models.CASCADE)
    name = models.CharField('物品名称', max_length=50)
    detail = models.CharField('物品描述', max_length=100)
    price = models.DecimalField('物品价格', max_digits=10,
                                decimal_places=2,
                                default=1,
                                validators=[MinValueValidator(0.01, message="单价必须大于等于0.01")])
    quantity = models.IntegerField('物品数量',
                                   validators=[MinValueValidator(1, message="数量必须大于等于1")])
    all_price = models.DecimalField('价值',
                                    max_digits=10,
                                    decimal_places=2,
                                    default=1,
                                    blank=True,
                                    validators=[MinValueValidator(0.01, message="价值必须大于0.01")])
    item_image = models.ImageField(upload_to=itemImage_directory_path,
                                   verbose_name='物品照片',
                                   blank=True,
                                   null=True)

    def image_tag(self):
        if self.item_image:
            return format_html('<img src="{}" height="50"/>'.format(self.item_image.url))
        else:
            return format_html('无图片')

    image_tag.short_description = '物品图片'  # 此处为了方便显示修改页面的 label 标题

    # def save(self, *args, **kwargs):
    #     print('save')
    #     from django.db.models import Sum
    #     # 保存捐赠物品时，自动更新物品价值
    #     self.all_price = self.price * self.quantityF
    #     # 更新捐赠项目中的目的捐赠价值donation_amount
    #     self.donation_project.donation_amount = self.donation_project \
    #                                                 .request_items \
    #                                                 .aggregate(Sum('all_price'))['all_price__sum'] or 0
    #     # 此处先保存至内存中的RequestItem对象的donation_project属性中
    #     # 最后在save_related方法中对内存中的RequestItem对象保存至数据库
    #     self.donation_project.save()
    #     super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        print('Request.delete()')
        return super(RequestItem, self).delete(using=None, keep_parents=False)

    class Meta:
        verbose_name = '请求物资'
        verbose_name_plural = '请求物资'

    def __str__(self):
        return self.name


@receiver(pre_save, sender=RequestItem)
def request_item_pre_save(sender, instance, **kwargs):
    print('RequestItem.request_item_pre_save')
    instance.all_price = instance.quantity * instance.price
    print(instance.all_price)


@receiver(post_save, sender=RequestItem)
def request_item_save(sender, instance, **kwargs):
    print('RequestItem.request_item_save')
    project_id = instance.donation_project.id
    project = DonationProject.objects.get(id=project_id)
    project.donation_amount = project.request_items \
                                  .aggregate(Sum('all_price'))['all_price__sum'] or 0
    project.save()


@receiver(post_delete, sender=RequestItem)
# post_delete 删除requestitem对象之后发出信号
# pre_delete 删除requestitem对象之前发出信号
def request_item_delete(sender, instance, **kwargs):
    print('RequestItem.request_item_delete')
    # 1.删除物品对应照片文件
    # 获取要删除的物品照片路径
    if instance.item_image:
        file_path = instance.item_image.path
        # 如果物品照片存在，则删除
        if os.path.exists(file_path):
            os.remove(file_path)
        # 删除物品照片所在的文件夹
        dirs = os.path.dirname(file_path)
        if os.path.exists(dirs):
            os.rmdir(dirs)
    # 更新捐赠项目中的目的捐赠价值donation_amount
    project_id = instance.donation_project.id
    project = DonationProject.objects.get(id=project_id)
    print(project.request_items.all())
    project.donation_amount = project.request_items \
                                  .aggregate(Sum('all_price'))['all_price__sum'] or 0
    print(project.donation_amount)
    project.save()


class Require(models.Model):
    name = models.CharField('要求名称', max_length=20)
    information = models.TextField('要求信息', max_length=500)
    request_item = models.ForeignKey(RequestItem,
                                     verbose_name='请求的物品',
                                     related_name='requirements',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)

    class Meta:
        verbose_name = '物资要求'
        verbose_name_plural = '物资要求'

    def __str__(self):
        return f"{self.request_item.name} - {self.information}"


class PublishedItemsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['1', '2'])


class DonationItem(models.Model):
    def itemImage_directory_path(instance, filename):
        dirs = f'donationItems_image' \
               f'/{instance.donation_record.donation_project.id}' \
               f'/{instance.donation_record.id}/{instance.id}'
        dirs = os.path.join(settings.MEDIA_ROOT, dirs)
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        # 文件将被上传到 MEDIA_ROOT/user_<id>/<filename> 文件夹中
        return 'donationItems_image/' \
               '{}/{}/{}/{}'.format(instance.donation_record.donation_project.id,
                                    instance.donation_record.id,
                                    instance.id,
                                    filename)

    status_choice = [('0', '待审核'), ('1', '暂存'), ('2', '捐赠完成'), ]

    donation_record = models.ForeignKey(DonationRecord,
                                        verbose_name='所属捐赠记录',
                                        related_name='donation_items',
                                        on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 verbose_name='物品类别',
                                 related_name='donation_items',
                                 on_delete=models.CASCADE)
    status = models.CharField('状态', max_length=10, choices=status_choice, default='0', blank=True)
    name = models.CharField('物品名称', max_length=50)
    detail = models.CharField('物品描述', max_length=100)
    price = models.DecimalField('物品价格', max_digits=10,
                                decimal_places=2,
                                default=1,
                                validators=[MinValueValidator \
                                                (0.01, message="单价必须大于等于0。01")])
    quantity = models.IntegerField('物品数量',
                                   default=1,
                                   validators=[MinValueValidator \
                                                   (1, message="数量必须大于等于1")])
    all_price = models.DecimalField('价值',
                                    max_digits=10,
                                    decimal_places=2,
                                    default=1,
                                    blank=True,
                                    validators=[MinValueValidator \
                                                    (0.01, message="价值必须大于0.01")])
    item_image = models.ImageField(upload_to=itemImage_directory_path, verbose_name='物品照片', blank=True, null=True)

    love_message = models.CharField('爱心寄语', max_length=100, blank=True, null=True)
    storage_location = models.CharField('存储位置', max_length=50, blank=True, null=True)

    objects = models.Manager()
    published = PublishedItemsManager()

    # 自定义admin状态显示方法
    def Status(self):
        if self.status == '0':
            format_td = format_html('<span style="padding:2px;background-color:red;color:white">待审核&nbsp;</span>')
        elif self.status == '1':
            format_td = format_html('<span style="padding:2px;background-color:blue;color:white">暂&nbsp;&nbsp;存</span>')
        elif self.status == '2':
            format_td = format_html('<span style="padding:2px;background-color:green;color:white">捐赠完成</span>')
        return format_td

    Status.short_description = "物品状态"

    def image_tag(self):
        if self.item_image:
            return format_html('<img src="{}" height="50"/>'.format(self.item_image.url))
        else:
            return format_html('无图片')

    image_tag.short_description = '物品图片'  # 此处为了方便显示修改页面的 label 标题

    # def save(self, *args, **kwargs):
    #     print('donationItem。save（）')
    #     # 保存捐赠物品时，自动更新物品价值
    #     self.all_price = self.price * self.quantity
    #     super().save(*args, **kwargs)
    #     # 获取与该物品相关的捐赠记录对象
    #     record = self.donation_record
    #     # 获取与该记录相关的受捐项目对象
    #     project = record.donation_project
    #     # 获取该捐赠项目下所有物品
    #     items = \
    #         DonationItem.published.filter(donation_record__donation_project=project)
    #     # 计算该捐赠项目的受捐总金额
    #     project.get_donation_amount = \
    #         items.aggregate(Sum('all_price'))['all_price__sum'] or 0
    #     # 计算该捐赠记录的捐赠金额
    #     record_price = items.filter(donation_record=record) \
    #                        .aggregate(Sum('all_price'))['all_price__sum'] or 0
    #     record.donation_amount = record_price
    #     # 保存更新后的受捐项目和捐赠记录对象
    #     project.save()
    #     record.save()

    class Meta:
        verbose_name = '捐赠物资'
        verbose_name_plural = '捐赠物资'
        ordering = ['donation_record', 'status', '-all_price']

    def __str__(self):
        return f'{self.name}_{self.all_price}元_{self.donation_record.id}'


@receiver(pre_save, sender=DonationItem)
def donation_item_pre_save(sender, instance, **kwargs):
    print('DonationItem.request_item_pre_save')
    instance.all_price = instance.quantity * instance.price
    print(instance.all_price)


@receiver(post_save, sender=DonationItem)
def donation_item_save(sender, instance, **kwargs):
    print('DonationItem.request_item_save')
    record_id = instance.donation_record.id
    record = DonationRecord.objects.get(id=record_id)
    project_id = record.donation_project.id
    project = DonationProject.objects.get(id=project_id)
    print('保存前，项目筹集金额:', project.get_donation_amount)
    # 更新捐赠项目获得捐赠总价值
    project.get_donation_amount = DonationItem.published \
                                      .filter(donation_record__donation_project=project) \
                                      .aggregate(Sum('all_price'))['all_price__sum'] or 0
    print('保存后，项目筹集金额:', project.get_donation_amount)

    print('保存前，记录筹集金额:', record.donation_amount)
    # 更新捐赠记录总捐赠值
    record.donation_amount = DonationItem.published.filter(donation_record=record) \
                                 .aggregate(Sum('all_price'))['all_price__sum'] or 0
    print('保存后，记录筹集金额:', record.donation_amount)
    project.save()
    record.save()
    print('-' * 20)


@receiver(post_delete, sender=DonationItem)
def item_delete(sender, instance, **kwargs):
    # 1.删除物品对应照片文件
    # 获取要删除的物品照片路径
    if instance.item_image:
        file_path = instance.item_image.path
        # 如果物品照片存在，则删除
        if os.path.exists(file_path):
            os.remove(file_path)
        # 删除物品照片所在的文件夹
        dirs = os.path.dirname(file_path)
        if os.path.exists(dirs):
            os.rmdir(dirs)
    # 2.调用item的save方法重新计算project和record的金额
    # 使用annotate方法将donation_record字段命名为record，以便在后面的查询中使用。
    # 使用values方法将查询的结果限制为record字段。这样做是为了使查询结果中只包含不同的记录。
    # 使用distinct方法确保查询结果中只包含不同的记录。
    # 使用annotate方法在查询结果中添加first_item字段，该字段是使用子查询从每个记录的第一个item对象中获取的。
    # first_item_ids = DonationItem.published.annotate(
    #     record=F('donation_record')
    # ).values('record').distinct().annotate(
    #     first_item=Subquery(
    #         DonationItem.published.filter(donation_record=OuterRef('record')).values('id')[:1]
    #     )
    # ).values_list('first_item', flat=True)
    # # 这里使用了 values_list 方法来获取 first_item 字段的值，并将 flat 参数设置为 True 来将结果展平为一个列表。
    # # 然后，使用 filter 方法和 id__in 条件来获取所有与 first_items 中的 id 匹配的 DonationItem 对象的 QuerySet。
    # # 这样就可以方便地对每个对象进行保存。
    # first_items = DonationItem.published.filter(id__in=first_item_ids)
    # for item in first_items:
    #     print('item_image_delete:item重新保存')
    #     item.save()
    record_id = instance.donation_record.id
    project_id = instance.donation_record.donation_project.id
    record = DonationRecord.objects.get(id=record_id)
    project = DonationProject.objects.get(id=project_id)
    record.save()
    project.save()
