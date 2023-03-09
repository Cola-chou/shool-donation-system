from django.contrib import admin

# Register your models here.
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from apps.item.models import DonationItem, RequestItem, Category
from django.db.models import Sum, ImageField
from apps.donation.models import DonationProject, DonationRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    fields = ['name', 'slug']


# @admin.register(DonationItem)
# class DonationItemAdmin(admin.ModelAdmin):
#     list_display = [
#         'donation_record',
#         'category',
#         'name',
#         'detail',
#         'price',
#         'quantity',
#         'item_image']
#     fields = [
#         'donation_record',
#         'category',
#         'name',
#         'detail',
#         'price',
#         'quantity',
#         'item_image']
#
#     def get_changeform_initial_data(self, request):
#         # admin创建物品对象页面自动填充指定字段
#         return {'name': 'itemname'}
#
# #
# def delete_selected(self, request, obj):
#     # 遍历选中捐赠记录
#     for o in obj:
#         related_record_id = o.donation_record.id
#         # 删除选中捐赠记录
#         o.delete()
#         try:
#             items = DonationItem.published.filter(donation_record_id=related_record_id)
#             record = DonationRecord.objects.get(id=related_record_id)
#             # print(len(records))
#             # print(records)
#             if len(items) > 0:
#                 item = items.first().donation_items.first()
#                 print(item)
#                 item.save()
#             else:
#                 project = DonationRecord.objects.get(id=related_record_id)
#                 project.donation_amount = 0
#                 project.save()
#
#         except ObjectDoesNotExist:
#             print('donation\\admin\\delete_selected()错误!!!')
#
# delete_selected.short_description = '删除所选的 捐赠记录'
#
# def save_related(self, request, form, formsets, change):
#     print('save_related')
#     # 保存所有的 ManyToManyField 和 ForeignKey 关联对象，
#     for formset in formsets:
#         self.save_formset(request, form, formset, change=change)
#     # 该物品的捐赠记录id
#     record_id = request.POST.get('donation_record')
#     # 获取该捐赠项目下所有物品
#     items = DonationItem.objects.filter(donation_record_id=record_id)
#     # 获取该捐赠项目下所有物品金额
#     get_total_price = items.exclude(all_price=None).aggregate(get_total_price=Sum('all_price'))['get_total_price']
#     print('itemAdmin/', 'donationItem/', 'save_related项目受捐金额:', get_total_price)
#     # 获取该捐赠项目下，该记录的物品金额
#     record_price = items.filter(donation_record_id=record_id) \
#         .exclude(all_price=None).aggregate(get_total_price=Sum('all_price'))['get_total_price']
#     print('itemAdmin/', 'donationItem/', 'save_related捐赠记录金额:', record_price)
#     # 获取与该物品相关的捐赠记录对象
#     record = DonationRecord.objects.get(id=record_id)
#     # 获取与该记录相关的受捐项目对象
#     project = record.donation_project
#     # 更新受捐项目的受捐总金额
#     project.get_donation_amount = get_total_price
#     project.save()
#     # 更新捐赠记录的捐赠金额
#     record.donation_amount = record_price
#     record.save()


@admin.register(RequestItem)
class RequestItemItemAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
    list_display = [
        'donation_project',
        'category',
        'name',
        'detail',
        'price',
        'quantity',
        'item_image',
        'all_price', ]
    fields = [
        'donation_project',
        'category',
        'name',
        'detail',
        'price',
        'quantity',
        'item_image']

    def get_changeform_initial_data(self, request):
        # admin创建物品对象页面自动填充指定字段
        return {'name': 'itemname'}

    def save_model(self, request, obj, form, change):
        """保存admin表之前，调用模型的save方法"""
        obj.save()

    def save_related(self, request, form, formsets, change):
        # print('save_related')
        # 保存所有的 ManyToManyField 和 ForeignKey 关联对象，
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        project_id = request.POST.get('donation_project')
        total_price = RequestItem.objects.exclude(all_price=None).aggregate(total_price=Sum('all_price'))['total_price']
        project = DonationProject.objects.get(id=project_id)
        project.donation_amount = total_price
        project.save()

    # 在第一段代码中（RequestItem的save方法），RequestItem 模型的 save 方法会在保存 RequestItem 对象时被自动调用。
    # 在该方法中，会自动更新 RequestItem 对象的 all_price 属性和关联的 donation_project 对象的 donation_amount 属性。
    # 由于 donation_project 是一个外键，Django 在保存 RequestItem 对象时并不会自动保存关联的 donation_project 对象。
    # 所以在这里，我们只是将更新后的 donation_project 对象保存在内存中，最终会在第二段代码中的 save_related 方法中被保存到数据库中。
    # 而在第二段代码中（RequestItemItemAdmin的save_related），RequestItemItemAdmin 类定义了 save_model 方法和 save_related 方法。当使用 Django Admin 保存 RequestItem 对象时，
    # Django 会先调用 save_model 方法，然后调用 save_related 方法。在 save_model 方法中，我们只是简单地调用了 obj.save()，这会触发 RequestItem 模型中的 save 方法。
    # 然后在 save_related 方法中，我们首先调用了 self.save_formset(request, form, formset, change=change) 来保存所有的 ManyToManyField 和 ForeignKey 关联对象，
    # 然后获取了 RequestItem 对象关联的 donation_project 对象，计算出该捐赠项目的 donation_amount，最后保存 donation_project 对象。
    # 总的来说，这两段代码共同实现了在 RequestItem 保存时自动更新关联的 donation_project 对象的 donation_amount 属性
    # 。RequestItem 模型的 save 方法中更新了 donation_project 的 donation_amount 属性，而在 RequestItemItemAdmin 类中的 save_related 方法中保存了更新后的 donation_project 对象。

    def delete_selected(self, request, obj):
        related_project_id = obj[0].donation_project.id
        # 遍历选中捐赠记录
        for o in obj:
            # 删除选中捐赠记录
            o.delete()
        print('item\\admin\\request\\delete_selected()')
        try:
            items = RequestItem.objects.filter(donation_project_id=related_project_id)
            print(items)
            project = DonationProject.published.get(id=related_project_id)
            print(project)
            if len(items) > 0:
                project.donation_amount = project.request_items \
                                              .aggregate(Sum('all_price'))['all_price__sum'] or 0
            else:
                # project = DonationProject.published.get(id=related_project_id)
                project.donation_amount = 0
            print(project.donation_amount)
            project.save()

        except ObjectDoesNotExist:
            print('item\\admin\\delete_selected()错误!!!')

    delete_selected.short_description = '删除所选的请求物资'
