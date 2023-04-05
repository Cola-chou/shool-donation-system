from django.core.paginator import InvalidPage
from django.views.generic import DetailView, ListView
from .models import News, Announcement
from apps.donation.models import DonationProject


class NewsListView(ListView):
    # 模型类名
    model = News
    # 模板文件名
    template_name = 'news_list.html'
    # 自定义查询上下文变量名：news_list
    context_object_name = 'news_list'
    # 开启新闻分页，每页3条新闻
    paginate_by = 3
    # 自定义管理器，只获取发布的新闻
    queryset = News.published.all()

    def paginate_queryset(self, queryset, page_size):
        """重写分页查询集方法"""
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        # 获取分页页码
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        # 页码判断逻辑
        try:
            page_number = int(page)
        except ValueError:
            # page为字符串
            if page == "last":
                page_number = paginator.num_pages
            else:
                page_number = 1
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            # page超出范围
            if page_number > paginator.num_pages:
                page_number = paginator.num_pages
                page = paginator.page(page_number)
            else:
                page_number = 1
                page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())


class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'new'
    queryset = News.published.all()

    def get_context_data(self, **kwargs):
        projects = None
        prev_news = None
        next_news = None
        context = {}
        published_news = News.published.all()  # 所有已发布的新闻
        # 新闻详情页分页
        try:
            # 获取当前新闻序号
            current_news_index = list(published_news).index(self.object)
            if current_news_index > 0:
                prev_news = published_news[current_news_index - 1]  # 上一条新闻
            if current_news_index < len(published_news) - 1:
                next_news = published_news[current_news_index + 1]  # 下一条新闻
        except ValueError:
            # 没有发布的新闻
            pass
        if self.object:
            # 获取当前新闻下所有捐赠项目
            projects = DonationProject.objects.filter(project_news_id=self.object.pk)
            print(projects)
        # 传入上下文
        context['projects'] = projects
        context['prev_news'] = prev_news
        context['next_news'] = next_news
        context.update(kwargs)
        return super(NewsDetailView, self).get_context_data(**context)


class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcement_list.html'
    context_object_name = 'announcement_list'
    queryset = Announcement.published.all()
