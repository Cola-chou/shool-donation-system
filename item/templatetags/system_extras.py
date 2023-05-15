from django import template
from django.db.models import Q

from ..models import DonationItem, RequestItem, Require
from ...donation.models import DonationProject
from django.template.defaultfilters import stringfilter
import collections

register = template.Library()


@register.inclusion_tag('item/inclusions/_record_items.html', takes_context=True)
def show_record_items(context, record_id):
    items = DonationItem.objects.filter(donation_record_id=record_id)
    return {
        'items': items,
        'record_id': record_id
    }


@register.inclusion_tag('item/inclusions/_request_items.html', takes_context=True)
def show_request_items(context, project_id, is_project_detail, is_published=False):
    # 获取请求物品集
    items = RequestItem.objects.filter(donation_project_id=project_id)
    # 装载 items_dict
    items_dict = {}
    for item in items:
        item_requirements_dict = {}
        item_requirements = Require.objects.filter(request_item=item.id)
        # 必须要判断物品是否存在图片对象
        if item.item_image:
            url = item.item_image.url
        else:
            url = ''
        for requirement in item_requirements:
            item_requirements_dict[requirement.name] = requirement.information
        item_dict = {
            'name': item.name,
            'detail': item.detail,
            'quantity': item.quantity,
            'url': url,
            'requirements': item_requirements_dict
        }
        items_dict[item.id] = item_dict
    return {
        'items_dict': items_dict,
        'project_id': project_id,
        'is_project_detail': is_project_detail,  # 此标签适用于新闻详情页和项目详情页，只在项目详情页显示捐赠按钮
        'is_published': is_published,  # 项目是否处于发布状态,截止状态不显示捐赠按钮
    }


@register.inclusion_tag('news/inclusions/_donation_users.html', takes_context=True)
def show_donation_users(context, project_id):
    """
    获取在该捐赠项目中有通过审核的捐赠物品的用户
    """
    # 限制位，只允许显示limit_number位用户
    # 且在模板中用户个数等于限制位时，会渲染 查看更多按钮
    limit_number = 42  # 限制位，只允许显示limit_number位用户
    donation_items = DonationItem.objects.filter(donation_record__donation_project_id=project_id) \
        .filter(Q(status='1') | Q(status='2'))
    users = list(set([item.donation_record.donation_user for item in donation_items]))
    print(users)
    return {
        'users': users[:limit_number],
        'project_id': project_id,
        'limit_number': limit_number,
    }


@register.filter(is_safe=True)
@stringfilter
def newslimit(value, arg):
    """
    Truncate a string after `arg` number of words.
    Remove newlines within the string.
    """
    try:
        length = int(arg)
    except ValueError:  # Invalid literal for int().
        return value  # Fail silently.
    return value[:arg] + '.....'
