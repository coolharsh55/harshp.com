#!/usr/bin/env python3

from urllib import request
from rdflib import Graph
import csv

query_books = (
    (
        'iri', 'id', 'name', 'author', 'date_created',
        'medium_owned', 'medium_read', 'status', 'date_read', 'rating', 
        'genre', 'list', 'review',
    ),
    '''
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix dct: <http://purl.org/dc/terms/> 
    prefix time: <http://www.w3.org/2006/time#> 
    prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    prefix schema: <https://schema.org/> 
    prefix hpcom: <https://harshp.com/code/vocab#> 
    prefix hpview: <https://harshp.com/code/views#> 
    prefix hptag: <https://harshp.com/tags/> 
    prefix list: <https://harshp.com/hobbies/books/lists/> 

    select
        ?iri ?id ?name ?author ?date_created
        ?medium_owned ?medium_read ?status ?date_read ?rating 
        ?genre ?list ?review
    {
        ?iri a schema:Book .
        ?iri hpcom:book_id ?id .
        OPTIONAL {
            SELECT ?iri (GROUP_CONCAT(?o; separator=";") AS ?medium_owned)
            WHERE {
                ?iri hpcom:book_owned_medium ?o
            }
            GROUP BY ?iri
        }
        OPTIONAL {
            SELECT ?iri (GROUP_CONCAT(?o; separator=";") AS ?medium_read)
            WHERE {
                ?iri hpcom:book_read_medium ?o
            }
            GROUP BY ?iri
        }
        OPTIONAL {
            SELECT ?iri (GROUP_CONCAT(?g; separator=";") AS ?genre)
            WHERE {
                ?iri schema:genre ?g
            }
            GROUP BY ?iri
        }
        OPTIONAL { ?iri hpcom:book_status ?status } .
        OPTIONAL { ?iri hpcom:date_book_read ?date_read } .
        OPTIONAL { ?iri schema:aggregatedRating ?rating } .
        ?iri schema:author ?author .
        ?iri schema:dateCreated ?date_created .
        ?iri schema:name ?name .
        OPTIONAL {
            SELECT ?iri (GROUP_CONCAT(?g; separator=";") AS ?genre)
            WHERE {
                ?iri schema:genre ?g
            }
            GROUP BY ?iri
        }

        OPTIONAL {
            SELECT ?iri (GROUP_CONCAT(?l; separator=";") AS ?list)
            WHERE {
                ?iri schema:isPartOf ?l
            }
            GROUP BY ?iri
        }
        OPTIONAL {
            ?iri schema:review ?review .
        }
    } order by ?id
    ''')

query_bookstoread = (
    ('name', 'author',),
    '''
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix dct: <http://purl.org/dc/terms/> 
    prefix time: <http://www.w3.org/2006/time#> 
    prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    prefix schema: <https://schema.org/> 
    prefix hpcom: <https://harshp.com/code/vocab#> 
    prefix hpview: <https://harshp.com/code/views#> 
    prefix hptag: <https://harshp.com/tags/> 
    prefix list: <https://harshp.com/hobbies/books/lists/> 

    select
        ?name ?author
    {
        ?iri a schema:Book .
        ?iri hpcom:book_id ?id .
        ?iri schema:author ?author .
        ?iri schema:name ?name .
        ?iri hpcom:book_status hpcom:book-to-read .
        FILTER NOT EXISTS { ?iri hpcom:book_owned_medium ?owned }
    } order by ?id
    ''')


def write_csv(header, query):
    graph = Graph()
    graph.parse('content/hobbies/books.ttl', format='turtle')
    results = graph.query(query)
    # print(len(results))

    with open(f'content/hobbies/bookstoread.csv', 'w', newline='') as fd:
        writer = csv.writer(fd)
        writer.writerow(header)
        for row in results:
            writer.writerow(row)
    print("CSV written")


def download_csv():
    url = 'https://docs.google.com/spreadsheets/d/1wnivY54pgSOZ_r2tvJkpZuBbXRRYoV8zJxERBis-4zw/export?exportFormat=csv&format=csv&title=books'
    request.urlretrieve(url, f'content/hobbies/books.csv')
    print("CSV downloaded")


def write_ttl():
    with open(f'content/hobbies/books.csv') as fd:
        reader = csv.DictReader(fd)
        from collections import namedtuple
        Book = namedtuple("Book", reader.fieldnames)
        books = [Book(**row) for row in reader]
    # print(books[0])
    g = Graph()

    from rdflib import Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, XSD

    DCT = Namespace("http://purl.org/dc/terms/")
    TIME = Namespace("http://www.w3.org/2006/time#")
    SCHEMA = Namespace("https://schema.org/")
    HPCOM = Namespace("https://harshp.com/code/vocab#")
    HPVIEW = Namespace("https://harshp.com/code/views#")
    HPTAG = Namespace("https://harshp.com/tags/")
    HPLIST = Namespace("https://harshp.com/hobbies/books/lists/")
    HPBOOK = Namespace("https://harshp.com/hobbies/books/")
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("dct", DCT)
    g.bind("time", TIME)
    g.bind("xsd", XSD)
    g.bind("schema", SCHEMA)
    g.bind("hpcom", HPCOM)
    g.bind("hpview", HPVIEW)
    g.bind("hptag", HPTAG)
    g.bind("hplist", HPLIST)

    booksiri = URIRef('https://harshp.com/hobbies/books')
    g.add((booksiri, RDF.type, RDFS.Class))
    g.add((booksiri, RDF.type, HPCOM.RenderedItem))
    g.add((booksiri, RDF.type, SCHEMA.BlogPosting))
    g.add((booksiri, SCHEMA.name, Literal("Books", lang='en')))
    g.add((booksiri, SCHEMA.url, Literal(booksiri, datatype=XSD.anyURI)))

    for book in books:
        iri = HPBOOK[book.id]
        # print(iri)
        # print(book)
        # <https://harshp.com/hobbies/books/947> a schema:Book, hpcom:RenderedItem ;
        g.add((iri, RDF.type, HPCOM.RenderedItem))
        g.add((iri, RDF.type, HPCOM.BookReading))
        g.add((iri, RDF.type, SCHEMA.Book))
        g.add((iri, RDF.type, HPCOM.Book))
        # hpcom:book_id "947"^^xsd:int ;
        g.add((iri, HPCOM.book_id, HPCOM[book.id]))
        # schema:url "https://harshp.com/hobbies/books/947"^^xsd:anyURI .
        g.add((iri, SCHEMA.url, Literal(HPBOOK[book.id], datatype=XSD.anyURI)))
        # schema:name "Atomic Habits: An Easy & ProvenWay to Build Good Habits & Break Bad Ones"@en ;
        g.add((iri, SCHEMA.name, Literal(book.name)))
        # schema:author "James Clear"^^xsd:string ;
        g.add((iri, SCHEMA.author, Literal(book.author)))
        # schema:dateCreated "2018"^^xsd:int ;
        g.add((iri, SCHEMA.dateCreated, Literal(book.date_created, datatype=XSD.int)))
        # schema:genre hpcom:BookNonFiction ;
        genres = book.genre.split(';')
        for genre in genres:
            g.add((iri, SCHEMA.genre, HPCOM[genre]))
        # hpcom:book_owned_medium hpcom:PhysicalBook ;
        if book.medium_owned:
            g.add((iri, HPCOM.book_owned_medium, HPCOM[book.medium_owned]))
        # hpcom:book_status hpcom:book-read ;
        # print(book.status)
        g.add((iri, HPCOM.book_status, HPCOM[f"book-{book.status}"]))
        if book.status == 'read':
            # schema:aggregatedRating hptag:Rating5 ;
            g.add((iri, SCHEMA.aggregatedRating, HPCOM[f"Rating{book.rating}"]))
            # hpcom:date_book_read "2025-11-23T12:00:00"^^xsd:dateTime ;
            if book.date_read:
                g.add((iri, HPCOM.date_book_read, Literal(book.date_read, datatype=XSD.dateTime)))
            # hpcom:book_read_medium hpcom:PhysicalBook ;
            g.add((iri, HPCOM.book_read_medium, HPCOM[book.medium_read]))
            # schema:review """..."""
            if book.review:
                g.add((iri, SCHEMA.review, Literal(book.review, lang='en')))
        # hpcom:list list:books-changed-life ;
        if book.list:
            booklists = book.list.split(';')
            for booklist in booklists:
                g.add((iri, SCHEMA.isPartOf, HPLIST[booklist]))

    g.serialize('content/hobbies/books.ttl', format='ttl')
    print("RDF written")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--all', action='store_true', help="download CSV and create RDF")
    parser.add_argument('-U', '--unread', action='store_true', help="create books.csv for UNREAD BOOKS from RDF")
    parser.add_argument('-D', '--download', action='store_true', help="download CSV from ONLINE spreadsheet")
    parser.add_argument('-C', '--create', action='store_true', help="update RDF from CSV")
    args = parser.parse_args()
    
    if args.all:
        download_csv()
        write_ttl()
    elif args.unread:
        header, query = query_bookstoread
        write_csv(header, query)
    elif args.download:
        download_csv()
    elif args.create:
        write_ttl()
    else:
        raise ValueError("unknown or incorrect argument")

    