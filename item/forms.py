from django import forms
from django.shortcuts import get_object_or_404

from apps.donation.models import DonationProject, DonationRecord
from .models import DonationItem, RequestItem
from ..user.models import MyUser


class DonationItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # 从参数字典中获取关键值
        request_id = kwargs.pop('request_id')
        project_id = kwargs.pop('project_id')
        item_detail = kwargs.pop('item_detail')
        user_id = kwargs.pop('user_id')
        # 根据关键值创建对象
        self.request_item = get_object_or_404(RequestItem,
                                              id=request_id)
        self.user = get_object_or_404(MyUser,
                                      id=user_id)
        self.item_detail = item_detail
        self.project = get_object_or_404(DonationProject,
                                         id=project_id)
        super().__init__(*args, **kwargs)

        # 添加支付方式选项
        if self.request_item.category.name == '人民币':
            self.fields['payment_method'] = forms.ChoiceField(
                choices=[('alipay', '支付宝捐赠'), ('offline', '线下捐赠')],
                widget=forms.RadioSelect,
                label='提交方式',
                initial='offline'  # 设置initial为'offline'
            )

    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if not payment_method:
            raise forms.ValidationError('请选择一个选项')
        return payment_method

    def clean(self):
        # 原有的表单验证
        cleaned_data = super(DonationItemForm, self).clean()
        # 验证成功
        # 获取请求物品信息
        name = cleaned_data.get('name')
        quantity = self.cleaned_data['quantity']
        detail = cleaned_data.get('detail')
        if detail == self.item_detail:
            detail = detail + f'x{quantity}'
        category = self.request_item.category
        price = self.request_item.price
        image = self.cleaned_data['item_image']
        love_message = self.cleaned_data['love_message']
        # 创建DonationItem对象
        donation_item = DonationItem(
            name=name,
            detail=detail,
            quantity=quantity,
            category=category,
            price=price,
            item_image=image,
            love_message=love_message
        )
        # 若用户在此项目中存在捐赠记录，则更新捐赠记录
        # 否则创建一条新的记录
        exist_record, create = DonationRecord.objects.get_or_create(donation_user_id=self.user.id,
                                                                    donation_project_id=self.project.id)
        # 返回的create为真，不存在原纪录，创建新的记录对象
        # 返回的create为假，存在原纪录
        print(f'是否新建记录对象：', create)
        if create:
            print(exist_record)
            exist_record.save()
        donation_item.donation_record = exist_record
        donation_item.save()
        # 传递创建物品id供支付宝对接使用
        cleaned_data.update({'id': donation_item.id})
        # cleaned_data.update({'id': 1})
        return cleaned_data

    class Meta:
        model = DonationItem
        fields = ['name', 'detail', 'quantity', 'love_message', 'item_image']
        widgets = {
            'detail': forms.Textarea(attrs={'style': 'width: 400px; height: 100px'}),
            'price': forms.HiddenInput(attrs={'value': RequestItem.price}),  # 模板该字段渲染时隐藏
            'storage_location': forms.HiddenInput(attrs={'value': ''}),  # 模板该字段渲染时隐藏
            'quantity': forms.NumberInput(attrs={'min': 1}),  # 模板渲染该字段为数字类型
        }


class DonationItemChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # 从参数字典中获取关键值
        print(kwargs, args)
        is_money = kwargs.pop('is_money', False)
        print(f'is_money:{is_money}')
        super().__init__(*args, **kwargs)
        # 添加支付宝支付选项
        # 添加支付方式选项
        if is_money:
            self.fields['payment_method'] = forms.ChoiceField(
                choices=[('alipay', '支付宝捐赠'), ('offline', '线下捐赠')],
                widget=forms.RadioSelect,
                label='提交方式',
                initial='offline'  # 设置initial为'offline'
            )

    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if not payment_method:
            raise forms.ValidationError('请选择一个选项')
        return payment_method

    class Meta:
        model = DonationItem
        fields = ['name', 'detail', 'quantity', 'love_message', 'item_image']
        widgets = {
            'price': forms.HiddenInput(attrs={'value': DonationItem.price}),
            'storage_location': forms.HiddenInput(attrs={'value': ''}),  # 模板该字段渲染时隐藏
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }
