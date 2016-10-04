from django.shortcuts import render
from wiki.models import Page
from wikimarkup import parse
import re
LINK_FROMAT = """<a href="{path}">{linktext}</a>"""

def processlink(m):
    if "|" in m.group(0):
        linktext = m.group(2)
    else:
        linktext = m.group(1)
    matchtext = m.group(1)
    matchtext = matchtext.replace(" ","_")
    if not Page.objects.filter(name=matchtext).only("id").exists():
        matchtext = u'Error_404'
    path = "/wiki/" + matchtext
    return LINK_FROMAT.format(path = path,linktext = linktext)

def processmedia(m):
    """TODO: process the objects and fill up html to render media"""
    return ""

def addlinks(text):
    text = re.sub(r'\[\[([a-zA-Z0-9 ()-.]+)\]\]', processlink, text) # direct links
    text = re.sub(r'\[\[([a-zA-Z0-9 ()-.]+)\|([a-zA-Z0-9 ()-.]+)\]\]', processlink, text) # links with
    text = re.sub(r'\[\[.+?\]\] | \{\{.+?\}\}', "", text) # for File Wikitory and other wikimedia
    return text

# Create your views here.
def article(request, page_name):
    page = Page.objects.get(name=page_name)
    text = addlinks(parse(page.text))
    context = {
    'name' : page.name,
    'text' : text,
    }
    return render(request,'wiki/article.html',context)

def home(request):
    context = {'title':"Home"}
    return render(request,'wiki/home.html',context)
