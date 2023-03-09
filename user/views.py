from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
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
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


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
        # items = records.donation_items.filter(donation_record_id=)
        return context
