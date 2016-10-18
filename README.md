# Django-semantic-wiki

A local wikipedia for the wikipedia database on a MySQL with sematic search using dbpedia's ontology built with django framework and love. The database was created using Wikipedia's XML dumps, which was parsed and stored.

### Dependencies
* [py-wikimarkup](https://github.com/dcramer/py-wikimarkup) is the parser used for the Mediawiki markup to HTML conversion. This can be installed with ```pip install py-wikimarkup```

* [SPARQLWrapper](https://rdflib.github.io/sparqlwrapper/) is a wrapper for SPARQL service. It helps in creating the query URI and provides formatted output. Install with ```pip install SPARQLWrapper```

* [nltk](https://github.com/nltk/nltk) is a suite of open source Python modules, data sets and tutorials supporting research and development in Natural Language Processing ```pip install nltk``` 

The database settings should be configured in ```/wiki_project/settings.py```


### Run
If database is not present ```python manage.py migrate```

To start the server ```python manage.py runserver```
