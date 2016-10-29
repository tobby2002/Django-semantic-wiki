from models import Page, Category
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from SPARQLWrapper import SPARQLWrapper, JSON
import nltk
import re
from nltk.corpus import wordnet
import enchant

d = enchant.Dict("en_US")

ABSTRACT_SPARQL = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?abstract
    WHERE { <http://dbpedia.org/resource/%s> dbo:abstract ?abstract
    FILTER (langMatches(lang(?abstract),"en")) }
"""

def getsynonyms(word):
    syns = wordnet.synsets(word)
    for syn in syns:
        yield syn.name().split('.')[0].capitalize()

def gethypernyms(word):
    syns = wordnet.synsets(word)
    for syn in syns:
        hyp = syn.hypernyms()
        for h in hyp:
            yield h.name().split('.')[0].capitalize()

def autoComplete(text):
    name = text.strip()
    pages = {}

    """ If the entered text is a page name then we go and render it """
    if not Page.objects.filter(name__exact=name.capitalize()).exists():
        """ Checking for spelling mistakes here at first level by splitting words"""
        words = name.split("_")
        words = map(lambda x : x.lower(), words)
        for idx, word in enumerate(words):
            if not d.check(word):
                suggestions = d.suggest(word)
                if suggestions:
                    words[idx] = suggestions[0]
        name = "_".join(words)
        print "Auto corrected:" , name

        """ Dictionary suggests a few words very close to the words by looking at letter placement """
        auto = d.suggest(name.lower().replace("_"," "))
        if auto:
            auto = map(lambda x:x.replace(" ","_"), auto)
        for correct in auto:
            if Page.objects.filter(name__exact=correct.capitalize()).exists():
                if not correct.lower() in pages.keys():
                    pages.update({correct.lower():1})
                else:
                    pages[correct.lower()] += 1
                break

    """ The spell checked input is then checked whether the any page name starts with given text"""
    for page in Page.objects.filter(name__startswith=name.capitalize())[0:5]:
        if not page.name in pages.keys():
            pages.update({page.name:1})
        else:
            pages[page.name] += 2

    """ Some extra points thrown if page name contains the text entered """
    for page in Page.objects.filter(name__contains=name.capitalize())[0:5]:
        if not page.name in pages.keys():
            pages.update({page.name:1})
        else:
            pages[page.name] += 1

    return pages, name


def matchedpages(text):
    """Includes the wordnet semantic bit"""
    pages, query = autoComplete(text)

    """ Gets synonyms from wordnet adds to suggestions """
    for page in getsynonyms(query):
        if Page.objects.filter(name__exact=page.capitalize()).exists():
            if not page in pages.keys():
                pages.update({page:1})
            else:
                pages[page] += 1

    """ Gets hypernyms form wordnet"""
    for page in gethypernyms(query):
        if Page.objects.filter(name__exact=page.capitalize()).exists():
            if not page in pages.keys():
                pages.update({page:1})
            else:
                pages[page] += 1

    """
    TODO :
        1) If a homonym exists in the same category as in the top pages we are ranked we give it extra points!
        2) Use nltk postagger to get nouns and verbs, search for common
    """
    #
    # pages = sorted(pages.items(),key=lambda x:x[1],reverse=True)
    # pages = map(lambda x:x[0],pages)
    # pageID = Page.objects.get(name=pages[0][0]).id
    # catID = Category.objects.filter(pageid=pageID).id
    #
    #  temp=name
	# #print "Label 1"
    # tagset=nltk.pos_tag(nltk.word_tokenize(temp))
    # length=len(nltk.word_tokenize(temp))
    # nouns=[]
    # verbs=[]
	# #first POS Tag the query and pull out nouns and verbs. Adjectives and Adverbs can be ignored here as they don't add too much information
	# #standard Regex Matching to POS tags
    # for tag in tagset:
    #     if re.match('NN*', tag[1]):
    #         nouns.append(tag[0])
    #     if re.match('VB*', tag[1]):
    #         verbs.append(tag[0])
    # if len(nouns)>=2:
    #     a=(wordnet.synsets(nouns[0]))[0]
    #     b=(wordnet.synsets(nouns[1]))[0]
    #     print "Lowest Common"
    #     print a.lowest_common_hypernyms(b)#moves up the hypernym tree of a and b and returns common ones, to see if two nouns are related, like if you now query "dog and cat" it finds carnivores which could legitly be what you're searching for
    #     print "Common"
    #     print a.common_hypernyms(b)
    # temp=name
    return pages

def simple(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    pageresults, query = autoComplete(name)
    results = []
    print pageresults
    if pageresults:
        results = map(lambda x : x.replace("_"," ").capitalize(), pageresults)
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
        for page in results.keys():
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            query = ABSTRACT_SPARQL % (page)
            print query
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparqlresults = sparql.query().convert()
            suggestion = {'page':page,'linktext':page.replace("_"," ")}
            abstract = ""
            if sparqlresults["results"]["bindings"]:
                abstract = sparqlresults["results"]["bindings"][0]["abstract"]["value"]
            suggestion.update({'abstract':abstract})
            suggestions.append(suggestion)
        context = {'suggestions':suggestions}
        return render(request,'wiki/results.html',context)
