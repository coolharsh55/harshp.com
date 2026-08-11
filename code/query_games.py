#!/usr/bin/env python3

from urllib import request
from rdflib import Graph
import csv


def download_csv():
    url = 'https://docs.google.com/spreadsheets/d/1wnivY54pgSOZ_r2tvJkpZuBbXRRYoV8zJxERBis-4zw/export?gid=477530597&exportFormat=csv&format=csv&title=games'
    request.urlretrieve(url, f'content/hobbies/games.csv')
    print("CSV downloaded")


def write_ttl():
    with open(f'content/hobbies/games.csv') as fd:
        reader = csv.DictReader(fd)
        from collections import namedtuple
        Game = namedtuple("Game", reader.fieldnames)
        games = [Game(**row) for row in reader]
    g = Graph()

    from rdflib import Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, XSD

    DCT = Namespace("http://purl.org/dc/terms/")
    TIME = Namespace("http://www.w3.org/2006/time#")
    SCHEMA = Namespace("https://schema.org/")
    HPCOM = Namespace("https://harshp.com/code/vocab#")
    HPVIEW = Namespace("https://harshp.com/code/views#")
    HPTAG = Namespace("https://harshp.com/tags/")
    HPLIST = Namespace("https://harshp.com/hobbies/games/lists/")
    HPGAME = Namespace("https://harshp.com/hobbies/games/")
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

    gamesiri = URIRef('https://harshp.com/hobbies/games')
    g.add((gamesiri, RDF.type, RDFS.Class))
    g.add((gamesiri, RDF.type, HPCOM.RenderedItem))
    g.add((gamesiri, RDF.type, SCHEMA.BlogPosting))
    g.add((gamesiri, SCHEMA.name, Literal("Games", lang='en')))
    g.add((gamesiri, SCHEMA.url, Literal(gamesiri, datatype=XSD.anyURI)))

    for game in games:
        iri = HPGAME[game.id]
        # print(iri)
        # print(game)
        # <https://harshp.com/hobbies/games/947> a schema:Book, hpcom:RenderedItem ;
        g.add((iri, RDF.type, HPCOM.RenderedItem))
        g.add((iri, RDF.type, SCHEMA.VideoGame))
        g.add((iri, RDF.type, HPCOM.VideoGame))
        # hpcom:game_id "947"^^xsd:int ;
        g.add((iri, HPCOM["game-id"], Literal(game.id, datatype=XSD.int)))
        # schema:url "https://harshp.com/hobbies/games/947"^^xsd:anyURI .
        g.add((iri, SCHEMA.url, Literal(HPGAME[game.id], datatype=XSD.anyURI)))
        # schema:name "Atomic Habits: An Easy & ProvenWay to Build Good Habits & Break Bad Ones"@en ;
        g.add((iri, SCHEMA.name, Literal(game.name)))
        # schema:author "James Clear"^^xsd:string ;
        g.add((iri, SCHEMA.author, Literal(game.developer)))
        g.add((iri, SCHEMA.publisher, Literal(game.publisher)))
        # schema:dateCreated "2018"^^xsd:int ;
        g.add((iri, SCHEMA.dateCreated, Literal(game.publisher, datatype=XSD.int)))
        # schema:genre hpcom:BookNonFiction ;
        genres = game.genre.split(';')
        for genre in genres:
            g.add((iri, SCHEMA.genre, HPCOM[genre]))
        # hpcom:game_owned_medium hpcom:PhysicalBook ;
        if game.owned:
            for platform in game.owned.split(','):
                g.add((iri, HPCOM["game-owned-platform"], HPCOM[platform]))
        # hpcom:game_status hpcom:game-read ;
        # print(game.status)
        g.add((iri, HPCOM["game-status"], HPCOM[f"game-{game.status}"]))
        if game.status == 'played':
            # schema:aggregatedRating hptag:Rating5 ;
            g.add((iri, SCHEMA.aggregatedRating, HPTAG[f"Rating{game.rating}"]))
            # hpcom:date_game_read "2025-11-23T12:00:00"^^xsd:dateTime ;
            if game.played_year:
                for year in game.played_year.split(','):
                    g.add((iri, HPCOM["date-game-played"], Literal(year, datatype=XSD.int)))
            # hpcom:game_read_medium hpcom:PhysicalBook ;
            if game.played_platform:
                for platform in game.played_platform.split(','):
                    g.add((iri, HPCOM["game-platform-played"], HPCOM[platform]))
            # schema:review """..."""
            # if game.review: # TODO: review
            #     g.add((iri, SCHEMA.review, Literal(game.review, lang='en')))
        # hpcom:list list:games-changed-life ;
        # if game.list: # TODO: review
        #     gamelists = game.list.split(';')
        #     for gamelist in gamelists:
        #         g.add((iri, SCHEMA.isPartOf, HPLIST[gamelist]))

    g.serialize('content/hobbies/games.ttl', format='ttl')
    print("RDF written")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--all', action='store_true', help="download CSV and create RDF")
    parser.add_argument('-D', '--download', action='store_true', help="download CSV from ONLINE spreadsheet")
    parser.add_argument('-C', '--create', action='store_true', help="update RDF from CSV")
    args = parser.parse_args()
    
    if args.all:
        download_csv()
        write_ttl()
    elif args.download:
        download_csv()
    elif args.create:
        write_ttl()
    else:
        raise ValueError("unknown or incorrect argument")

    