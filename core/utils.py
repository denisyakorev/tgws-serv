import os
import codecs
import xml.etree.ElementTree as ET
from lxml import etree
import json
from django.conf import settings
import shutil
import datetime

from core.models import Module, Publication, PublicationModule, TempModule


def get_publication_file(path):
    """
    Функция,проверяющая наличие модуля публикации в указанной папке
    :param str path: Путь к директории с файлом структуры публикации (PMC-...)
    :return: абсолютный путь к файлу публикации
    :rtype: str
    :raises ValueError: ошибка при загрузке публикации
    """
    pub_file_prefix = 'PMC-'
    files = os.listdir(path)
    publication_files = list(filter(lambda x: x[:4] == pub_file_prefix, files))

    if(len(publication_files)==0):
        raise ValueError('could not find %s file in %s directory' % (pub_file_prefix, path))
    elif(len(publication_files)>1):
        raise ValueError('too many %s files in %s directory' % (pub_file_prefix, path))
    else:
        return os.path.join(path, publication_files[0]), publication_files[0]


def get_publication_props(file_path):
    """
    Открываем файл публикации и получаем оттуда все нужные параметры
    :param str file_path: Путь к файлу публикации
    :return: Объект со свойствами, аналогичными модели публикации, а именно
    - str title
    - str code
    - int issue_number
    - str content_xml
    :rtype: obj
    :raises ValueError: ошибка при разборе публикации
    """
    file = codecs.open(file_path, 'r', encoding="utf8", errors='replace')
    tree = ET.parse(file)
    root = tree.getroot()

    title = False
    code = False
    issue_number = False

    identAndStatusSection = root.find('identAndStatusSection')
    if not identAndStatusSection:
        raise ValueError('there is no identAndStatusSection in file')

    for elem in identAndStatusSection:
        if elem.tag == 'pmAddress':
            for each in elem:
                if each.tag == 'pmIdent':
                    issue_number = each.find('issueInfo').get('issueNumber')
                elif each.tag == 'pmAddressItems':
                    title = each.find('pmTitle').text
        elif elem.tag == 'pmStatus':
            dmCode = elem.find('brexDmRef').find('dmRef').find('dmRefIdent').find('dmCode')
            code = dmCode.get('modelIdentCode')
            code += '-' + dmCode.get('systemDiffCode')
            code += '-' + dmCode.get('systemCode')
            code += '-' + dmCode.get('subSystemCode')
            code += '-' + dmCode.get('subSubSystemCode')
            code += '-' + dmCode.get('assyCode')
            code += '-' + dmCode.get('disassyCode')
            code += '-' + dmCode.get('disassyCodeVariant')
            code += '-' + dmCode.get('infoCode')
            code += '-' + dmCode.get('infoCodeVariant')
            code += '-' + dmCode.get('itemLocationCode')

    if title and code and issue_number:
        return{
            'title': title,
            'code': code,
            'issue_number': issue_number,
            'content_xml': ET.tostring(root, encoding="utf-8", method="xml")
        }
    else:
        raise ValueError('publication file incomplete')


def create_module_publication_link(module, publication, parent=None, order=0):
    """
    Функция, создающая модуль-категорию и связь модуля и публикации
    :param Module module: Экземпляр модели Модуль, для которого создается связь
    :param Publication publication: экземпляр модели публикации, к которой будет привязываться модуль
    :param Module parent: Экземпляр модели Модуль, для которого создается связь
    :param int order: Порядок модуля в родителе
    :return: Экземпляр связи
    :rtype: Module
    """
    link = PublicationModule(
        module=module,
        publication=publication,
        parent = parent,
        order_in_parent=order
    )
    link.save()

    return link


def create_category(node, publication, parent=None, order=0):
    """
    Функция, создающая модуль-категорию и связь модуля и публикации
    :param ETreeElement node: Узел, по которому создаётся категория
    :param Publication publication: экземпляр модели публикации, к которой будет привязываться модуль
    :param Module parent: экземпляр модели модуля - родителя
    :param int order: Порядок модуля в родителе
    :return: экземпляры вновь созданного модуля и связи
    :rtype: Module, PublicationModule
    :raises ValueError: ошибка при поиске параметров, нужных для создания категории
    """    
    title = node.find('pmEntryTitle').text

    if not title:
        raise ValueError('Для узла не указан заголовок')

    cat = Module(
        title=title,
        is_category=True
    )
    cat.save()
    link = create_module_publication_link(cat, publication, parent, order)

    return cat, link


def get_media_path(img_name, media_path):
    """
    Функция, возвращающая путь к файлу в медиа-папке по его имени
    :param str img_name: Имя файла без расширения
    :param str media_path: Путь к директория с медиа-объектами
    :return: Относительный путь к файлу
    :rtype: str
    :raises ValueError:не найден указанный файл
    """
    files = os.listdir(media_path)
    full_file_name = ''
    for file in files:
        file_name = file.split('.')[0]
        if file_name == img_name:
            full_file_name = file_name
            break
    abs_path = os.path.join(media_path, full_file_name)
    rel_path = abs_path.replace(settings.BASE_DIR, '')
    return rel_path


def get_module_content(content_xml, media_path):
    """
    Функция, возвращающая содержание модуля, преобразованное для просмотра
    :param str content_xml: xml структура модуля
    :param str media_path: путь к директории размещения медиа-контента
    :return content_json: json строка содержания модуля
    :rtype: str
    :raises ValueError: ошибка при разборе xml документа
    """
    content = {}
    parser = ET.XMLParser(encoding="utf-8")
    root = ET.XML(content_xml, parser=parser)
    #print(content_xml)
    #tree = etree.fromstring(content_xml)
    
    info = content['info'] = {}
    data = content['data'] = {}

    #find info
    dmAddress = root.find('identAndStatusSection').find('dmAddress')
    issueInfo = dmAddress.find('dmIdent').find('issueInfo')
    info['issueNumber'] = issueInfo.get('issueNumber')
    info['inWork'] = issueInfo.get('inWork')
    dmAddressItems = dmAddress.find('dmAddressItems')
    issueDate = dmAddressItems.find('issueDate')
    date_str = issueDate.get('day')+'.'+issueDate.get('month')+'.'+issueDate.get('year')
    info['issueDate'] = datetime.datetime.strptime(date_str, '%d.%m.%Y')
    info['techName'] = dmAddressItems.find('dmTitle').find('techName').text

    #find imgs
    illustratedPartsCatalog = root.find('content').find('illustratedPartsCatalog')
    imgs = illustratedPartsCatalog.find('figure').findall('graphic')
    data['imgs'] = []
    for img in imgs:
        img_obj = {}
        img_obj['src'] = get_media_path(img.get('infoEntityIdent'), media_path)
        img_obj['id'] = img.get('id')
        img_obj['hotspots'] = []
        hotspots = img.findall('hotspot')
        for hs in hotspots:
            hs_obj = hs.attr
            img_obj['hotspots'].append(hs_obj)

        data['imgs'].append(img_obj)

    #find parts
    data['parts'] = []
    parts = illustratedPartsCatalog.findall('catalogSeqNumber')
    for part in parts:
        part_obj = part.attr
        data['parts'].append(part_obj)

    content_json = json.dumps(content)
    return content_json


def create_end_module(node, parent=None, publication=None, order=None):
    """
    Функция, создающая модуль
    :param ETreeElement node: Узел, для которого создается модуль
    :param Module parent: Экземпляр класса Модуль - родительский модуль
    :param Publication publication: Экземпляр публикации, к которой будет привязан модуль
    :param int order: Порядок следования модуля в родителе
    :return: экземпляр вновь созданного модуля и экземпляр связи с публикацией
    :rtype: Module, ModulePublication
    :raises ValueError: ошибка при поиске параметров, нужных для создания модуля
    """
    tech_name = node.find('dmRefAddressItems').find('dmTitle').find('techName').text
    issue_number = node.find('dmRefIdent').find('issueInfo').get('issueNumber')
    if not tech_name or not issue_number:
        raise ValueError('Не хватает данных для создания модуля')
    try:
        temp_module = TempModule.objects.get(tech_name=tech_name, issue_number=issue_number)
    except TempModule.DoesNotExist:
        raise ValueError('В папке публикации не найдено файла для модуля: %s c номером выпуска: %d' % (tech_name, issue_number))
    except TempModule.MultipleObjectsReturned:
        raise ValueError('В папке публикации найдено несколько модулей: %s c номером выпуска: %d' % (tech_name, issue_number))

    new_module = Module(
        tech_name = tech_name,
        issue_number = issue_number,
        title = tech_name,
        file_name = temp_module.file_name,
        content_xml = temp_module.content_xml,
        #content_json = json,
        is_category = False
    )
    new_module.save()
    link = create_module_publication_link(new_module, publication, parent, order)

    return new_module, link


def create_nodes(node, parent=None, publication=None):
    """
    Функция, рекурсивно создающая модули и категории для переданного узла
    :param ETreeElement node: Узел, для которого осуществляется поиск
    :param Module parent: Экземпляр класса Модуль - родительский модуль
    :param Publication publication: экземпляр модели публикации, для которой создаются модули
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибки при создании модулей
    """    
    counter_end_nodes = 0
    counter_categories = 0    
    for child in node:
        if child.tag == 'dmRef':
            counter_end_nodes += 1
            try:
                create_end_module(child, parent, publication, counter_end_nodes)
            except Exception as err:
                if parent:
                    raise ValueError('Ошибка при создании модуля №%d для узла %s: %s'%(counter_end_nodes, parent.title, err))
                else:
                    raise ValueError('Ошибка при создании модуля №%d для узла без родителя: %s'%(counter_end_nodes, parent.title, err))
        elif child.tag == 'pmEntry':
            counter_categories += 1
            new_category, link = create_category(child, publication, parent=parent, order=counter_categories)
            create_nodes(child, parent=new_category, publication=publication)

    return True


def load_modules_from_files(path):
    """
    Функция, загружающая все модули из директории публикации во временное хранилище
    :param str path: Путь к папке публикации
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибка при обработке модуля
    """
    mod_file_prefix = 'DMC-'
    files = os.listdir(path)
    modules_files = list(filter(lambda x: x[:4] == mod_file_prefix, files))
    for f in modules_files:
        tech_name = None
        issue_number = None
        file_path = os.path.join(path, f)

        file = codecs.open(file_path, 'r', encoding="utf8", errors='replace')
        tree = ET.parse(file)
        root = tree.getroot()
        dmAddressItems = root.find('identAndStatusSection').find('dmAddress')
        tech_name = dmAddressItems.find('dmAddressItems').find('dmTitle').find('techName').text
        issue_number = dmAddressItems.find('dmIdent').find('issueInfo').get('issueNumber')
        if not tech_name or not issue_number:
            raise ValueError('Не хватает данных для создания модуля из файла: %s' % f)
        temp_module = TempModule(
            tech_name = tech_name,
            title = tech_name,
            issue_number = issue_number,
            file_name = f,
            content_xml = ET.tostring(root, encoding='utf-8', method='xml')
        )
        temp_module.save()

    return True




def load_modules(file_path, publication, path):
    """
    Функция, загружающая все модули данных публикации
    :param str file_path: Путь к файлу публикации
    :param Publication publication: Экземпляр модели публикации, для которой создаются модули
    :param str path: Путь к папке публикации
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибка при отсутствии предусмотренного родительского узла
    """
    file = codecs.open(file_path, 'r', encoding="utf8", errors='replace')
    tree = ET.parse(file)
    root = tree.getroot()
    try:
        content = root.find('content')
    except Exception as err:
        raise ValueError('В файле публикации не найден узел content: %s' % err)

    create_nodes(content, publication=publication)

    #Очистим временные модули
    TempModule.objects.all().delete()

    return True


def copy_static(path, publication_code, media_path):
    """
    Функция, копирующая статические файлы публикации в папку сервера
    :param str path: Путь к директории публикации
    :param str code: Код публикации, будет служить названием папки для файлов в медиа-папке
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    """
    static_folder = 'graphics'
    static_path = os.path.join(path, static_folder)
    shutil.copytree(static_path, media_path)
    return True


def get_childrens(holder, publication, parent=None):
    """
    Функция, рекурсивно заполняющая массив дочерних элементов
    :param array holder: массив для заполнения
    :param Module parent: экземпляр модели Модуль - родителя, для которого ищутся дочерние элементы
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    """
    if not parent:
        links = PublicationModule.objects.filter(publication=publication, parent__isnull=True).order_by('order_in_parent')

    else:
        links = PublicationModule.objects.filter(publication=publication, parent=parent).order_by('order_in_parent')

    for link in links:
        obj = {
            'id': link.module.id,
            'text': link.module.title,
            'a_attr':{'href':link.module.id},
            'children': []
        }
        holder.append(obj)
        get_childrens(obj['children'], publication, parent=link.module)

    return True


def get_tree_structure(publication):
    """
    Функция, создающее дерево модулей в публикации
    :param Publication publication: экземпляр модели публикации, для которой выполняется поиск
    :return: json структура публикации
    :rtype: str
    :raise ValueError: не найдена публикация
    """
    
    tree = {
        'core':{
            'data':[]
        }
    }
    get_childrens(tree['core']['data'], publication)

    return json.dumps(tree)


def parce_modules(publication, media_path):
    """
    Функция, формирующее json содержание модуля
    :param Publication publication: экземпляр объекта публикации, для модулей которой будет заполняться содержимое
    :param str media_path: путь к директории размещения медиа-объектов
    :return: Флаг об успешном завершении операции
    :rtype: bool
    """
    modules = publication.modules.filter(is_category = False)
    for module in modules:
        module.content_json = get_module_content(module.content_xml, media_path)
        module.save()

    return True

def load_publication(path):
    """
    Функция для загрузки публикации
    :param str path: Путь к директории с файлом структуры публикации (PMC-...)
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибка при загрузке публикации
    """
    pub_file_path, file_name = get_publication_file(path)
    #Создание публикации
    pub_data = get_publication_props(pub_file_path)
    publication = Publication(
        title = pub_data['title'],
        code = pub_data['code'],
        file_name = os.path.splitext(file_name)[0],
        issue_number = pub_data['issue_number'],
        content_xml = pub_data['content_xml']
        )
    publication.save()
    MEDIA_PATH = os.path.join(settings.MEDIA_ROOT, 'pub_files', publication.code)
    print("publication created")
    load_modules_from_files(path)
    print("loaded modules from files")
    #Создание модулей
    load_modules(pub_file_path, publication, path)
    print("modules from publication file loaded")
    #Перенос статического контента
    copy_static(path, pub_data['code'], MEDIA_PATH)
    print("static copied")
    #Cоздание дерева модулей
    publication.structure_json = get_tree_structure(publication)
    publication.save()
    print("publication tree created")
    parce_modules(publication, MEDIA_PATH)
    print("modules parced")


    return True



"""
from core.utils import *

Publication.objects.all().delete()
Module.objects.all().delete()
PublicationModule.objects.all().delete()
TempModule.objects.all().delete()

#home
shutil.rmtree('/home/denis/projects/tgws-serv/tgws_serv/media/pub_files/3204-A-00-0-0-00-00-A-022-A-D')
load_publication('/home/denis/projects/tgws-serv/assets/ПубликацииПАЗ/ПАЗ-320445 Вектор Next (АТ)_10.08.18_12.39.02')

#work
shutil.rmtree('/home/denis/projects/tgws_serv/tgws_serv/media/pub_files/3204-A-00-0-0-00-00-A-022-A-D')
load_publication('/home/denis/projects/tgws_serv/assets/pubs/ПАЗ-320445 Вектор Next (АТ)_10.08.18_12.39.02')

#only load publications
publication = Publication.objects.all()[0]
MEDIA_PATH = os.path.join(settings.MEDIA_ROOT, 'pub_files', publication.code)
parce_modules(publication, MEDIA_PATH)

"""






