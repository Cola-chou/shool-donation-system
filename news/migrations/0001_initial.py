# Generated by Django 4.1.5 on 2023-03-04 03:14

import apps.news.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('donation', '0003_alter_donationrecord_donation_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='标题')),
                ('body', models.TextField(verbose_name='正文')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('image', models.ImageField(upload_to=apps.news.models.News.newsImage_directory_path, verbose_name='新闻图片')),
                ('modified_time', models.DateTimeField(verbose_name='修改时间')),
                ('news_project', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='donation.donationproject', verbose_name='所属捐赠项目')),
            ],
        ),
    ]
