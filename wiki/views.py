from django.shortcuts import render
from django.http import Http404
from wiki.models import Page, PageOutlinks
from wikimarkup import parse
import re

LINK_FROMAT = """<a href="{path}">{linktext}</a>"""
OUTLINK_TITLES = []

_re_linktext = re.compile(r'\[\[([a-zA-Z0-9 ()-.]+)\]\]')
_re_altlink = re.compile(r'\[\[([a-zA-Z0-9 ()-.]+)\|([a-zA-Z0-9 ()-.]+)\]\]')
_re_media = re.compile(r'\[\[([a-zA-Z0-9 -,.:<>=""/_|]+)\]\]')
_re_annotate = re.compile(r'\{\{([\'a-zA-Z0-9 -,.:<>=""/_|]+)\}\}')

def processlink(m):
    if "|" in m.group(0):
        linktext = m.group(2)
    else:
        linktext = m.group(1)
    matchtext = m.group(1)
    matchtext = matchtext.replace(" ","_")
    if matchtext not in OUTLINK_TITLES:
        return linktext
    path = "/wiki/" + matchtext
    return LINK_FROMAT.format(path = path,linktext = linktext)

def processmedia(m):
    """TODO: process the objects and fill up html to render media"""
    return ""

def getOutlinks(id):
    outlinks = PageOutlinks.objects.filter(id=id)
    for outLink in outlinks:
        OUTLINK_TITLES.append(Page.objects.get(id=outLink.outlinks).name)

def addlinks(id,text):
    getOutlinks(id)
    text = _re_linktext.sub(processlink, text) # direct links
    text = _re_altlink.sub(processlink, text) # links with
    text = _re_media.sub(processmedia, text) # for File Wikitory and other wikimedia
    text = _re_annotate.sub(processmedia, text) # infobox and related info
    OUTLINK_TITLES = []
    return text

# Create your views here.
def article(request, page_name):
    try:
        page = Page.objects.get(name=page_name)
    except Page.DoesNotExist as e:
        raise Http404("No such page exists")
    text = addlinks(page.id, parse(page.text))
    context = {
    'name' : page.name,
    'text' : text,
    }
    return render(request,'wiki/article.html',context)

def home(request):
    context = {'title':"Home"}
    return render(request,'wiki/home.html',context)
