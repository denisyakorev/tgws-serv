from django.urls import path, include
from api.views import publication_detail, module_detail


urlpatterns = [
    path('publication_detail/<str:pubcode>/', publication_detail, name='pub_tree'),
    path('module_detail/<str:module_id>/', module_detail, name='module_detail'),
]


