from django import forms
from apps.donation.models import DonationProject, DonationRecord
from .models import DonationItem, RequestItem, Category
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from ..user.models import MyUser


class DonationItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        request_id = kwargs.pop('request_id')
        project_id = kwargs.pop('project_id')
        user_id = kwargs.pop('user_id')
        self.request_item = get_object_or_404(RequestItem,
                                              id=request_id)
        self.user = get_object_or_404(MyUser,
                                      id=user_id)
        self.project = get_object_or_404(DonationProject,
                                         id=project_id)
        super().__init__(*args, **kwargs)

    # def clean_name(self):
    #     name = self.cleaned_data['name']
    def clean(self):
        # 验证失败标志
        valid_flag = True
        # lambda函数：物品名称预填充
        has_rmb = lambda text: '人民币' if '人民币' in text else f'xx{text},xx型号'
        # 原有的表单验证
        cleaned_data = super(DonationItemForm, self).clean()
        # 获取表单的name,deatail字段
        name = cleaned_data.get('name')
        detail = cleaned_data.get('detail')
        # 验证name和detail字段是否修改预填充文字
        if self.cleaned_data['name'] == has_rmb(self.request_item.category.name) \
                and self.request_item.category.name != '人民币':
            self.add_error('name', f'请将xx替换为自己的物品')
            valid_flag = False
        if self.cleaned_data['detail'] == has_rmb(self.request_item.category.name) \
                and self.request_item.category.name != '人民币':
            self.add_error('detail', f'请将xx替换为自己的描述')
            valid_flag = False
        if valid_flag:
            # 验证成功
            # 创建
            category = get_object_or_404(Category,
                                         id=self.request_item.category.id)
            price = self.request_item.price
            quantity = self.cleaned_data['quantity']
            image = self.cleaned_data['item_image']
            # 创建DonationItem对象
            donation_item = DonationItem(
                name=name,
                detail=detail,
                quantity=quantity,
                category=category,
                price=price,
                item_image=image
            )
            # 已存在记录
            try:
                exist_record = DonationRecord.objects.get(donation_user_id=self.user.id,
                                                          donation_project_id=self.project.id)
                donation_item.donation_record = exist_record
                donation_item.save()
            except ObjectDoesNotExist:
                # 创建DonationRecord对象
                donation_record = DonationRecord(
                    donation_user=self.user,
                    donation_project=self.project,
                    status='0'
                )

                # 将DonationItem对象和DonationRecord对象关联
                donation_item.donation_record = donation_record

                # 保存DonationRecord对象和DonationItem对象到数据库中
                donation_record.save()
                donation_item.save()
        return cleaned_data

    class Meta:
        model = DonationItem
        fields = ['name', 'detail', 'quantity', 'item_image']
        widgets = {
            'price': forms.HiddenInput(attrs={'value': RequestItem.price}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }


class DonationItemChangeForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     user_id = kwargs.pop('user_id')
    #     self.user = get_object_or_404(MyUser,
    #                                   id=user_id)
    #     self.project = get_object_or_404(DonationProject,
    #                                      id=self.request_item.donation_project_id)
    #     super().__init__(*args, **kwargs)

    # def clean(self):
    #     # 验证失败标志
    #     valid_flag = True
    #     # lambda函数：物品名称预填充
    #     has_rmb = lambda text: '人民币' if '人民币' in text else f'xx{text},xx型号'
    #     # 原有的表单验证
    #     cleaned_data = super(DonationItemChangeForm, self).clean()
    #     # 获取表单的name,deatail字段
    #     name = cleaned_data.get('name')
    #     detail = cleaned_data.get('detail')
    #     # 验证name和detail字段是否修改预填充文字
    #     if self.cleaned_data['name'] == has_rmb(self.request_item.category.name) \
    #             and self.request_item.category.name != '人民币':
    #         self.add_error('name', f'请将xx替换为自己的物品')
    #         valid_flag = False
    #     if self.cleaned_data['detail'] == has_rmb(self.request_item.category.name) \
    #             and self.request_item.category.name != '人民币':
    #         self.add_error('detail', f'请将xx替换为自己的描述')
    #         valid_flag = False
    #     if valid_flag:
    #         # 验证成功
    #         # 创建
    #         category = get_object_or_404(Category,
    #                                      id=self.request_item.category.id)
    #         price = self.request_item.price
    #         quantity = self.cleaned_data['quantity']
    #         image = self.cleaned_data['item_image']
    #         # 创建DonationItem对象
    #         donation_item = DonationItem(
    #             name=name,
    #             detail=detail,
    #             quantity=quantity,
    #             category=category,
    #             price=price,
    #             item_image=image
    #         )
    #         # 已存在记录
    #         try:
    #             exist_record = DonationRecord.objects.get(donation_user_id=self.user.id,
    #                                                       donation_project_id=self.project.id)
    #             donation_item.donation_record = exist_record
    #             donation_item.save()
    #         except ObjectDoesNotExist:
    #             # 创建DonationRecord对象
    #             donation_record = DonationRecord(
    #                 donation_user=self.user,
    #                 donation_project=self.project,
    #                 status='0'
    #             )
    #
    #             # 将DonationItem对象和DonationRecord对象关联
    #             donation_item.donation_record = donation_record
    #
    #             # 保存DonationRecord对象和DonationItem对象到数据库中
    #             donation_record.save()
    #             donation_item.save()
    #     return cleaned_data

    class Meta:
        model = DonationItem
        fields = ['name', 'detail', 'quantity', 'item_image']
        widgets = {
            'price': forms.HiddenInput(attrs={'value': DonationItem.price}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }
