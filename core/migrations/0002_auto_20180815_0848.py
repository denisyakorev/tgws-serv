# Generated by Django 2.0.8 on 2018-08-15 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='content_xml',
            field=models.BinaryField(blank=True, verbose_name='XML содержимое'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='content_xml',
            field=models.BinaryField(blank=True, verbose_name='XML содержимое'),
        ),
        migrations.AlterField(
            model_name='tempmodule',
            name='content_xml',
            field=models.BinaryField(blank=True, verbose_name='XML содержимое'),
        ),
    ]
