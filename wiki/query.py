from models import Page
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from SPARQLWrapper import SPARQLWrapper, JSON
import nltk
import re
from nltk.corpus import wordnet

ABSTRACT_SPARQL = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?abstract
    WHERE { <http://dbpedia.org/resource/%s> dbo:abstract ?abstract
    FILTER (langMatches(lang(?abstract),"en")) }
"""

def matchedpages(text):
    name = text.strip()
    temp=name
	#print "Label 1"
    tagset=nltk.pos_tag(nltk.word_tokenize(temp))
    length=len(nltk.word_tokenize(temp))
    nouns=[]
    verbs=[]
	#first POS Tag the query and pull out nouns and verbs. Adjectives and Adverbs can be ignored here as they don't add too much information
	#standard Regex Matching to POS tags
    for tag in tagset:
        if re.match('NN*', tag[1]):
            nouns.append(tag[0])
        if re.match('VB*', tag[1]):
            verbs.append(tag[0])
    limit=2
    for n in nouns:
        print "\n",n
		#print "Label 3"
        syn=wordnet.synsets(n)#returns a list of synsets each of which contains a different meaning of the noun
		#print "Label 4"
		#This first wordnet operation creates a pause. Maybe it'll be fine in our server as the first link would have been made already no?
        print "Hypernyms : "
        k=0
        for a in syn:
            k=k+1
            if k>limit:
                break
            print " ",a.hypernyms()
            #each item on the list of synsets i.e. each different meaning of the noun contains a set of hypernyms
            print "Hyponyms : "
        k=0
        for a in syn:
            k=k+1
            if k>limit:
                break
            print " ",a.hyponyms()
            #same but hyponyms
            print "Synonyms : "
        k=0
        for a in syn:
            k=k+1
            if k>limit:
                break
            print a.name()
            for lemma in a.lemmas():
                print " ", lemma.name()
    for v in verbs:
        print "\n",v
        syn=wordnet.synsets(v)
        k=0
        print "Hypernyms : "
        for a in syn:
            k=k+1
            if k>limit:
                break
            print " ",a.hypernyms()
        print "Hyponyms : "
        k=0
        for a in syn:
            k=k+1
            if k>limit:
                break
            print " ",a.hyponyms()
        print "Synonyms : "
        k=0
        for a in syn:
            k=k+1
            if k>limit:
                break
            print a.name()
            for lemma in a.lemmas():
                print " ",lemma.name()
    if len(nouns)>=2:
        a=(wordnet.synsets(nouns[0]))[0]
        b=(wordnet.synsets(nouns[1]))[0]
        print "Lowest Common"
        print a.lowest_common_hypernyms(b)#moves up the hypernym tree of a and b and returns common ones, to see if two nouns are related, like if you now query "dog and cat" it finds carnivores which could legitly be what you're searching for
        print "Common"
        print a.common_hypernyms(b)
    name=name.replace(" ","_").capitalize()
    print name
    #to find same category items from our db, not sure of the sql query but, should test on MySQL database itself before putting it here
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
        context = {'suggestions':suggestions}
        return render(request,'wiki/results.html',context)
