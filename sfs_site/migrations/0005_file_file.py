# Generated by Django 2.1.5 on 2019-01-11 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfs_site', '0004_auto_20190111_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file',
            field=models.FileField(default='oops', upload_to='files'),
            preserve_default=False,
        ),
    ]
