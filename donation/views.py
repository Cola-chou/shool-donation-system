from datetime import datetime
import logging
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db import models
from django.db.models import Q, Case, When
from django.utils import timezone
from django.views.generic import ListView, DetailView
from .models import DonationProject
from apps.item.models import RequestItem, DonationItem
from operator import itemgetter
from django.db.models import Q
from django.contrib import messages


class DonationProjectListView(ListView):
    # 数据模型类
    model = DonationProject
    # 数据渲染的模板文件名
    template_name = 'donationproject_list.html'
    # 自定义 返回给前端的上下文变量名称为donation_projects
    # 否则为object
    context_object_name = 'donation_projects'
    # 分页页数设置
    paginate_by = 4
    extra_context = {'number': None, 'q': None}
    # 自定义查询集：获取所有状态为发起，完成和截止的捐赠项目
    donation_projects = DonationProject.objects.all()
    # 使用Case和When表达式对状态和创建时间进行排序
    donation_projects = donation_projects.annotate(
        is_finished=Case(
            When(project_status='3', then=1),
            default=0,
            output_field=models.IntegerField(),
        )
    ).order_by('is_finished', '-start_time')
    queryset = donation_projects

    # def get(self, request, *args, **kwargs):
    #    return super(DonationProjectListView, self).get(request)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        self.extra_context.update(number=queryset.count())
        self.extra_context.update(q=None)
        print(f'搜索执行前：{self.extra_context}')
        print(f'打印query:{query}')
        if query:
            if '发起' == query:
                temp = query
                query = '1'
                queryset = queryset.filter(Q(project_status__contains=query))
                query = temp
            elif '完成' == query:
                temp = query
                query = '2'
                queryset = queryset.filter(Q(project_status__contains=query))
                query = temp
            elif '截止' == query:
                temp = query
                query = '3'
                queryset = queryset.filter(Q(project_status__contains=query))
                query = temp
            else:
                print('普通搜索')
                queryset = queryset.filter(Q(project_name__icontains=query))
                # query参数会被自动转义以防止注入攻击。在内部，Django ORM会将查询字符串中的特殊字符
                # （如单引号、双引号等）进行转义，从而使其变成安全的查询条件。
            self.extra_context.update(number=queryset.count(), q=query)
        print(f'搜索执行后：{self.extra_context}')
        print(f' DonationProjectListView.get_queryset '.join(['******'] * 2))
        return queryset.annotate(
            is_finished=Case(
                When(project_status='3', then=1),
                default=0,
                output_field=models.IntegerField(),
            )
        ).order_by('is_finished', '-start_time')


class DonationProjectDetailView(DetailView):
    model = DonationProject
    template_name = 'donationproject_detail.html'
    queryset = DonationProject.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 获取本捐赠项目的请求物资对象
        request_items = RequestItem.objects \
            .filter(donation_project_id=self.object.id)
        news = self.object.project_news

        # 获取该项目所有捐赠物品：暂存，捐赠成功
        donation_items = DonationItem.objects \
            .filter(donation_record__donation_project_id=self.object.id) \
            .filter(Q(status='1') | Q(status='2'))
        # 获取捐赠用户
        users = list(set([item.donation_record.donation_user for item in donation_items]))

        # 获取每个用户的捐款总金额
        results = []
        for user in users:
            # 获取一个字典：用户在某捐赠项目中捐赠的总价值和物品列表
            user_donation_x = user.get_donations_for_project(self.object.id)
            total_amount = user_donation_x['total_amount']
            items = user_donation_x['items']
            result = {'user': user, 'total_amount': total_amount, 'items': items}
            results.append(result)

        # 按照总金额从高到低排序
        # itemgetter('total_amount') 创建了一个函数对象，该函数可用于从字典中获取 'total_amount' 键对应的值。
        # 这里使用 operator 模块中的 itemgetter 函数来简化代码。
        # itemgetter 的作用是获取一个可迭代对象中每个元素的指定位置的元素，并返回这些元素组成的元组。
        # reverse=True 参数表示按照降序排序
        # sorted_results 中每个字典表示一个用户的捐款记录和捐款总金额，且按照total_amount的从高到低排列
        sorted_results = sorted(results, key=itemgetter('total_amount'), reverse=True)

        # 分页器
        paginator = Paginator(sorted_results, 4)

        # 获取当前页码
        page = self.request.GET.get('page')
        try:
            # 获取当前页的结果
            results = paginator.page(page)
        except PageNotAnInteger:
            # 如果页码不是一个整数，则显示第一页的结果
            results = paginator.page(1)
        except EmptyPage:
            # 如果页码超出范围，则显示最后一页的结果
            results = paginator.page(paginator.num_pages)

            # 将重新组织的结果列表传递给模板
        count = round(self.object.get_donation_amount / self.object.donation_amount * 100)
        context['count'] = count
        context['news'] = news
        context['request_items'] = request_items
        context['results'] = results
        context['paginator'] = paginator
        return context


'''
date：在您希望在某个特定时间仅运行一次作业时使用
interval：当您要以固定的时间间隔运行作业时使用
cron：以crontab的方式运行定时任务
minutes：设置以分钟为单位的定时器
seconds：设置以秒为单位的定时器
'''


def check_expired_projects():
    # 检查过期的捐赠项目
    print('xxxxxxxxxxxxxxxxxxx检查过期项目xxxxxxxxxxxxxxxxxxxxxxx')
    print('当前时间:{}'.format(timezone.now()))
    # 获取当前时间
    now = timezone.now()
    # 查询所有过期的捐赠项目
    projects = DonationProject.objects.filter(deadline__lt=now)
    # 遍历过期捐赠项目，修改状态为截止态，对应字符编码为 3
    for project in projects:
        if project.project_status == '1' \
                and project.get_donation_amount < project.donation_amount:
            print(project.project_status)
            project.project_status = '3'
            project.save()
