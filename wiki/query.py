from models import Page
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from SPARQLWrapper import SPARQLWrapper, JSON
ABSTRACT_SPARQL = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?abstract
    WHERE { <http://dbpedia.org/resource/%s> dbo:abstract ?abstract
    FILTER (langMatches(lang(?abstract),"en")) }
"""

def matchedpages(text):
    pages = Page.objects.filter(name__startswith=text)[0:5]
    return pages

def simple(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    # pages = Page.objects.filter(name__startswith=name)[0:5]
    pageresults = matchedpages(name)
    results = map(lambda x : x.name.replace("_"," "), pageresults)
    # results = map(lambda x : x.name.replace("_"," "), pages)
    return JsonResponse({"results":results})

def results(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    if Page.objects.filter(name__exact=name).exists():
        print "Page exists"
        return HttpResponseRedirect('/wiki/'+name)
    else:
        results = matchedpages(name)
        suggestions = []
        for page in results:
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            query = ABSTRACT_SPARQL % (page.name)
            print query
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparqlresults = sparql.query().convert()
            suggestion = {'page':page.name,'linktext':page.name.replace("_"," ")}
            abstract = ""
            if sparqlresults["results"]["bindings"]:
                abstract = sparqlresults["results"]["bindings"][0]["abstract"]["value"]
            suggestion.update({'abstract':abstract})
            suggestions.append(suggestion)
        # suggestions = [
        #     {
        #     'page' : 'April',
        #     'linktext' : 'April',
        #     'abstract' : 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
        #     },
        # ]
        context = {'suggestions':suggestions}
        return render(request,'wiki/results.html',context)
