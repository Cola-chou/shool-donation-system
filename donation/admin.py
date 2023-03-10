from django.contrib import admin

from apps.donation.models import DonationRecord, DonationProject
from apps.item.models import RequestItem, DonationItem
from django.contrib.admin import StackedInline
from django.core.exceptions import ObjectDoesNotExist


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


@admin.register(DonationProject)
class DonationProjectAdmin(admin.ModelAdmin):
    inlines = [RequestItemInline]
    list_display = ['project_name', 'project_status', 'get_donation_amount', 'donation_amount', 'start_time', 'deadline', ]
    fields = ['project_name', 'project_desc', 'project_status', 'project_news',
              'deadline', 'start_time']
    # fields = [f.name for f in DonationProject._meta.get_fields() if f.name not in ('donationrecords', 'donation_items','records')]
    readonly_fields = ['start_time']

    # def save_related(self, request, form, formsets, change):
    #     """
    #     在admin保存时先保存物品再保存捐赠项目
    #     """
    #     # 先保存内联表单
    #     print('save_related')
    #     for formset in formsets:
    #         self.save_formset(request, form, formset, change=change)
    #     super().save_related(request, form, formsets, change)


class DonationItemInline(StackedInline):
    model = DonationItem
    min_num = 0
    extra = 0
    readonly_fields = ['all_price']


@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    inlines = [DonationItemInline]
    list_display = ['donation_user', 'donation_project', 'donation_amount', 'donation_time']
    readonly_fields = ['donation_amount']
    fields = ['status', 'donation_user', 'donation_project', 'donation_amount']
    actions = ['delete_selected']


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
