import pandas as pd
from django.contrib import admin
from django.http import HttpResponse
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime, time

from apps.donation.models import DonationRecord, DonationProject, Client
from apps.item.models import RequestItem, DonationItem
from django.contrib.admin import StackedInline
import pytz


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


def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="my_projects_{}.xlsx"'.format(datetime.now().strftime('%Y-%m-%d %H-%M-%S'))

    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    # Add headers to the worksheet based on the model fields
    headers = [field.verbose_name.capitalize() for field in queryset.model._meta.fields]
    ws.append(headers)

    # Add data to the worksheet
    data = get_export_data(queryset)
    for row in data:
        ws.append(row)

    # Save the workbook to the response
    wb.save(response)

    # Close the workbook to release resources
    wb.close()

    return response


def get_export_data(queryset):
    # fields = ['deadline', 'donation_amount', 'donation_records', 'get_donation_amount', 'id', 'project_client', 'project_client_id', 'project_desc', 'project_name',
    #           'project_news', 'project_news_id', 'project_status', 'request_items', 'start_time']
    fields = [field.name for field in queryset.model._meta.fields]
    foreign_key_fields = [field.name for field in queryset.model._meta.fields if field.get_internal_type() == 'ForeignKey']
    data = []
    for obj in queryset.values(*fields).iterator():
        row = []
        for field_name in fields:
            if field_name in foreign_key_fields:
                # related_field_name = f"{field_name}__id"
                # # project = DonationProject.objects.get(id=obj.get('id')).
                # locale = {'field_name': field_name}
                # 动态转换
                # 使用了compile函数将字符串表达式编译成字节码对象，并使用eval函数在运行时评估该对象。
                # compile函数的第二个参数是一个文件名，用于显示错误消息中的文件名，而第三个参数是编译模式，它指定编译的类型（例如，'eval'表示对单个表达式进行评估）。
                code = compile(f"DonationProject.objects.get(id=obj.get('id')).{field_name}", '<string>', 'eval')
                value = str(eval(code))
                print(f'外键:{value}')
                if value == 'None':
                    value = ''
                    print(f'外键-:{value}')
            else:
                value = obj[field_name]
            if isinstance(value, datetime) or isinstance(value, time):
                value = value.replace(tzinfo=None)
            print(value)
            row.append(value)
        data.append(row)
    return data


export_to_excel.short_description = '导出为Excel表格'


@admin.register(DonationProject)  # 在admin中注册捐赠项目admin
# 捐赠项目admin类
class DonationProjectAdmin(admin.ModelAdmin):
    # 内联类名：捐赠项目admin界面将会内联请求物资的admin界面
    inlines = [RequestItemInline]
    actions = [export_to_excel]
    # 查询到的数据列表显示的字段
    list_display = ['id', 'project_name', 'Status', 'get_donation_amount', 'donation_amount',
                    'Speed', 'start_time', 'deadline', 'project_client_link']
    # 可以修改的字段
    fields = ['id', 'project_client', 'project_name', 'project_desc', 'project_status', 'project_news',
              'deadline', 'start_time']
    # 设置 列表中可点击的字段，若无list_display_links 则默认第一个字段添加a标签可点击
    list_display_links = ['project_name']
    # 只读不能修改的字段
    readonly_fields = ['id', 'start_time']
    # 可以通过搜索器搜索的字段
    search_fields = ("project_name", 'id', 'project_client')
    # 自定义搜索菜单栏
    list_filter = [StatusSearcher]



# 内联的捐赠物资操控面板
class DonationItemInline(StackedInline):
    model = DonationItem
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


@admin.register(DonationRecord)  # 在admin中注册捐赠记录admin
# 捐赠记录admin类
class DonationRecordAdmin(admin.ModelAdmin):
    inlines = [DonationItemInline]
    list_display = ['id', 'donation_user', 'donation_project', 'donation_amount', 'donation_time']
    # 设置 列表中可点击的字段，若无list_display_links 则默认第一个字段添加a标签可点击
    list_display_links = ['donation_user', ]
    readonly_fields = ['id', 'donation_amount']
    fields = ['id', 'donation_user', 'donation_project', 'donation_amount']
    actions = ['delete_selected']
    search_fields = ("donation_user__username", 'donation_project__project_name', 'id')


class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact', 'address', 'is_organization', 'organization_name', 'view_pdf_out']
    list_display_links = ['name']
    fields = ['name', 'contact', 'address', 'proof', 'is_organization', 'organization_name', 'view_pdf_in']
    readonly_fields = ['view_pdf_in']
    search_fields = ['name', 'organization_name']

    def pdf_link(self, obj):
        return obj.pdf_link()


admin.site.register(Client, ClientAdmin)
