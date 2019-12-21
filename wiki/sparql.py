from SPARQLWrapper import SPARQLWrapper, JSON

ALL_PROPERTIES ="""
PREFIX dbr:<http://dbpedia.org/resource/>
select distinct ?property {
  { dbr:%s ?property ?o }
  union
  { ?o ?property dbr:%s }
}"""

ABSTRACT = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?abstract
    WHERE { <http://dbpedia.org/resource/%s> dbo:abstract ?abstract
    FILTER (langMatches(lang(?abstract),"en")) }
"""

GET_RELATION = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    SELECT ?res
    WHERE {
        <http://dbpedia.org/resource/%s> <%s> ?res.
}"""

def abstract_fetch(page):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = ABSTRACT % (page)
    abstract = ""
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparqlresults = sparql.query().convert()
    if sparqlresults["results"]["bindings"]:
        abstract = sparqlresults["results"]["bindings"][0]["abstract"]["value"]
    return abstract


def prop_fetch(prop_name_partial, page_exact):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = ALL_PROPERTIES % (page_exact,page_exact)
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparqlresults = sparql.query().convert()
    preperties = []
    if sparqlresults["results"]["bindings"]:
        print(sparqlresults['results']['bindings'])
        for props in sparqlresults["results"]["bindings"]:
            if prop_name_partial.lower() in props['property']['value'].split('/')[-1].lower():
                print(props['property']['value'])
                sub_query = GET_RELATION % (page_exact,props['property']['value'])
                print(sub_query)
                sparql.setQuery(sub_query)
                sparql.setReturnFormat(JSON)
                sub_sparqlresults = sparql.query().convert()
                print(sub_sparqlresults['results']['bindings'])
                if sub_sparqlresults["results"]["bindings"]:
                    for result in sub_sparqlresults["results"]["bindings"]:
                        if result['res']['type'] != 'uri':
                            yield {'type':'raw','property':props['property']['value'].split('/')[-1],'value':result['res']['value']}
                        else:
                            yield {'type':'resource','property':props['property']['value'].split('/')[-1],'value':result['res']['value'].split('/')[-1]}


ALL_CLASSES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT distinct ?subject ?predicate
WHERE 
{?subject ?predicate rdfs:Class}
LIMIT 1000
"""

CLASS_PROPERTIES = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?o
    WHERE {
        <%s> rdfs:label ?o.
}"""

def _class_prop_fetch():
    sparql = SPARQLWrapper("http://127.0.0.1:3030/neo/sparql")
    query = ALL_CLASSES
    class_list = []
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparqlresults = sparql.query().convert()
    if sparqlresults["results"]["bindings"]:
        print(sparqlresults["results"]["bindings"])
        for cls in sparqlresults["results"]["bindings"]:
            # s = aclass["subject"]["value"].split('/')[-1]
            s = cls["subject"]["value"]
            print(s)
            # class_list.append(aklass)
            sub_query = CLASS_PROPERTIES % (s)
            sparql.setQuery(sub_query)
            sparql.setReturnFormat(JSON)
            sub_sparqlresults = sparql.query().convert()
            if sub_sparqlresults["results"]["bindings"]:
                for prop in sub_sparqlresults["results"]["bindings"]:
                    # p = prop["property"]["value"]
                    o = prop["o"]["value"]
                    class_list.append({'s':s, 'o':o})
    return class_list



CLASS_LABEL_COMMENT = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT distinct ?s ?label ?comment
WHERE 
{
  ?s rdfs:label  ?label. 
  ?s rdfs:comment  ?comment.
}
"""

def _class_label_comment_fetch():
    sparql = SPARQLWrapper("http://127.0.0.1:3030/neo/sparql")
    query = CLASS_LABEL_COMMENT
    rs_list = []
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparqlresults = sparql.query().convert()
    if sparqlresults["results"]["bindings"]:
        print(sparqlresults["results"]["bindings"])
        for rs in sparqlresults["results"]["bindings"]:
            # s = aclass["subject"]["value"].split('/')[-1]
            s = rs["s"]["value"]
            l = rs["label"]["value"]
            c = rs["comment"]["value"]
            print(s, l, c)
            rs_list.append({'s':s, 'l':l, 'c':c})
    return rs_list


def test():
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = ALL_PROPERTIES % ('Moon','Moon')
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparqlresults = sparql.query().convert()
    preperties = []
    if sparqlresults["results"]["bindings"]:
        for props in sparqlresults["results"]["bindings"]:
            print(props['property']['value'])
            sub_query = GET_RELATION % ('Moon',props['property']['value'])
            sparql.setQuery(sub_query)
            sparql.setReturnFormat(JSON)
            sub_sparqlresults = sparql.query().convert()
            if sub_sparqlresults["results"]["bindings"]:
                for i in sub_sparqlresults["results"]["bindings"]:
                    print(i)


    # query = ABSTRACT_SPARQL % (page.capitalize())
    # print(query)
    # sparql.setQuery(query)
    # sparql.setReturnFormat(JSON)
    # sparqlresults = sparql.query().convert()
    # suggestion = {'page':page,'linktext':page.replace("_"," ")}
    # abstract = ""
    # if sparqlresults["results"]["bindings"]:
    #     abstract = sparqlresults["results"]["bindings"][0]["abstract"]["value"]
    # suggestion.update({'abstract':abstract})
    # suggestions.append(suggestion)


if __name__ == '__main__':
    # 1. only India leader
    # for prop in prop_fetch('leader','India'):
    #     print(prop)

    # 2. Moon - Moon all list
    # test()

    # 3. localhost sparql endpoint when sub query
    # _class_prop_fetch()

    # 4. local when one query
    _class_label_comment_fetch()
