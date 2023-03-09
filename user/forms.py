from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MyUser

class MyLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, label='用户名或邮件')

    class Meta:
        model = MyUser
        fields = ['username', 'password']

class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='请输入一个有效的邮件地址')

    class Meta:
        model = MyUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'mobile', 'address', 'weChat']
