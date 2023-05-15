from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import News, Announcement

# 状态选择搜索器
from ..donation.models import Client


class StatusSearcher(admin.SimpleListFilter):
    '''新闻状态选择器'''
    title = '状态'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('0', '编辑'),
            ('1', '发布'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status__icontains=self.value())
        else:
            return queryset


class AnnounceStatusSearcher(StatusSearcher):
    '''公告状态选择器'''
    def lookups(self, request, model_admin):
        return [
            ('draft', '草稿'),
            ('published', '发布'),
        ]


# admin类
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'Status', 'image_tag']
    readonly_fields = ['created_time', 'image_tag']
    fields = ['title', 'status', 'body', 'image', 'created_time', 'modified_time']
    actions = ['make_published', 'make_draft']
    list_filter = [StatusSearcher]
    search_fields = ['title','']

    def image_tag(self, obj):
        return format_html('<img src="{}" height="50"/>'.format(obj.image.url))

    image_tag.short_description = '新闻配图'  # 此处为了方便显示修改页面的 label 标题

    # 自定义action
    def make_published(self, request, queryset):
        # 自定义action 发布已选择的新闻
        rows_updated = queryset.update(status='1')
        if rows_updated == 1:
            message_bit = "成功发布 1 条新闻"
        else:
            message_bit = "成功发布 %s 条新闻" % rows_updated
        self.message_user(request, "%s" % message_bit)

    make_published.short_description = "发布已选择的新闻"

    def make_draft(self, request, queryset):
        # 自定义action 将已选择的新闻变成草稿
        rows_updated = queryset.update(status='0')
        if rows_updated == 1:
            message_bit = "1 条新闻"
        else:
            message_bit = "%s 条新闻" % rows_updated
        self.message_user(request, "成功将 %s转为草稿" % message_bit)

    make_draft.short_description = "停止发布已选择的新闻"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_time', 'author']
    fields = ['title', 'status', 'content', 'author']
    actions = ['make_published', 'make_draft']
    search_fields = ['title','author__username']
    list_filter = [AnnounceStatusSearcher]

    # 自定义action
    def make_published(self, request, queryset):
        # 自定义action 发布已选择的新闻
        rows_updated = queryset.update(status='published')
        self.message_user(request, "成功发布 %s 条公告" % rows_updated)

    make_published.short_description = "发布已选择的公告"

    def make_draft(self, request, queryset):
        # 自定义action 将已选择的新闻变成草稿
        rows_updated = queryset.update(status='draft')
        self.message_user(request, "成功将 %s 条公告转为草稿" % rows_updated)

    make_draft.short_description = "停止发布已选择的公告"


