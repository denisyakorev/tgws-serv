# Generated by Django 2.0.8 on 2018-08-11 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tech_name', models.CharField(blank=True, max_length=200, verbose_name='полное название')),
                ('title', models.CharField(max_length=200, verbose_name='название')),
                ('file_name', models.CharField(blank=True, max_length=200, verbose_name='имя файла')),
                ('issue_number', models.CharField(blank=True, max_length=200, verbose_name='номер версии')),
                ('content_xml', models.TextField(blank=True, verbose_name='XML содержимое')),
                ('content_json', models.TextField(blank=True, verbose_name='JSON содержимое')),
                ('is_category', models.BooleanField(default=False, verbose_name='категория')),
            ],
            options={
                'verbose_name': 'модуль',
                'verbose_name_plural': 'модули',
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='название')),
                ('code', models.CharField(max_length=200, unique=True, verbose_name='код')),
                ('file_name', models.CharField(max_length=200, verbose_name='имя файла')),
                ('issue_number', models.CharField(blank=True, max_length=200, verbose_name='номер версии')),
                ('content_xml', models.TextField(blank=True, verbose_name='XML содержимое')),
                ('structure_json', models.TextField(blank=True, verbose_name='JSON cтруктура')),
            ],
            options={
                'verbose_name': 'публикация',
                'verbose_name_plural': 'публикации',
            },
        ),
        migrations.CreateModel(
            name='PublicationModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_in_parent', models.IntegerField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Module')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parents', related_query_name='parent', to='core.Module')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='TempModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tech_name', models.CharField(blank=True, max_length=200, verbose_name='полное название')),
                ('title', models.CharField(max_length=200, verbose_name='название')),
                ('file_name', models.CharField(blank=True, max_length=200, verbose_name='имя файла')),
                ('issue_number', models.CharField(blank=True, max_length=200, verbose_name='номер версии')),
                ('content_xml', models.TextField(blank=True, verbose_name='XML содержимое')),
            ],
        ),
        migrations.AddField(
            model_name='publication',
            name='modules',
            field=models.ManyToManyField(blank=True, through='core.PublicationModule', to='core.Module'),
        ),
    ]
