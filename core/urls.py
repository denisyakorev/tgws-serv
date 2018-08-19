from django.urls import path, include
from core.views import show_tgws

urlpatterns = [
    path('', show_tgws, name='main_page'),
    ]