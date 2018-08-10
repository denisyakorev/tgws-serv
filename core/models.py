from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Publication(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('название'))    
    code = models.CharField(max_length=200, verbose_name=_('код'), unique=True)
    file_name = models.CharField(max_length=200, verbose_name=_('имя файла'))
    issueNumber = models.IntegerField(verbose_name=_('номер версии'))
    content_xml = models.TextField(verbose_name=_('XML содержимое'), blank=True)
    structure_json = models.TextField(verbose_name=_('JSON cтруктура'), blank=True)    
    modules = models.ManyToManyField('Module', through='PublicationModule', through_fields=('publication', 'module'), blank=True)

    def __unicode__(self):
        return self.file_name

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = _("публикация")
        verbose_name_plural = _("публикации")
        


class Module(models.Model):
    tech_name = models.CharField(max_length=200, verbose_name=_('полное название'), blank=True)
    title = models.CharField(max_length=200, verbose_name=_('название'))
    code = models.CharField(max_length=200, verbose_name=_('код'), blank=True)    
    file_name = models.CharField(max_length=200, verbose_name=_('имя файла'), blank=True)
    issueNumber = models.IntegerField(verbose_name=_('номер версии'), blank=True)    
    content_xml = models.TextField(verbose_name=_('XML содержимое'), blank=True)
    content_json = models.TextField(verbose_name=_('JSON содержимое'), blank=True)
    is_category = models.BooleanField(verbose_name=_('категория'), default=False)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("модуль")
        verbose_name_plural = _("модули")


class PublicationModule(models.Model):
    '''
    Промежуточная таблица для связи модулей и публикаций
    '''
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE,)
    parent = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='parents', related_query_name='parent', blank=True, null=True)
    order_in_parent = models.IntegerField()


