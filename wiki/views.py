from django.shortcuts import render
# from django.http import HttpResponse
# from django.template import loader
from wiki.models import Page

# Create your views here.
def article(request, page_name):
    page = Page.objects.get(name=page_name)
    return render(request,'wiki/article.html',page.__dict__)
