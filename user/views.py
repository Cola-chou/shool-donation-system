from random import randint

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .forms import MyLoginForm, MyRegistrationForm
from apps.donation.views import DonationProjectListView
# 动态获取用户模型对象,此处为MyUser
from apps.user.models import MyUser

User = get_user_model()


def index(request):
    return render(request, 'user/index.html')


class RegisterView(CreateView):
    model = MyUser
    form_class = UserCreationForm
    template_name = 'user/register.html'

    def form_valid(self, form):
        # Set custom fields from form data
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.role = form.cleaned_data['role']
        user.mobile = form.cleaned_data['mobile']
        user.address = form.cleaned_data['address']
        user.weChat = form.cleaned_data['weChat']
        user.save()
        return super().form_valid(form)


class MyLoginView(LoginView):
    authentication_form = MyLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        # 根据表单中是否勾选了 "remember me" 复选框来设置会话过期时间。
        # 调用父类的 form_valid() 方法来完成用户登录操作，并重定向到 success_url 指定的页面。
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
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
        # Add a random parameter to the success URL to prevent caching
        random_param = urlsafe_base64_encode(force_bytes(randint(1, 1000)))
        return f"{url}?r={random_param}"


class MyLogoutView(auth_views.LogoutView):
    template_name = 'registration/logged_out.html'


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'
    login_url = 'account:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        records = user.donation_records.filter(donation_user_id=user.pk)
        context['records'] = records
        # items = DonationItem.objects.filter(donation_record_id=record_id)
        # items = records.donation_items.filter(donation_record_id=)
        return context
