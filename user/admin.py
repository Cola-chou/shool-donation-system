from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from apps.user.models import MyUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm


class CustomUserAdminForm(UserChangeForm):
    # 自定义后台用户创建表单
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_superuser:
            # 如果当前用户是超级用户，则将 mobile 和 role 字段的 required 属性设为 False
            # self.fields['email'].required = False
            self.fields['role'].required = False


class MyUserAdmin(UserAdmin):
    list_display = ['username', 'password', 'role', 'mobile']
    # 自定义用户表单
    form = CustomUserAdminForm
    # 自定义用户创建表单
    add_form = UserCreationForm
    # 自定义密码修改表单类
    change_password_form = AdminPasswordChangeForm

    # 添加用户后台显示字段
    fieldsets = (
        (('个人信息'), {'fields': ('avatar','username', 'password', 'email', 'mobile',
                               'role', 'first_name', 'last_name',)}),
        (('权限'), {'fields': ('groups',)}),
    )


admin.site.register(MyUser, MyUserAdmin)
#管理后台名称
admin.site.site_header = '高校爱心捐赠系统'  # 设置header
admin.site.site_title = '高校爱心捐赠系统'   # 设置title
admin.site.index_title = '高校爱心捐赠系统'