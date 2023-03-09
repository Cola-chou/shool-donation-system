# Generated by Django 4.1.5 on 2023-03-02 05:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0003_alter_requestitem_donation_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationitem',
            name='all_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.01, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, message='价值必须大于0.01')], verbose_name='价值'),
        ),
        migrations.AddField(
            model_name='requestitem',
            name='all_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.01, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, message='价值必须大于0.01')], verbose_name='价值'),
        ),
        migrations.AlterField(
            model_name='donationitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.01, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, message='单价必须大于等于0。01')], verbose_name='物品价格'),
        ),
        migrations.AlterField(
            model_name='donationitem',
            name='quantity',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='数量必须大于等于1')], verbose_name='物品数量'),
        ),
        migrations.AlterField(
            model_name='requestitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.01, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, message='单价必须大于等于0.01')], verbose_name='物品价格'),
        ),
        migrations.AlterField(
            model_name='requestitem',
            name='quantity',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='数量必须大于等于1')], verbose_name='物品数量'),
        ),
    ]