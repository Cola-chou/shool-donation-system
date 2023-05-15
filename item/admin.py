from django.contrib import admin
from django.contrib.admin import StackedInline

from django.core.exceptions import ObjectDoesNotExist

from apps.item.models import DonationItem, RequestItem, Category, Require
from django.db.models import Sum
from apps.donation.models import DonationProject


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    fields = ['name', 'slug']


class StatusSearcher(admin.SimpleListFilter):
    # 状态选择器
    title = '状态'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('0', '待审核'),
            ('1', '暂存'),
            ('2', '捐赠完成'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status__icontains=self.value())
        else:
            return queryset


@admin.register(DonationItem)
class DonationItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'category',
        'detail',
        'quantity',
        'all_price',
        'donation_record',
        'Status',
        'image_tag',
        'storage_location'
    ]
    # 设置 列表中可点击的字段，若无list_display_links 则默认第一个字段添加a标签可点击
    list_display_links = ['name', 'donation_record', ]
    fields = [
        'id',
        'donation_record',
        'love_message',
        'storage_location',
        'category',
        'status',
        'name',
        'detail',
        'price',
        'quantity',
        'item_image'
    ]
    readonly_fields = ['id']

    # 可搜索字段，可通过'__'搜索外键字段
    search_fields = [
        'name',
        'detail',
        'category__name',
        'donation_record__donation_user__username',
        'donation_record__donation_project__project_name',
        'id',
        'storage_location'
    ]
    actions = ['make_donation_success']
    list_filter = [StatusSearcher, ]

    # 自定义修改状态action
    def make_donation_success(self, request, queryset):
        # 自定义action 改变物品状态为成功捐赠
        queryset_tmp = queryset
        # 更改选中物品状态
        # update不会触发save的信号机制,且update后queryset生成器被清空
        # 所以还要将queryset拷贝一份用于手动save
        rows_updated = queryset.update(status='2')
        for q in queryset_tmp:
            q.save()
        if rows_updated == 1:
            message_bit = "成功修改 1 件物品"
        else:
            message_bit = "成功修改 %s 件物品" % rows_updated
        self.message_user(request, "%s" % message_bit)

    make_donation_success.short_description = "完成捐赠"


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


class RequestItemProjectsSearcher(StatusSearcher):
    # 自定义搜素控件
    def lookups(self, request, model_admin):
        # 数据库选项
        project_list = DonationProject.objects.values_list('project_name')
        project_list = [(name[0], name[0]) for name in project_list]
        print('RequestItem项目选择器选项:', project_list)
        return project_list

    def queryset(self, request, queryset):
        if self.value():
            print('当前选择:', self.value())
            return queryset.filter(donation_project__project_name__icontains=self.value())
        else:
            return queryset


# # 内联的捐赠物资操控面板
class RequireInline(StackedInline):
    model = Require
    min_num = 1
    extra = 0
    fields = ['name', 'information']


@admin.register(RequestItem)
class RequestItemItemAdmin(admin.ModelAdmin):
    actions = ['delete_selected']
    list_display = [
        'name',
        'category',
        'detail',
        'price',
        'quantity',
        'image_tag',
        'all_price',
        'donation_project',
    ]
    inlines = [RequireInline]
    list_display_links = ['name', 'donation_project']
    list_filter = [RequestItemProjectsSearcher, ]
    fields = [
        'donation_project',
        'category',
        'name',
        'detail',
        'price',
        'quantity',
        'item_image'
    ]

    def get_changeform_initial_data(self, request):
        # admin创建物品对象页面自动填充指定字段
        return {'name': 'itemname'}

    def save_model(self, request, obj, form, change):
        """保存admin表之前，调用模型的save方法"""
        obj.save()

    # def save_related(self, request, form, formsets, change):
    #     # print('save_related')
    #     # 保存所有的 ManyToManyField 和 ForeignKey 关联对象，
    #     for formset in formsets:
    #         self.save_formset(request, form, formset, change=change)
    #     project_id = request.POST.get('donation_project')
    #     total_price = RequestItem.objects.exclude(all_price=None).aggregate(total_price=Sum('all_price'))['total_price']
    #     project = DonationProject.objects.get(id=project_id)
    #     project.donation_amount = total_price
    #     project.save()

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
        # 遍历选中的请求物资
        for o in obj:
            # 删除选中的请求物资
            o.delete()
            pass
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


@admin.register(Require)
class RequireAdmin(admin.ModelAdmin):
    list_display = ('request_item', 'name', 'information')
    # list_filter = ('request_item',)
    # fields = ['name', 'information']
    # readonly_fields = ['request_item']
    # search_fields = ('name', 'information')
