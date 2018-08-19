from django.shortcuts import render
from django.shortcuts import render_to_response
# Create your views here.

def show_tgws(request):
    return render_to_response('index.html')