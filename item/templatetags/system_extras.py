from django import template
from ..models import DonationItem

register = template.Library()


@register.inclusion_tag('item/inclusions/_record_items.html', takes_context=True)
def show_record_items(context, record_id):
    items = DonationItem.objects.filter(donation_record_id=record_id)
    return {
        'items': items,
        'record_id': record_id
    }
