from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'image_tag']
    readonly_fields = ['created_time', 'image_tag']
    fields = ['title', 'status', 'body', 'image', 'created_time', 'modified_time']

    def image_tag(self, obj):
        return format_html('<img src="{}" height="50"/>'.format(obj.image.url))

    image_tag.short_description = '新闻配图'  # 此处为了方便显示修改页面的 label 标题
