from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    url(r'^$',RedirectView.as_view(pattern_name='home', permanent=True)),
    url(r'(?P<page_name>[a-zA-Z_()-]+)/', views.article)
]
