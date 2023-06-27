import os
from operator import itemgetter
from random import randint

import pdfkit
import weasyprint
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from mysystem import settings
from .forms import MyLoginForm, MyRegistrationForm, MyUserForm

# 动态获取用户模型对象,此处为MyUser
from apps.user.models import MyUser
from ..donation.models import DonationRecord, DonationProject
from ..item.models import DonationItem

User = get_user_model()


def index(request):
    return render(request, 'user/index.html')


def url_fetcher(url):
    if url.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, url.replace(settings.MEDIA_URL, ''))
        with open(path, 'rb') as f:
            return dict(string=f.read(), mime_type='image/jpeg')
    else:
        return weasyprint.default_url_fetcher(url)



from django.http import HttpResponse


def create_pdf(request, self=None):
    # 获取用户所有的通过审核的捐赠物品
    items = DonationItem.published.filter(donation_record__donation_user_id=request.user.id)

    if items:
        # 获得该用户参与的所有的捐赠项目
        projects = DonationProject.objects.filter(donation_records__donation_user_id=request.user.id)

        # 获取用户捐赠的所有通过审核物品的总金额
        total_amount = DonationItem.published.filter(donation_record__donation_user_id=request.user.id).aggregate(Sum('all_price'))['all_price__sum'] or 0

        result = {}  # 存储项目名称及其对应的捐赠物品列表
        for project in projects:
            donation_items = items.filter(donation_record__donation_project=project)
            if donation_items:
                project_total_amount = donation_items.aggregate(Sum('all_price'))['all_price__sum'] or 0
                result[project.project_name] = {
                    'donation_items': donation_items,
                    'total_amount': project_total_amount
                }

        # print(result)
        # return render(request, 'E:\\DJANGO\\universityDonationSystem\\mysystem\\apps\\user\\templates\\user\\pdf.html', locals())

        # return HttpResponse('ok')
        # 生成pdf页面
        html = render_to_string('user/pdf.html',
                                {
                                    # 'projects': projects,
                                    # 'items': items,
                                    'result': result,
                                    'total_amount': total_amount,
                                    'user': request.user,
                                    # 'time': timezone.now()
                                })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename={}的捐赠证书.pdf'.format(request.user.username)
        weasyprint.HTML(string=html).write_pdf(response,
                                               stylesheets=[
                                                   #     # weasyprint.CSS('..css/pdf.css')
                                               ], )
        return response
    else:
        messages.success(request, '未查询到您的捐赠记录！')
        return redirect('account:profile')


class RegisterView(CreateView):
    # 模型类
    model = MyUser
    # 自定义表单类
    form_class = MyRegistrationForm
    # 模板文件名
    template_name = 'user/register.html'
    # 注册成功重定向
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # 自定义表单验证
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.gender = form.cleaned_data['gender']
        print(f'性别：{user.gender}')
        user.role = form.cleaned_data['role']
        user.mobile = form.cleaned_data['mobile']
        user.address = form.cleaned_data['address']
        user.weChat = form.cleaned_data['weChat']
        user.save()

        # 将用户添加至普通用户组
        group = Group.objects.get(name='普通用户')
        user.groups.add(group)

        # 父类表单验证
        return super().form_valid(form)


class MyLoginView(LoginView):
    # 自定义表单类
    authentication_form = MyLoginForm
    # 模板名
    template_name = 'registration/login.html'
    # 登录成功跳转至主页或者物品捐赠页面
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        """自定义表单验证方法"""
        # 根据表单中是否勾选了 "remember me" 复选框来设置会话过期时间。
        # 调用父类的 form_valid() 方法来完成用户登录操作，并重定向到 success_url 指定的页面。
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(1209600)  # 账号密码存储在session中2周
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        # 这将检查用户是否已经通过身份验证，如果是，则自动重定向到成功 URL。
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super(MyLoginView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # 在这个代码中，我重写了 get_success_url 方法，并在成功 URL 中添加了一个名为 r 的随机参数。
        # 这个随机参数的值是一个随机生成的整数，
        # 通过 base64 编码后作为 URL 的一部分。这样做可以确保每次访问成功 URL 时，URL 都不同，从而避免浏览器缓存该页面。
        url = super().get_success_url()
        # 返回随机数避免缓存
        random_param = urlsafe_base64_encode(force_bytes(randint(1, 1000)))
        return f"{url}?r={random_param}"


class MyLogoutView(LogoutView):
    template_name = 'registration/logged_out.html'


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'
    login_url = 'account:login'

    def get_context_data(self, **kwargs):
        # 继承父级上下文内容
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # 获取用户的所有捐赠记录
        records = user.donation_records.filter(donation_user_id=user.pk)
        # 循环遍历每个 DonationRecord 对象
        for record in records:
            # 获取该记录中未通过审核的物品数量和通过物品的数量
            all_items_count = record.donation_items.all().count
            unchecked_items_count = record.donation_items.filter(status='0').count()
            checked_items_count = record.donation_items.filter(status__in=['1', '2']).count()
            # 将该记录的检查数量和已检查数量添加为属性
            record.check_number = unchecked_items_count  # 待审核的物品数量
            record.checked_number = checked_items_count  # 审核通过的物品数量
            record.all_items_count = all_items_count  # 总的物品数量
        # 聚合查找出用户的总捐赠价值
        total_donation_amount = records.aggregate(Sum('donation_amount'))['donation_amount__sum']
        # 将自定义的记录变量和用户总捐赠价值加入上下文
        context['records'] = records
        context['total_donation_amount'] = total_donation_amount
        print('MyProfileView.get_context_data.total_donation_amount:', total_donation_amount)
        return context


class MyUserUpdateView(LoginRequiredMixin, UpdateView):
    model = MyUser
    form_class = MyUserForm
    template_name = 'user/user_form.html'
    success_url = reverse_lazy('account:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


import random
from django.core.mail import send_mail


def send_verification_code(request):
    email = request.POST.get('email')
    if not email:
        return HttpResponseBadRequest('请输入邮箱')
    verification_code = str(random.randint(1000, 9999))
    send_mail(
        '验证码',
        f'您的验证码是：{verification_code}',
        'service@example.com',  # 发送方邮件地址
        [email],  # 接收方邮件地址
        fail_silently=False,
    )
    return JsonResponse({'status': 'ok'})
