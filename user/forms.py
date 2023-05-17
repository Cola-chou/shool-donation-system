import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import MyUser


class MyLoginForm(AuthenticationForm):
    # 自定义表单字段
    username = forms.CharField(max_length=254, label='用户名或邮件')
    # 表单错误信息字典
    error_messages = {
        'invalid_login': '您输入的用户名或邮箱或密码不正确，请重新输入。'
    }

    # 表单属性内部类
    class Meta:
        # 表单模型类
        model = MyUser
        # 显示的表单字段
        fields = ['username', 'password']


class MyRegistrationForm(UserCreationForm):
    # 自定义表单字段
    # GENDER_CHOICES = [('male', '男'), ('female', '女')]
    # gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect())
    email = forms.EmailField(label='邮件', max_length=254, required=True)
    mobile = forms.CharField(label='手机号码', max_length=11)

    # 重写邮件验证方法
    def clean_email(self):
        email = self.cleaned_data['email']
        if MyUser.objects.filter(email=email).exists():
            print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
            raise ValidationError('该邮箱已被注册')
        return email

    # 重写手机号码验证方法
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        # 判断手机号码是否合法，如果不合法，则抛出ValidationError异常，同时显示错误信息
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            raise ValidationError('请输入正确的手机号码')
        if MyUser.objects.filter(mobile=mobile).exists():
            print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
            raise ValidationError('该手机号码已被注册')
        return mobile

    class Meta:
        # 表单模型类
        model = MyUser
        # 显示的表单字段
        fields = ['username', 'last_name', 'first_name', 'gender', 'email', 'password1', 'password2', 'role', 'mobile', 'address', 'weChat']


class MyUserForm(forms.ModelForm):
    class Meta:
        # 表单模型类
        model = MyUser
        # 显示的表单字段
        fields = ['last_name', 'first_name', 'email', 'gender', 'avatar', 'role', 'mobile', 'address', 'weChat']
