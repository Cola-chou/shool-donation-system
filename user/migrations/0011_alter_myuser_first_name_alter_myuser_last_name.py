# Generated by Django 4.1.5 on 2023-05-18 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_myuser_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=20, verbose_name='名'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=20, verbose_name='姓'),
        ),
    ]