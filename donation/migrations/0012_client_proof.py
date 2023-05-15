# Generated by Django 4.1.5 on 2023-05-14 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0011_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='proof',
            field=models.FileField(default=0, upload_to='donor_proofs', verbose_name='证明文件'),
            preserve_default=False,
        ),
    ]
