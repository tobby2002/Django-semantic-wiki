# from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.
def article(request, page_name):
    #load page deatails from db
    template = loader.get_template('wiki/article.html')
    dummy_article = [
        {
        'header':"Intro",
        'content':"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        },
        {
        'header':"History",
        'content':"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        }
    ]
    context = {'title':str(page_name),"sections":dummy_article}
    return HttpResponse(template.render(context, request))
    # return render(request,'wiki/article.html',context)
