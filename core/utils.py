import os
import codecs
import xml.etree.ElementTree as ET
import xmltodict, json

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


def get_publication_props(file):
    """
    Открываем файл публикации и получаем оттуда все нужные параметры
    :param file file: Файл структуры публикации
    :return: Объект со свойствами, аналогичными модели публикации, а именно
    - str title
    - str code
    - int issue_number
    - str content_xml
    :rtype: obj
    :raises ValueError: ошибка при разборе публикации
    """
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
                    issue_number = int(each.find('issueInfo').get('issue_number'))
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
    title = node.find('pmEntryTitle')
    if not title:
        raise ValueError('Для узла не указан заголовок')

    # Cоздадим корневой узел
    cat = Module(
        title=title,
        is_category=True
    )
    cat.save()
    link = create_module_publication_link(cat, publication, parent, order)

    return cat, link


def create_end_module(node, parent, publication, order):
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
    issue_number = node.find('dmRefIdent').find('issueInfo').get('issue_number')
    if not tech_name or not issue_number:
        raise ValueError('Не хватает данных для создания модуля')
    try:
        temp_module = TempModule.objects.get(tech_name=tech_name, issue_number=issue_number)
    except TempModule.DoesNotExist:
        raise ValueError('В папке публикации не найдено файла для модуля: %s c номером выпуска: %d' % (tech_name, issue_number))
    except TempModule.MultipleObjectsReturned:
        raise ValueError('В папке публикации найдено несколько модулей: %s c номером выпуска: %d' % (tech_name, issue_number))

    obj = xmltodict.parse(temp_module.content_xml)
    json = json.dumps(obj)
    new_module = Module(
        tech_name = tech_name,
        issue_number = issue_number,
        title = tech_name,
        file_name = temp_module.file_name,
        content_xml = temp_module.content_xml,
        content_json = json,
        is_category = False
    )
    new_module.save()
    link = create_module_publication_link(new_module, publication, parent, order)

    return new_module, link


def create_nodes(node, parent, publication):
    """
    Функция, рекурсивно создающая модули и категории для переданного узла
    :param ETreeElement node: Узел, для которого осуществляется поиск
    :param Module parent: Экземпляр класса Модуль - родительский модуль
    :param Publication publication: экземпляр модели публикации, для которой создаются модули
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибки при создании модулей
    """
    end_module_nodes = node.findall('dmRef')
    counter = 0
    for node in end_module_nodes:
        counter += 1
        try:
            create_end_module(node, parent, publication, counter)

        except Exception as err:
            if parent:
                raise ValueError('Ошибка при создании модуля №%d для узла %s: %s'%(counter, parent.title, err))
            else:
                raise ValueError('Ошибка при создании модуля №%d для узла без родителя: %s'%(counter, parent.title, err))

    categories = node.findall('pmEntry')
    counter = 0
    for category in categories:
        counter += 1
        create_category(category, publication)
        create_nodes(category, publication)

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
        dmAddressItems = root.find('identAndStatusSection').find('dmAddressItems')
        tech_name = dmAddressItems.find('dmTitle').find('techName').text
        issue_number = int(dmAddressItems.find('dmIdent').find('issueInfo').get('issue_number'))
        if not tech_name or not issue_number:
            raise ValueError('Не хватает данных для создания модуля из файла: %s' % f)
        temp_module = TempModule(
            tech_name = tech_name,
            title = tech_name,
            issue_number = issue_number,
            file_name = f,
            content_xml = ET.tostring(root, encoding="utf-8", method="xml")
        )
        temp_module.save()

    return True




def load_modules(file, publication, path):
    """
    Функция, загружающая все модули данных публикации
    :param file file: Файл публикации
    :param Publication publication: Экземпляр модели публикации, для которой создаются модули
    :param str path: Путь к папке публикации
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибка при отсутствии предусмотренного родительского узла
    """
    load_modules_from_files(path)
    tree = ET.parse(file)
    root = tree.getroot()
    try:
        content = root.find('content')
    except Exception as err:
        raise ValueError('В файле публикации не найден узел content: %s' % err)

    root_category = create_category(content, publication)
    create_nodes(content, root_category, publication)

    #Очистим временные модули
    TempModule.objects.all().delete()

    return True


def copy_static(path):
    pass


def load_publication(path):
    """
    Функция для загрузки публикации
    :param str path: Путь к директории с файлом структуры публикации (PMC-...)
    :return: результат выполнения операции - True при успешном выполнении
    :rtype: bool
    :raises ValueError: ошибка при загрузке публикации
    """
    pub_file_path, file_name = get_publication_file(path)
    file = codecs.open(pub_file_path, 'r', encoding="utf8", errors='replace')

    #Создание публикации
    pub_data = get_publication_props(file)
    publication = Publication(
        title = pub_data['title'],
        code = pub_data['code'],
        file_name = os.path.splitext(file_name)[0],
        issue_number = pub_data['issue_number'],
        content_xml = pub_data['content_xml']
        )
    publication.save()

    #Создание модулей
    load_modules(file, publication)

    #Перенос статического контента
    copy_static(path)

    #Cоздание дерева модулей
    publication.structure_json = get_tree_structure(publication.pk)
    publication.save()

    return True










