# Generated by Django 4.1.5 on 2023-03-16 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0006_alter_donationrecord_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donationrecord',
            name='status',
        ),
        migrations.AlterField(
            model_name='donationproject',
            name='project_status',
            field=models.CharField(choices=[('0', '编辑'), ('1', '发起'), ('2', '完成'), ('3', '截止')], default='0', max_length=10, verbose_name='项目状态'),
        ),
    ]