# Generated by Django 4.1.5 on 2023-03-16 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0009_rename_item_iamge_requestitem_item_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donationitem',
            options={'ordering': ['donation_record', 'status', '-all_price'], 'verbose_name': '捐赠物资', 'verbose_name_plural': '捐赠物资'},
        ),
    ]