from models import Page, Category
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from SPARQLWrapper import SPARQLWrapper, JSON
from nltk.corpus import wordnet

import re
import nltk
import sparql
import logging
import enchant

d = enchant.Dict("en_US")
from wiki_project.settings import DEBUG
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(filename="wiki.log", level=logging.DEBUG)

logger = logging.getLogger(__name__)

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

def autoCorrect(name):
    """ Checking for spelling mistakes here at first level by splitting words"""
    words = name.split("_")
    words = map(lambda x : x.lower(), words)
    for idx, word in enumerate(words):
        if not d.check(word):
            suggestions = d.suggest(word)
            if suggestions:
                words[idx] = suggestions[0]
    name = "_".join(words)
    logger.debug("Auto corrected:" + name)
    return name

def checkForSuggestion(pages,name):

    """ If the entered text is a page name then we go and render it """
    if not Page.objects.filter(name__exact=name.capitalize()).exists():
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
    else:
        pages.update({name:2})

    """ Check for all words and to check if they have pages each """
    words = name.split("_")
    for word in words:
        logger.debug("Word:"+word)
        if Page.objects.filter(name__exact=word.capitalize()).exists():
            if not word in pages.keys():
                pages.update({word:1})
            else:
                pages[word] += 1

    """ The spell checked input is then checked whether the any page name starts with given text"""
    for page in Page.objects.filter(name__startswith=name.capitalize())[0:5]:
        if not page.name in pages.keys():
            pages.update({page.name:1})
        else:
            pages[page.name] += 1

    """ Some extra points thrown if page name contains the text entered """
    for page in Page.objects.filter(name__contains=name.capitalize())[0:5]:
        if not page.name in pages.keys():
            pages.update({page.name:1})
        else:
            pages[page.name] += 1

    return pages

def autoComplete(text):
    name = text.strip()
    pages = {}

    auto_name = autoCorrect(name)
    logger.debug('auto_name'+auto_name)
    checkForSuggestion(pages, name)
    logger.debug('normal'+str(pages))
    checkForSuggestion(pages, auto_name)
    logger.debug('corrected'+ str(pages))
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

    """NLP for getting nouns"""
    tagset=nltk.pos_tag(nltk.word_tokenize(query.replace("_"," ")))
    logger.debug('query:'+str(query))
    logger.debug('tagset:'+str(tagset))
    # length=len(nltk.word_tokenize(temp))
    nouns=[]
    # verbs=[]
	#first POS Tag the query and pull out nouns and verbs. Adjectives and Adverbs can be ignored here as they don't add too much information
	#standard Regex Matching to POS tags
    for tag in tagset:
        if re.match('NN*',tag[1]):
            nouns.append(tag[0])
        # if re.match(r'VB*', tag[1]):
        #     verbs.append(tag[0])
    logger.debug('nouns:'+str(nouns))

    """ To get all the hypernyms and add to each noun """
    print nouns
    raw_result = None
    if len(nouns)>=2:
        if len(nouns) == 2:
            if Page.objects.filter(name__exact=nouns[0].capitalize()).exists():
                part, page = nouns[1], nouns[0]
                for prop in sparql.prop_fetch(part, page.capitalize()):
                    print prop
                    if prop['type'] == 'raw':
                        raw_result = prop
                        continue
                    if Page.objects.filter(name__exact=prop['value'].capitalize()).exists():
                        if not prop['value'] in pages.keys():
                            pages.update({prop['value']:1})
                        else:
                            pages[prop['value']] += 3

            if Page.objects.filter(name__exact=nouns[1].capitalize()).exists():
                part, page = nouns[0], nouns[1]
                for prop in sparql.prop_fetch(part, page.capitalize()):
                    print prop
                    if prop['type'] == 'raw':
                        raw_result = prop
                        continue
                    if Page.objects.filter(name__exact=prop['value'].capitalize()).exists():
                        if not prop['value'] in pages.keys():
                            pages.update({prop['value']:1})
                        else:
                            pages[prop['value']] += 3

        hypernyms = {}
        for noun in nouns:
            for hypernym in gethypernyms(noun):
                if not hypernym in hypernyms.keys():
                    hypernyms.update({hypernym:1})
                else:
                    hypernyms[hypernym] += 1
        print hypernyms
        filtered_hypernyms = []
        for hypernym in hypernyms:
            if hypernyms[hypernym] > 1:
                filtered_hypernyms.append(hypernym)
        print filtered_hypernyms

        page_found = False
        for hypernym in filtered_hypernyms:
            if Page.objects.filter(name__exact=hypernym.capitalize()).exists():
                page_found = True
                if not hypernym in pages.keys():
                    pages.update({hypernym:1})
                else:
                    pages[hypernym] += 1

        flag=0
        if not page_found:
            if(len(wordnet.synsets(nouns[0]))==0):
                flag=1
            else:
                a=(wordnet.synsets(nouns[0]))[0]
            if(len(wordnet.synsets(nouns[1]))==0):
                flag=1
            else:
                b=(wordnet.synsets(nouns[1]))[0]
            # print "Lowest Common"
            if flag==0:
                hypernym = a.lowest_common_hypernyms(b)[0]#moves up the hypernym tree of a and b and returns common ones, to see if two nouns are related, like if you now query "dog and cat" it finds carnivores which could legitly be what you're searching for
                hypernym = hypernym.name().split('.')[0]
                if Page.objects.filter(name__exact=hypernym.capitalize()).exists():
                    if not hypernym in pages.keys():
                        pages.update({hypernym:1})
                    else:
                        pages[hypernym] += 1


    """
    TODO :
        1) If a homonym exists in the same category as in the top pages we are ranked we give it extra points!
        2) Use nltk postagger to get nouns and verbs, search for common
    """
    # if len(nouns)>=2:
    #     a=(wordnet.synsets(nouns[0]))[0]
    #     b=(wordnet.synsets(nouns[1]))[0]
    #     print "Lowest Common"
    #     print a.lowest_common_hypernyms(b)#moves up the hypernym tree of a and b and returns common ones, to see if two nouns are related, like if you now query "dog and cat" it finds carnivores which could legitly be what you're searching for
    #     print "Common"
    #     print a.common_hypernyms(b)
    # temp=name
    return pages,raw_result

def simple(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    pageresults, query = autoComplete(name)
    results = []
    pageresults =  sorted(pageresults.iteritems(), key=lambda (k,v): (v,k))[::-1]
    logger.debug(pageresults)
    if pageresults:
        results = map(lambda x : x[0].replace("_"," ").capitalize(), pageresults)
    return JsonResponse({"results":results})

def results(request):
    query = request.GET.get('q',"")
    name = query.strip().replace(" ","_").capitalize()
    print name
    if Page.objects.filter(name__exact=name).exists():
        logger.info("Page found:"+name)
        return HttpResponseRedirect('/wiki/'+name)
    else:
        results,raw_result = matchedpages(name)
        suggestions = []
        for page in results.keys():
            abstract = sparql.abstract_fetch(page.capitalize())
            suggestion = {'page':page,'linktext':page.replace("_"," ")}
            suggestion.update({'abstract':abstract})
            suggestions.append(suggestion)
        if raw_result:
            raw_result['property'] = re.sub("([a-z])([A-Z])","\g<1> \g<2>",raw_result['property']).capitalize()
        context = {'suggestions':suggestions,'title':"Results",'semantic_result':raw_result}
        return render(request,'wiki/results.html',context)
