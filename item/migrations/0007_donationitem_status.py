# Generated by Django 4.1.5 on 2023-03-07 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0006_alter_donationitem_all_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationitem',
            name='status',
            field=models.CharField(blank=True, choices=[('0', '待审核'), ('1', '暂存'), ('2', '捐赠成功')], default='0', max_length=10, verbose_name='状态'),
        ),
    ]