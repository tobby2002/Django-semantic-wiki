from models import Page
from django.http import JsonResponse

def simple(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    pages = Page.objects.filter(name__startswith=name)[0:5]
    results = map(lambda x : x.name.replace("_"," "), pages)
    return JsonResponse({"results":results})
