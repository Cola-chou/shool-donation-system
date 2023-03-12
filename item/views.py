import os
import shutil

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.forms import model_to_dict
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import ListView, DetailView

from .forms import DonationItemForm, DonationItemChangeForm
from .models import DonationItem, RequestItem
from apps.donation.models import DonationProject, DonationRecord
from django.shortcuts import render, redirect, get_object_or_404


@login_required(login_url='account:login')
def record_items(request, record_id):
    items = DonationItem.objects.filter(donation_record_id=record_id)
    return render(request, 'record_items_list.html', context={'items': items,
                                                              'record_id': record_id})


@login_required(login_url='account:login')
def donation_item_create(request, request_id, project_id):
    # lambda函数：物品名称预填充
    has_rmb = lambda text: '人民币' if '人民币' in text else f'xx{text},xx型号'
    # 请求物资对象
    request_item = get_object_or_404(RequestItem,
                                     id=request_id)
    user_id = request.user.id
    print(request_item)
    if request.method == 'POST':
        form = DonationItemForm(request.POST,
                                request.FILES,
                                request_id=request_id,
                                user_id=user_id,
                                project_id=project_id)
        if form.is_valid():
            # 处理表单提交
            return redirect('donation:project_detail', pk=project_id)
    else:
        initial = {
            'price': request_item.price,
            'name': has_rmb(request_item.category.name),
            'detail': has_rmb(request_item.category.name)
        }
        form = DonationItemForm(initial=initial,
                                request_id=request_id,
                                user_id=user_id,
                                project_id=project_id)

    context = {'form': form}
    if form.errors:
        context['post_data'] = request.POST
    return render(request, 'donation_item_create.html', context)


@login_required(login_url='account:login')
def donation_item_change(request, item_id, record_id):
    # lambda函数：物品名称预填充
    has_rmb = lambda text: '人民币' if '人民币' in text else f'xx{text},xx型号'
    # 请求物资对象
    donation_item = get_object_or_404(DonationItem,
                                      id=item_id)
    user_id = request.user.id
    print(donation_item)
    if request.method == 'POST':
        form = DonationItemChangeForm(request.POST,
                                      request.FILES)
        if form.is_valid():
            # 假设新图片的文件名为 new_image.jpg
            try:
                new_image = ContentFile(request.FILES['item_image'].read(), name=request.FILES['item_image'])
            except MultiValueDictKeyError:
                new_image = None
            # if donation_item.item_image:
            # 将新图片保存到原来的位置
            if new_image:
                dirs = f'donationItems_image' \
                       f'/{DonationRecord.objects.get(id=record_id).donation_project.id}' \
                       f'/{record_id}/{item_id}'
                dirs = os.path.join(settings.MEDIA_ROOT, dirs)
                if os.path.exists(dirs):
                    shutil.rmtree(dirs)
                os.makedirs(dirs)
            # default_storage.save(dirs, new_image)
            # 处理表单提交
            data = {
                'name': form.cleaned_data['name'],
                'detail': form.cleaned_data['detail'],
                'quantity': form.cleaned_data['quantity'],
                'category': donation_item.category,
                'price': donation_item.price,
                'item_image': form.cleaned_data['item_image'],
                'donation_record': donation_item.donation_record,
                'all_price': form.cleaned_data['quantity'] * donation_item.price,
            }
            # 更新DonationItem对象
            DonationItem.objects.filter(id=item_id).update(**data)
            donation_item = DonationItem.objects.get(id=item_id)
            if new_image:
                donation_item.item_image = new_image
                donation_item.item_image.name = new_image.name
                # donation_item.item_image.path = dirs
                donation_item.save(update_fields=['name'])
                donation_item.save()

            return redirect('item:record_items_list', record_id)
    else:
        # get请求
        if donation_item.status != '0':
            # 非法get请求，用户只能修改未审核过的物品
            return redirect('account:profile')
        form = DonationItemChangeForm(instance=donation_item)

    context = {'form': form}
    if form.errors:
        context['post_data'] = request.POST
    return render(request, 'donation_item_create.html', context)


class DonationItemListView(ListView):
    model = DonationItem
    template_name = 'record_items_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return super().get_queryset().filter(status='')
