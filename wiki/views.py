from django.shortcuts import render, redirect
from django.http import Http404
from wiki.models import Page, PageOutlinks, PageRedirects
from wikimarkup import parse

import mwparserfromhell
import logging
import string
import re

from wiki_project.settings import DEBUG
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(filename="wiki.log", level=logging.DEBUG)

logger = logging.getLogger(__name__)

LINK_FROMAT = u'<a href="{path}">{linktext}</a>'
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

def processmedia(text):
    mwcode = mwparserfromhell.parse(text)
    templates = mwcode.filter_templates()
    tags = mwcode.filter_tags()
    for template in templates:
        try:
            mwcode.remove(template)
        except ValueError as e:
            logger.warning("Unrenderable template")
    for tag in tags:
        if tag.__unicode__().startswith(u'<ref'):
            try:
                mwcode.remove(tag)
            except ValueError as e:
                logger.warning("Unrenderable template")
    return mwcode

def getOutlinks(id):
    outlinks = PageOutlinks.objects.filter(id=id)
    for outLink in outlinks:
        OUTLINK_TITLES.append(Page.objects.get(id=outLink.outlinks).name)


def addlinks(id,text):
    getOutlinks(id)
    text = _re_linktext.sub(processlink, text) # direct links
    text = _re_altlink.sub(processlink, text) # links with
    text = _re_media.sub("", text) # for File Wikitory and other wikimedia
    # text = processmedia(text) # infobox and related info
    OUTLINK_TITLES = []

    return text

# Create your views here.
def article(request, page_name):
    try:
        page = Page.objects.get(name=page_name)
    except Page.DoesNotExist as e:
        if PageRedirects.objects.filter(redirects__exact=page_name).exists():
            name = Page.objects.get(id=PageRedirects.objects.filter(redirects__exact=page_name)[0].id).name
            return redirect('/wiki/'+name)
        else:
            raise Http404("No such page exists")
    text = processmedia(page.text)
    text = addlinks(page.id, parse(text))
    context = {
    'name' : page.name.replace("_"," "),
    'text' : text,
    }
    return render(request,'wiki/article.html',context)

def home(request):
    context = {'title':"Home"}
    return render(request,'wiki/home.html',context)
