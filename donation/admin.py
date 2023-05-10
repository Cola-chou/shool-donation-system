from django.contrib import admin

from apps.donation.models import DonationRecord, DonationProject
from apps.item.models import RequestItem, DonationItem
from django.contrib.admin import StackedInline
from django.core.exceptions import ObjectDoesNotExist


# 内联的请求物资操控面板
class RequestItemInline(StackedInline):
    # 继承自StackedInline
    # 当xx admin中指定了inlines = [xxInline]时
    # 内联表单将model内联至xx admin
    model = RequestItem
    min_num = 1
    extra = 0
    fields = [
        'donation_project',
        'category',
        'name',
        'detail',
        'price',
        'quantity',
        'item_image']


# 自定义捐赠项目状态选择菜单栏
class StatusSearcher(admin.SimpleListFilter):
    title = '状态'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('0', '编辑'),
            ('1', '发起'),
            ('2', '完成'),
            ('3', '截止'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project_status__icontains=self.value())
        else:
            return queryset


@admin.register(DonationProject)  # 在admin中注册捐赠项目admin
# 捐赠项目admin类
class DonationProjectAdmin(admin.ModelAdmin):
    # 内联类名：捐赠项目admin界面将会内联请求物资的admin界面
    inlines = [RequestItemInline]
    # 查询到的数据列表显示的字段
    list_display = ['id', 'project_name', 'Status', 'get_donation_amount', 'donation_amount',
                    'Speed', 'start_time', 'deadline', ]
    # 可以修改的字段
    fields = ['id','project_name', 'project_desc', 'project_status', 'project_news',
              'deadline', 'start_time']
    # 设置 列表中可点击的字段，若无list_display_links 则默认第一个字段添加a标签可点击
    list_display_links = ['project_name', ]
    # 只读不能修改的字段
    readonly_fields = ['id', 'start_time']
    # 可以通过搜索器搜索的字段
    search_fields = ("project_name",'id')
    # 自定义搜索菜单栏
    list_filter = [StatusSearcher]
    # def save_related(self, request, form, formsets, change):
    #     """
    #     在admin保存时先保存物品再保存捐赠项目
    #     """
    #     # 先保存内联表单
    #     print('save_related')
    #     for formset in formsets:
    #         self.save_formset(request, form, formset, change=change)
    #     super().save_related(request, form, formsets, change)


# 内联的捐赠物资操控面板
class DonationItemInline(StackedInline):
    model = DonationItem
    min_num = 0
    extra = 0
    readonly_fields = ['all_price']


@admin.register(DonationRecord)  # 在admin中注册捐赠记录admin
# 捐赠记录admin类
class DonationRecordAdmin(admin.ModelAdmin):
    inlines = [DonationItemInline]
    list_display = ['id','donation_user', 'donation_project', 'donation_amount', 'donation_time']
    # 设置 列表中可点击的字段，若无list_display_links 则默认第一个字段添加a标签可点击
    list_display_links = ['donation_user', ]
    readonly_fields = ['id','donation_amount']
    fields = ['id','donation_user', 'donation_project', 'donation_amount']
    actions = ['delete_selected']
    search_fields = ("donation_user__username",'donation_project__project_name','id')

    # def save_related(self, request, form, formsets, change):
    #     """
    #     在admin保存时先保存物品再保存捐赠项目
    #     """
    #     # 先保存内联表单,
    #     # 在保存item时更新record和project对象的金额值
    #     for formset in formsets:
    #         self.save_formset(request, form, formset, change=change)
    #
    #     # # 获取捐赠项目id
    #     project_id = request.POST.get('donation_project')
    #     amount = 0
    #     # 更新donation_record的donation_amount字段
    #     for item in form.instance.donation_items.all():
    #         amount += item.all_price
    #     form.instance.donation_amount = amount
    #     print('DonationRecordAdmin/', '/save_related:', amount)
    #
    #     form.instance.save()
    #     super(DonationRecordAdmin, self).save_related(request, form, formsets, change)
    #     # 获取调用此admin的record_id
    #     # record_id = form.instance.id
    #     # 获取所有审核过的捐赠物品
    #     items = DonationItem.published.all()
    #     print(list(items))
    #     if items:
    #         # 存在捐赠物品
    #         project_items = items.filter(donation_record__donation_project__id=project_id)
    #         if project_items:
    #             # 存在该捐赠项目的捐赠物品
    #             # 获取所有捐赠物品总金额
    #             total_amount = project_items.exclude(all_price=None).aggregate(total_price=Sum('all_price'))['total_price']
    #             print('donationAdmin/', 'donationRecord/', 'save_related项目受捐金额:', total_amount)
    #             # 获取记录金额
    #             amount = project_items.filter(donation_record_id=form.instance.id) \
    #                 .exclude(all_price=None).aggregate(total_price=Sum('all_price'))['total_price']
    #             print('donationAdmin/', 'donationRecord/', 'save_relate记录金额:', amount)
    #             print('DonationRecordAdmin/', '/save_related:', amount)
    #         else:
    #             # 存在通过审核的捐赠物品，但不存在该捐赠项目的通过审核的捐赠物品
    #             total_amount = 0
    #             print('存在通过审核的捐赠物品，但不存在该捐赠项目的通过审核的捐赠物品')
    #     else:
    #         # 该捐赠项目不存在通过审核的捐赠物品
    #         total_amount = 0
    #         print('该捐赠项目不存在通过审核的捐赠物品')
    #     project = DonationProject.published.get(id=project_id)
    #     project.get_donation_amount = total_amount
    #     project.save()

    def delete_selected(self, request, obj):
        # 遍历选中捐赠记录
        for o in obj:
            related_project_id = o.donation_project.id
            # 删除选中捐赠记录
            o.delete()
            try:
                records = DonationRecord.objects.filter(donation_project_id=related_project_id)
                # print(len(records))
                # print(records)
                if len(records) > 0:
                    item = records.first().donation_items.first()
                    print(item)
                    item.save()
                else:
                    project = DonationProject.published.get(id=related_project_id)
                    project.get_donation_amount = 0
                    project.save()

            except ObjectDoesNotExist:
                print('donation\\admin\\delete_selected()错误!!!')

    delete_selected.short_description = '删除所选的 捐赠记录'
