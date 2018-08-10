import os
import codecs
import xml.etree.ElementTree as ET

from core.models import Module, Publication, PublicationModule


def get_publication_file(dir):
	"""
	Функция,проверяющая наличие модуля публикации в указанной папке
	:param str dir: Путь к директории с файлом структуры публикации (PMC-...)
	:return: абсолютный путь к файлу публикации
	:rtype: str
	:raises ValueError: ошибка при загрузке публикации 
	"""
	pub_file_prefix = 'PMC-'
	files = os.listdir(dir)
	publication_files = list(filter(lambda x: x[:4] == pub_file_prefix, files))
	
	if(len(publication_files)==0):
	    raise ValueError('could not find %s file in %s directory' % (pub_file_prefix, dir))
	elif(len(publication_files)>1):
		raise ValueError('too many %s files in %s directory' % (pub_file_prefix, dir))
	else:
		return os.path.join(dir, publication_files[0]), publication_files[0]


def get_publication_props(file)
	"""
	Открываем файл публикации и получаем оттуда все нужные параметры
	:param file file: Файл структуры публикации
	:return: Объект со свойствами, аналогичными модели публикации, а именно
	- str title
	- str code
	- int issueNumber
	- str content_xml
	:rtype: obj
	:raises ValueError: ошибка при разборе публикации
	"""
	
	tree = ET.parse(file)
	root = tree.getroot()
	
	title = False
	code = False
	issueNumber = False
	
	identAndStatusSection = root.find('identAndStatusSection')
	if not identAndStatusSection:
		raise ValueError('there is no identAndStatusSection in file')

	for elem in identAndStatusSection:
		if elem.tag == 'pmAddress':
			for each in elem:
				if each.tag == 'pmIdent':
					issueNumber = int(each.find('issueInfo').get('issueNumber'))
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

	if title and code and issueNumber:
		return{
			'title': title,
			'code': code,			
			'issueNumber': issueNumber,
			'content_xml': ET.tostring(root, encoding="utf-8", method="xml")
		}
	else:
		raise ValueError('publication file incomplete') 


def create_nodes(node, parent=None):
	"""
	Функция, рекурсивно создающая модули и категории для переданного узла
	:param ETreeElement node: Узел, для которого осуществляется поиск
	:param Module parent: экземпляр модели, который будет родительским узлом
	:return: результат выполнения операции - True при успешном выполнении
	:rtype: bool
	:raises ValueError: ошибки при создании модулей
	"""
	end_modules = node.findall('dmRef')
	counter = 0
	for module in end_modules:
		counter += 1		
		try:
			create_end_module(module, parent, counter)

		except Exception as err:
			if parent:
				raise ValueError('Ошибка при создании модуля №%d для узла %s'%(counter, parent.title))
			else:
				raise ValueError('Ошибка при создании модуля №%d для узла без родителя'%(counter, parent.title))

	categories = node.findall('pmEntry')






def load_modules(file, publication):
	"""
	Функция, загружающая все модули данных публикации
	:param file file: Файл публикации
	:param Publication publication: Экземпляр модели публикации, для которой создаются модули	
	:return: результат выполнения операции - True при успешном выполнении
	:rtype: bool
	:raises ValueError: ошибка при отсутствии предусмотренного родительского узла	
	"""
	tree = ET.parse(file)
	root = tree.getroot()
	try:
		content = root.find('content')
	except Exception as err:
		raise ValueError('В файле публикации не найден узел content')

	#Cоздадим корневой узил
	root_module = Module(
		title= publication.title,
		is_category = True
		)
	root_module.save()

	link = PublicationModule(
		module = root_module,
		publication = publication,
		order_in_parent = 0 
		)
	link.save()

	create_nodes(content, root_module, publication)

	return True


def copy_static(dir):
	pass


def load_publication(dir):
	"""
	Функция для загрузки публикации
	:param str dir: Путь к директории с файлом структуры публикации (PMC-...)
	:return: результат выполнения операции - True при успешном выполнении
	:rtype: bool
	:raises ValueError: ошибка при загрузке публикации 
	"""
	pub_file_path, file_name = get_publication_file(dir)
	file = codecs.open(pub_file_path, 'r', encoding="utf8", errors='replace')
	
	#Создание публикации
	pub_data = get_publication_props(file)		
	publication = Publication(
		title = pub_data['title'],
		code = pub_data['code'],
		file_name = os.path.splitext(file_name)[0],
		issueNumber = pub_data['issueNumber'],
		content_xml = pub_data['content_xml']
		)
	publication.save()

	#Создание модулей
	load_modules(file, publication)
	
	#Перенос статического контента
	copy_static(dir)

	#Cоздание дерева модулей
	publication.structure_json = get_tree_structure(publication.pk)
	publication.save()

	return True
		
		
		







