from django.urls import path, include
from api.views import publication_detail


urlpatterns = [
    path('publication_detail/<str:pubcode>/', publication_detail, name='pub_tree'),
]


