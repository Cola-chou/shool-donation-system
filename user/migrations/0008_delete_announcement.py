# Generated by Django 4.1.5 on 2023-03-16 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_myuser_avatar'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Announcement',
        ),
    ]