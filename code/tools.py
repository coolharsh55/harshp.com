import datetime
import os
import types
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

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

_pyg = {
    'lexers': {
        'turtle':get_lexer_by_name("turtle", stripall=True),
        'bash':get_lexer_by_name("bash", stripall=True),
        'python':get_lexer_by_name("python", stripall=True),
    },
    'formatter': HtmlFormatter(cssclass="source", noclasses=True)
}

from config import logging, DEBUG, INFO

from config import LOCAL_PATH
# Namespaces used in the RDF files
# RDF-ORM can also auto-detect them
SCHEMA = Namespace('https://schema.org/')
HPCOM = Namespace('https://harshp.com/code/vocab#')
HPVIEWS = Namespace('https://harshp.com/code/views#')

_DATA = {}


class CheckRW(object):
    _readonly = []
    _write = []
    READ = True
    WRITE = True

    @staticmethod
    def check_readonly(name):
        for path in CheckRW._readonly:
            if name.startswith(path):
                return True
        return False

    @staticmethod
    def add_readonly(name):
        DEBUG(f"{name} marked as readonly")
        CheckRW._readonly.append(name)

    @staticmethod
    def add_write(name):
        DEBUG(f"{name} marked as to-write")
        CheckRW._write.append(name)

def _register(key, value):
    _DATA[key] = value
    DEBUG(f"registered {key} in tools")

def _get_localised_path(iri):
    if not iri.startswith('https://harshp.com/'):
        raise Exception(f'Path {iri} is not local to harshp.com')
    return iri.replace('https://harshp.com/', LOCAL_PATH, 1)

def _is_schema_PresentationDigitalDocument(item):
    if type(item.rdf_type) is RDFS_Resource:
        type_iris = [item.rdf_type]
    if type(item.rdf_type) is list:
        type_iris = [URIRef(t.iri) for t in item.rdf_type]
    else:
        type_iris = [item.rdf_type]
    # for cat in item.rdf_type:
    #     DEBUG(f'{cat} {type(cat)} {type(HPCOM.FullPaper)}')
    if SCHEMA.PresentationDigitalDocument in type_iris:
        return True
    return False

# Tests that can be used within Jinja2 code
JINJA2_TESTS = {
    'RDFS_Resource': lambda x: type(x) is RDFS_Resource,
    'BNode': lambda x: x.startswith('u'),
    'schema_PresentationDigitalDocument': _is_schema_PresentationDigitalDocument,
}

def _get_view(item):
    """determine view to render this item with"""
    views=_DATA['views']
    RenderedItem=_DATA['RenderedItem']

    def _find_view(item):
        # DEBUG(item.iri)
        for view in views:
            if hasattr(view, 'hpcom_view_target'):
                target = view.hpcom_view_target
                # DEBUG(f'checking view {view} with target {target}')
                # DEBUG(f'{target.iri}')
                if target.iri == item.iri:
                    return view
    # a view can be defined in (order of checking)
    # content object associated with it
    # view declared as targeting this object
    # view declared as targeting the classes of this object
    # view declared as targeting the parent classes of this object
    # view declared as targeting rdfs:Resource (generic fallback)

    if hasattr(item, 'hpcom_renderWith'):
        # DEBUG('item declared its own renderer')
        return item.hpcom_renderWith

    # checking content for associated view
    if hasattr(item, 'hpcom_content'):
        content = item.hpcom_content
        # DEBUG(f'item has content {content}')
        if hasattr(content, 'hpcom_renderWith'):
            # DEBUG('item declared its own renderer')
            return content.hpcom_renderWith

    # object either has content with no view attached
    # or object does not have content
    # regardless, check if there is a view associated with iri
    for view in views:
        if hasattr(view, 'hpcom_view_target') and view.hpcom_view_target is item:
            return view

    # check view associated with classes of this object
    for parent in item.rdf_type:
        if parent is RenderedItem:
            continue
        # DEBUG(f'find view for parent: {parent} {type(parent)}')
        view = _find_view(parent)
        if view is not None:
            return view

    # check views associated with parents of parents
    ancestors = [p.rdf_type for p in item.rdf_type if hasattr(p, 'rdf_type')]
    while ancestors:
        ancestor = ancestors.pop()
        if not ancestor:
            break
        if type(ancestor) is list:
            temp = ancestor.pop()
            for a in ancestor:
                ancestors.insert(0, a)
            ancestor = temp
        view = _find_view(ancestor)
        if view is not None:
            return view

    # all avenues exhausted
    # return view for rdfs:resource
    return _DATA['view_rdfs_resource']

def prefix_this(item):
    # DEBUG(f'item: {item} type: {type(item)}')
    if type(item) is RDFS_Resource:
        item = item.iri
    elif type(item) is URIRef:
        item = str(item)
    if type(item) is str and item.startswith('http'):
        iri = URIRef(item).n3(_DATA['data'].graph.namespace_manager)
    else:
        iri = item
    if iri.count('_') > 0:
        iri = iri.split('_', 1)[1]
    # DEBUG(f'prefixed {item} to: {iri}')
    return iri



def _execute_sparql(data, query, bindings=None):
    """execute given sparql query and return results
    supplement query with given bindings"""
    DEBUG(f'executing query: {query}')
    results = data.graph.query(query, initBindings=bindings)
    for row in results:
        DEBUG(row)
        # DEBUG(data.resolve_entities_to_objects(row))
    DEBUG(f'query returned {len(results)} rows')
    return [data.resolve_entities_to_objects(row) for row in results]


def _view_filecopy(path, *args):
    """simple writer --> will write contents to path
    ensures folder structure exists before writing"""
    with open(path, 'w') as fd:
        DEBUG(f'writing file {path}')
        fd.writelines(contents)
    return


JINAJ2_TEMPLATE_VARS = {
    'RDF_DESC_PROP': ('rdf_type', 'schema_name', 'schema_url'),
    'prefix_this': prefix_this,
}

def html_view(item):
    if hasattr(item, 'schema_url'):
        s = f'<a href="{item.schema_url}">{str(item)}</a>'
    elif type(item) is RDFS_Resource:
        s = f'<a href="{item.iri}">{str(item)}</a>'
    elif type(item) is str and item.startswith('http'):
        s = f'<a href="{item}">{str(item)}</a>'
    else:
        s = item
        if s == "true":
            s = "✅"
        elif s == "false":
            s = "❌"
    # DEBUG(f'html for item {item} type{type(item)} is {s}')
    return s

def publication_type(publication):
    type_iris = [URIRef(t.iri) for t in publication.rdf_type]
    # for cat in publication.rdf_type:
    #     DEBUG(f'{cat} {type(cat)} {type(HPCOM.FullPaper)}')
    if HPCOM.Thesis in type_iris:
        s = f'Thesis'
    elif HPCOM.FullPaper in type_iris:
        if hasattr(publication, 'schema_publisher'):
            if type(publication.schema_publisher.rdf_type) is list:
                for parent in publication.schema_publisher.rdf_type:
                    if str(parent) == str(SCHEMA.Periodical):
                        s = 'Journal'
                        break
            elif str(publication.schema_publisher.rdf_type) == str(SCHEMA.Periodical):
                s = 'Journal'
            else:
                s = str(publication.schema_publication.hpcom_event_type)
        else:
            s = str(publication.schema_publication.hpcom_event_type)
    elif HPCOM.ShortPaper in type_iris:
        s = 'Short Paper'
    elif HPCOM.Abstract in type_iris:
        s = 'Abstract'
    elif HPCOM.ExtendedAbstract in type_iris:
        s = 'Ext. Abstract'
    elif HPCOM.BookChapter in type_iris:
        s = 'Book Chapter'
    elif HPCOM.Report in type_iris:
        s = 'Report'
    else:
        s = 'Publication'
    # if hasattr(publication, 'hpcom_peer_reviewed') \
    #     and publication.hpcom_peer_reviewed == "true":
    #     s = f'{s}, peer-reviewed'
    return s


def in_past(timestamp):
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    return timestamp < now


def format_amount(amount):
    amount = int(amount)
    return '{:0,}'.format(amount)


def publication_is_draft(publication):
    return HPCOM.DraftPaper in (URIRef(t.iri) for t in publication.rdf_type)


def _is_rdf_type(item, rdf_type):
    if type(item) is RDFS_Resource:
        if type(item.rdf_type) is list:
            for item_type in item.rdf_type:
                if prefix_this(item_type) == rdf_type:
                    return True
        else:
            if prefix_this(item.rdf_type) == rdf_type:
                return True
    return False


def _rdf_check_object(s, p, o):
    if not hasattr(s, p):
        return False
    sp = str(getattr(s, p).iri)
    so = str(o)
    return sp == so


def _view_empty(*args, **kwargs):
    """dummy view, does nothing"""
    pass

def _view_jinja2(path, metadata=None):
    """jinja2 renderer --> renders contents using Jinja2
    requires metadata['template'] to render with"""
    assert('template' in metadata)
    template_dir, template_file = os.path.split(
        _get_localised_path(metadata['template']))
    template_loader = FileSystemLoader(searchpath=template_dir)
    template_env = Environment(
        loader=template_loader, 
        autoescape=True, trim_blocks=True, lstrip_blocks=True)
    template_env.tests.update(JINJA2_TESTS)
    template_env.filters.update(JINJA2_FILTERS)
    template_env.globals.update(JINJA2_FUNCS)
    template = template_env.get_template(template_file)
    if not path.endswith('html'):
        if not os.path.isdir(path):
            path = f'{path}.html'
        else:
            path = f'{path}/index.html'
    DEBUG(f'writing {metadata["item"].iri} to {path}')
    RenderedItem = _DATA['RenderedItem']
    with open(path, 'w+') as fd:
        fd.write(template.render(
            **metadata, RenderedItem=RenderedItem, 
            **JINAJ2_TEMPLATE_VARS, SCHEMA=SCHEMA, HPCOM=HPCOM))


def _resolve_view_and_write(view, path, metadata=None):
    """gets view associated with renderer and passes on data to it
    metadata can contain anything required for the view to render
    """
    # DEBUG(f'{view.hpcom_view_renderer}')
    renderer = view.hpcom_view_renderer
    if renderer.iri not in VIEW_DICT:
        raise Exception(f'Renderer {renderer} is not registered with any handler')

    view = VIEW_DICT[renderer.iri]
    view(path, metadata)


def _today():
    literal = Literal(datetime.datetime.now(), datatype=XSD.dateTime)
    return literal

def _year_start():
    literal = Literal(
        datetime.datetime.now().replace(
            day=1,month=1,hour=0,minute=0), datatype=XSD.dateTime)
    return literal


def render_item(item):
    """generate html file for item using its view"""
    data = _DATA['data']
    assert(item.view)
    DEBUG(f'rendering {item} with view {item.view}')

    # at this point, the object can be rendered
    view = item.view
    metadata = { 'item': item }  # metadata of item for rendering

    # 1) get template attached with file if it exists
    # 2) if (1) does not exist, get template attached with view
    template = None
    if hasattr(item, 'hpcom_content') \
            and hasattr(item.hpcom_content, 'hpcom_view_template'):
        template = item.hpcom_content.hpcom_view_template
    elif hasattr(view, 'hpcom_view_template'):
        template = view.hpcom_view_template
    else:
        template = 'https://harshp.com/code/templates/template_base.jinja2'
    metadata['template'] = template

    # 3) get content file for item if it exists
    contents = None
    if hasattr(item, 'hpcom_content') \
            and hasattr(item.hpcom_content, 'hpcom_contentFile'):
        content_file = item.hpcom_content.hpcom_contentFile
        content_file_format = item.hpcom_content.hpcom_contentFileFormat
        path = _get_localised_path(content_file)
        with open(path, 'r') as fd:
            contents = fd.read()

        if hasattr(item, 'hpcom_code_highlight'):
            import re
            pattern = re.compile(r'<highlight>(.*?)</highlight>', re.DOTALL)
            contents = pattern.sub(
                lambda match: highlight_turtle(match.group(1).strip()), 
                contents)

    metadata['contents'] = contents

    if not contents and not template:
        # no contents, no template --> this item cannot be rendered
        raise Exception(f'{iri} has no content nor template, cannot render')

    # 4) get SPARQL query for renderer if exists
    sparql_source = None
    if hasattr(item, 'hpcom_sparql'):
        sparql_source = item.hpcom_sparql
    elif hasattr(view, 'hpcom_sparql'):
        sparql_source = view.hpcom_sparql

    if sparql_source:
        # DEBUG(f'sparql source: {sparql_source}')
        if type(sparql_source) is not list:
            sparql_source = [sparql_source]
        for node in sparql_source:
            label = str(node.rdfs_label)
            bindings= { 'iri': URIRef(item.iri) }
            if hasattr(node, 'hpcom_queryParam'):
                param = node.hpcom_queryParam
                param_label = str(param.hpcom_queryParamLabel)
                param_action = SPARQL_ACTIONS[str(param.hpcom_queryParamValue)]
                param_value = param_action()
                # DEBUG(f'query parameters with label {param_label} and value {param_value}')
                bindings[param_label] = param_value

            metadata[f'{label}_sparql'] = node.hpcom_queryString
            metadata [label] = _execute_sparql(
                    data, node.hpcom_queryString, bindings=bindings)

    # call function handling views
    # just contents, no template --> directly generate the file
    path = _get_localised_path(item.iri)
    if path.endswith('/'):
        path = f'{path}index.html'
    if path.startswith('../code/vocab#'):
        path = path.replace('../code/vocab#', '../resources/')
    _resolve_view_and_write(view, path, metadata)


def highlight_turtle(contents):
    return highlight(contents.strip(), _pyg['lexers']['turtle'], _pyg['formatter'])


def find_missing_tags(data):
    # store missing tags
    sparql_missing_tags = """
        SELECT DISTINCT ?tag WHERE {
            ?article hpcom:tag ?tag .
            FILTER NOT EXISTS { ?tag schema:name ?name } .
        } ORDER BY ?tag
        """
    results = data.graph.query(sparql_missing_tags)
    if len(results) > 0:
        with open('tags_missing.ttl', 'w+') as fd:
            for tag in results:
                iri = tag[0]
                prefixed = prefix_this(iri)
                name = prefixed.split(':')[1]
                print(f"""{prefixed} a hpcom:RenderedItem, hpcom:Tag ;
                    schema:name "{name}"@en ;
                    schema:url "{iri}"^^xsd:anyURI .
                    """, file=fd)
        logging.warning(f'found {len(results)} missing tags, check tags_missing.ttl')


def xjoin(data):
    if type(data) is not list:
        return data
    data.sort()
    return ', '.join([str(x) for x in data])


VIEW_DICT = {
    'https://harshp.com/code/vocab#FileCopy': _view_filecopy,
    'https://harshp.com/code/vocab#Jinja2': _view_jinja2,
    'https://harshp.com/code/vocab#EmptyRenderer': _view_empty,
}


SPARQL_ACTIONS = {
    'date-today': _today,
    'date-year-start': _year_start,
}

JINJA2_FILTERS = {
    'html_view': html_view,
    'publication_type': publication_type,
    'year': lambda x: x[:4],
    'in_past': in_past,
    'format_amount': format_amount,
    'publication_is_draft': publication_is_draft,
    'xjoin': xjoin
}


JINJA2_FUNCS = {
    'is_rdf_type': _is_rdf_type,
    'rdf_check_object': _rdf_check_object,
}