# Generated by Django 4.1.5 on 2023-03-02 03:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100, verbose_name='捐赠项目')),
                ('project_desc', models.CharField(max_length=200, verbose_name='项目介绍')),
                ('project_status', models.CharField(choices=[('0', '创建'), ('1', '发起'), ('2', '完成'), ('3', '截止')], max_length=10, verbose_name='项目状态')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='发起时间')),
                ('deadline', models.DateTimeField(verbose_name='截止时间')),
                ('get_donation_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='当前筹集金额')),
                ('donation_amount', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=10, verbose_name='目的捐赠价值')),
            ],
            options={
                'verbose_name': '捐赠项目',
                'verbose_name_plural': '捐赠项目',
            },
        ),
        migrations.CreateModel(
            name='DonationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donation_time', models.DateTimeField(auto_now_add=True, verbose_name='捐赠时间')),
                ('donation_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='捐赠价值')),
                ('status', models.CharField(choices=[('0', '审核'), ('1', '暂存'), ('2', '完成')], max_length=10, verbose_name='捐赠状态')),
                ('donation_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='donation.donationproject', verbose_name='所属捐赠项目')),
                ('donation_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donation_records', to=settings.AUTH_USER_MODEL, verbose_name='捐赠者')),
            ],
            options={
                'verbose_name': '捐赠记录',
                'verbose_name_plural': '捐赠记录',
            },
        ),
    ]