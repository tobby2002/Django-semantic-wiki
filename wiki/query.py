from models import Page
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

def simple(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    pages = Page.objects.filter(name__startswith=name)[0:5]
    results = map(lambda x : x.name.replace("_"," "), pages)
    return JsonResponse({"results":results})

def results(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    if Page.objects.filter(name__exact=name).exists():
        print "Page exists"
        return HttpResponseRedirect('/wiki/'+name)
    else:
        suggestions = [
            {
            'page' : 'April',
            'linktext' : 'April',
            'abstract' : 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            },
            {
            'page' : 'April',
            'linktext' : 'April',
            'abstract' : 'lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            },
        ]
        context = {'suggestions':suggestions}
        return render(request,'wiki/results.html',context)
