from django.views.generic import ListView, DetailView
from .models import DonationProject
from apps.item.models import RequestItem


class DonationProjectListView(ListView):
    model = DonationProject
    template_name = 'donationproject_list.html'
    context_object_name = 'donation_projects'

    def get_queryset(self):
        self.queryset = DonationProject.published.all()
        return super(DonationProjectListView, self).get_queryset()


class DonationProjectDetailView(DetailView):
    model = DonationProject
    template_name = 'donationproject_detail.html'

    def get_context_data(self, **kwargs):
        # 创建新的上下文对象
        context = {}
        # 获取本捐赠项目的请求物资对象
        request_items = RequestItem.objects.filter(donation_project_id=self.object.id)
        print(request_items)
        # 打包请求对象至上下文
        context['request_items'] = request_items
        # 保存原有上下文对象
        context.update(kwargs)
        return super().get_context_data(**context)
