from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the m2 index.")
    
def update(request):
    return HttpResponse("Hello, world. You're at the m2/update index.")