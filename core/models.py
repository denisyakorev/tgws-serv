from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Publication(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('названиеи'))
    code = models.CharField(max_length=200, verbose_name=_('код'), unique=True)
    content_xml = models.TextField(verbose_name=_('XML содержимое'), blank=True)
    content_json = models.TextField(verbose_name=_('JSON содержимое'), blank=True)
    modules = models.ManyToManyField('Module', blank=True, null=True)


class Module(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('название'))
    code = models.CharField(max_length=200, verbose_name=_('код'), unique=True)
    content_xml = models.TextField(verbose_name=_('XML содержимое'), blank=True)
    content_json = models.TextField(verbose_name=_('JSON содержимое'), blank=True)


