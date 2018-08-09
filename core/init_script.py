from core.models import Publication

def make_init_pub():
    init_pub, created = Publication.objects.get_or_create(code= "2")

    init_pub.name = 'TestPub'
    init_pub.content_json= '{"core":{"data":[{"text":"Publication","state":{"selected":true},"children":[{"text":"Chapter_1","a_attr":{"href":"www.yandex.ru"},"children":[{"text":"Module1","a_attr":{"href":"www.yandex.ru"}},{"text":"Module2","a_attr":{"href":"www.yandex.ru"}}]}]}]}}'

    init_pub.save()
    print("True")
