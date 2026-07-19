#!/usr/bin/env python3

"""Generator for HTML

This is the main file that takes in the data written inside ttl files
and renders it into static HTML files that can be served via a server.

The gist of the approach is thus:
* RDF data is based on IRIs which act as unique identifiers for each node 
* A RenderedItem is a class that represents nodes to be rendered in HTML
* The generator loads all RDF data, then looks for instances of RenderedItem
* A 'view' is a way to render a node
* Views can be defined at any arbitrary level e.g. node, class, generic
* The generator will find an appropriate view to render the node
* The generator then executes the view
* If the view contains a SPARQL query, the generator will execute it
* Results of the query are passed to the view as data

The file is to be executed as a script `python generator.py`
It does not have a mains method.
"""

import datetime
import os
# RDFlib is used to interact with RDF data
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import NamespaceManager
from rdflib.namespace import XSD
from rdflib import RDF, RDFS
from rdflib.term import Literal, URIRef
# RDF-SPARQL is a plugin for RDFlib for executing SPARQL queries
from rdflib.plugins.sparql import prepareQuery
# RDF-ORM is a custom library for conveniently using RDF in Python
from rdform import DataGraph, RDFS_Resource
# Jinja2 is used as the templating engine for rendering HTML
from jinja2 import FileSystemLoader
from jinja2 import Environment

import tools
from config import logging, DEBUG, INFO


def load_graphs(content_write):
    def _load(graph, path):
        try:
            # TODO: check format by extension, it assumed as ttl now
            graph.parse(path, format='turtle')
        except Exception as E:
            logging.error(f"Error occured for path {path}")
            raise

    '''loads content files into RDF graph'''
    from config import CONTENT
    # load data from files into graph
    graph = Graph()
    contentlist = list(CONTENT.keys())
    for content in content_write:
        if content not in CONTENT:
            raise AttributeError(f"No content called {content}")
        contentlist.remove(content)
        filelist = CONTENT[content]['files']
        tools.CheckRW.add_write(CONTENT[content]['iripath'])
        DEBUG(f"following files will be loaded for content {content}")
        DEBUG(f"{filelist}")
        for file in filelist:
            _load(graph, file)
    for content in contentlist:
        filelist = CONTENT[content]['files']
        tools.CheckRW.add_readonly(CONTENT[content]['iripath'])
        DEBUG(f"following files will be loaded for content {content}")
        DEBUG(f"{filelist}")
        for file in filelist:
            _load(graph, file)

    # Prints recent books read with dates
    # query = '''
    #     prefix hpcom: <https://harshp.com/code/vocab#>
    #     prefix schema: <https://schema.org/>  
    #     SELECT ?id ?date_read WHERE {
    #         ?book a schema:Book . 
    #         ?book hpcom:book_id ?id .
    #         ?book hpcom:book_status hpcom:book-read .
    #         ?book hpcom:date_book_read ?date_read .
    #     } ORDER BY DESC(?date_read) LIMIT 20
    # '''
    # results = graph.query(query)
    # for row in results:
    #     print(f"{row[0]} {row[1]}")
        
    validate_constraints(graph)

    # create data graph through ORM
    data = DataGraph()
    data.load(graph)
    # This create a namespace mapping for the namespaces defined in graph
    # E.g. 'rdfs' will be k="rdfs" v="Namespace(RDFS IRI)"
    data.graph.ns = { k:v for k,v in data.graph.namespaces() }
    tools._register('data', data)
    INFO(f"Successfully loaded {len(graph)} triples")
    return data


def validate_constraints(graph):
    '''validates RDf graph using SHACL'''
    # validate using PySHACL
    from config import FLAG_VALIDATE_CONSTRAINTS
    # FIXME: manual override
    # FLAG_VALIDATE_CONSTRAINTS = False
    if FLAG_VALIDATE_CONSTRAINTS:
        logging.info("Validating data...")
        from pyshacl import validate
        validation_constraints = Graph()
        validation_constraints.parse('shacl_constraints.ttl', format='turtle')
        validation_results = validate(graph,
              shacl_graph=validation_constraints,
              ont_graph=None,
              inference='rdfs',
              abort_on_first=False,
              allow_infos=False,
              allow_warnings=False,
              meta_shacl=False,
              advanced=True,
              js=False,
              debug=False)
        conforms, results_graph, results_text = validation_results
        # DEBUG(conforms)
        # DEBUG(f"{results_text=}")
        results_graph.serialize('validation_errors.ttl', format='turtle')
        if conforms is False:
            # logging.error(results_text)
            # for error in results_graph:
            #     print(error)
            sparql_error = """
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                SELECT ?book ?message
                WHERE {
                    ?result a sh:ValidationResult ;
                            sh:focusNode ?book .
                    OPTIONAL { ?result sh:detail/sh:resultMessage ?detailMessage } .
                    OPTIONAL { ?result sh:resultMessage ?resultMessage } .
                    FILTER NOT EXISTS { ?parent sh:detail ?result } .
                    BIND(COALESCE(?detailMessage, ?resultMessage) AS ?message)
                }
                """
            # DEBUG(list(results_graph.query(sparql_error)))
            results = list(results_graph.query(sparql_error))
            results.sort(key=lambda x: int(x.book.split('/')[-1]))
            for row in results:
                book = row.book.split('/')[-1]
                INFO(f"Error in Book#{book}: {row.message}")
            raise AssertionError("Validation of RDF graph FAILED")
        else:
            INFO("Validation PASSED")
        graph.serialize('data_combined.ttl', format='turtle')
        INFO("Graph serialised as 'data_combined.ttl'")
    else:
        logging.info("Validation SKIPPED")


def get_rendered_items(data):
    '''retrieve items from data graph that should be rendered'''
    # rendered items are those that should be created into files
    # they are defined as hpcom:RenderedItem
    rendered_items = data.get_instances_of('hpcom_RenderedItem')
    # Views define how the RDF data gets rendered into formats
    views = data.get_instances_of('hpcom_View')
    # DEBUG(f'registered views: {views}')
    tools._register('views', views)
    # RDFS Resource View is a generic view targeting rdfs:Resource
    # If all other views fail or are not found, it gets selected
    view_rdfs_resource = data.get_entity('hpview_RDFSResourceView')
    tools._register('view_rdfs_resource', view_rdfs_resource)
    # DEBUG(f'default view: {view_rdfs_resource}')
    RenderedItem = data.get_entity('hpcom_RenderedItem')
    tools._register('RenderedItem', RenderedItem)
    INFO(f"Queued {len(rendered_items)} items to render")
    return rendered_items


def render_items(render_items):
    from tools import _get_view, render_item
    DEBUG('Retrieving Views and Renderers')
    counter_rendered = 0
    counter_skipped = 0
    for item in rendered_items:
        if tools.CheckRW.check_readonly(item.iri):
            DEBUG(f'handling item: {item.iri} -- SKIPPED')
            counter_skipped += 1
            continue
        DEBUG(f'render {item.iri}')
        view = _get_view(item)
        DEBUG(f'render with: {view}')
        assert(view)
        item.view = view
        render_item(item)
        counter_rendered += 1
    INFO(f"Rendered {counter_rendered} items; skipped {counter_skipped} items")


def _parse_arguments():
    import argparse
    parser = argparse.ArgumentParser()
    # - `-d` will download and extract ALL files
    parser.add_argument('-c', '--content', nargs='+', help="content to generate")
    parser.add_argument('-A', '--allcontents', action='store_true', help="generate all contents")
    parser.add_argument('-D', '--debug', action='store_true', help="enable debug logs")
    parser.add_argument('-V', '--validate', action='store_true', help="validation only")
    args = parser.parse_args()
    import sys
    if len(sys.argv) < 2:
        parser.print_usage()
        return
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        # logging.disable(logging.DEBUG)
        logging.getLogger().setLevel(logging.INFO)
    if args.content:
        content = ['site']
        content += [x.strip() for x in args.content[0].split(',')]
    if args.allcontents:
        from config import CONTENT
        content = CONTENT.keys()
    INFO(f"generator input: {content}")
    return args, content

if __name__ == '__main__':
    args, content_write = _parse_arguments()
    if not content_write:
        INFO('No content specified to generate')
        import sys
        sys.exit(0)
    data = load_graphs(content_write)
    if args.validate:
        INFO("Skipping rendering due to validation only flag")
    else:
        rendered_items = get_rendered_items(data)
        render_items(rendered_items)