from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from apps.user.models import MyUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm


class CustomUserAdminForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_superuser:
            # 如果当前用户是超级用户，则将 mobile 和 role 字段的 required 属性设为 False
            self.fields['mobile'].required = False
            self.fields['role'].required = False


class MyUserAdmin(UserAdmin):
    list_display = ['username', 'password', 'role', 'mobile']
    form = CustomUserAdminForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        # (None, {'fields': ('email', 'password')}),
        (('个人信息'), {'fields': ('username', 'password', 'mobile', 'role', 'first_name', 'last_name',)}),
        (('权限'), {'fields': ('groups',)}),
        # (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(MyUser, MyUserAdmin)