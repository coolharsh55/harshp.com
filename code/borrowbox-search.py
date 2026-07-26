import csv
import datetime
from pprint import pprint
import requests

BASE_URL = "https://dublin.borrowbox.com"
SEARCH_URL = (
    "https://dublin.borrowbox.com/api/v1/search/products"
    "?offset=0&limit=60&availableOnly=false"
)
SESSION = None
books = {}


def create_session():
    session = requests.Session()

    # Get initial page to receive cookies
    session.get(
        BASE_URL,
        headers={ "User-Agent": "Mozilla/5.0" }
        )
    xsrf_token = session.cookies.get("XSRF-TOKEN")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "app-name": "ppui",
        "app-siteId": "4815",
        "app-language": "en-GB",
        "X-XSRF-TOKEN": xsrf_token,
        "Origin": BASE_URL,
    }
    return session, headers


def create_payload(author, title):
    payload = {
        "searchOperation": "CONJUNCTION",
        "searchTerm": {
            "TITLE": title,
            "GENRE": "",
            "SERIES": "",
            "AUTHOR": author,
            "NARRATOR": "",
            "ISBN": "",
        },
        "fuzzy": False,
        "filters": {
            "loanFormat": ["eBooks"]
        }
    }
    return payload


def send_request(headers,payload):
    response = session.post(
        SEARCH_URL,
        headers=headers,
        json=payload,
    )
    return response.json()


def parse_response(rawdata, title):
    if 'products' not in rawdata or len(rawdata['products']) == 0:
        return None, None, None, None
    # print(rawdata)
    data = {
        'title': rawdata['products'][0]['title'],
        'availability': rawdata['products'][0]['availability'],
        'linkid': rawdata['products'][0]['productId'],
    }
    match = title.lower() == data['title'].lower()
    status = data['availability']['status']
    if status == 'ON_LOAN':
        available = datetime.datetime.fromtimestamp(
            data['availability']['nextAvailableDate']/1000).date()
    else:
        available = 0
    link = f"https://dublin.borrowbox.com/product/{data['linkid']}/"
    return match, status, available, link


session, headers = create_session()
HUGO = {
    "ALIEN CLAY": "ADRIAN TCHAIKOVSKY",
    "SERVICE MODEL": "ADRIAN TCHAIKOVSKY",
    "THE MINISTRY OF TIME": "KALIANE BRADLEY",
    "SOMEONE YOU CAN BUILD A NEST IN": "JOHN WISWELL",
    "A SORCERESS COMES TO CALL": "T. KINGFISHER",
    "THE TAINTED CUP": "ROBERT JACKSON BENNETT",
    "SOME DESPERATE GLORY": "EMILY TESH",
    "THE ADVENTURES OF AMINA AL-SIRAFI": "SHANNON CHAKRABORTY",
    "THE SAINT OF BRIGHT DOORS": "VAJRA CHANDRASEKERA",
    "STARTER VILLAIN": "JOHN SCALZI",
    "TRANSLATION STATE": "ANN LECKIE",
    "WITCH KING": "MARTHA WELLS",
    "NETTLE & BONE": "T. KINGFISHER",
    "THE DAUGHTER OF DOCTOR MOREAU": "SILVIA MORENO-GARCIA",
    "THE KAIJU PRESERVATION SOCIETY": "JOHN SCALZI",
    "LEGENDS & LATTES": "TRAVIS BALDREE",
    "NONA THE NINTH": "TAMSYN MUIR",
    "THE SPARE MAN": "MARY ROBINETTE KOWAL",
    "A DESOLATION CALLED PEACE": "ARKADY MARTINE",
    "THE GALAXY, AND THE GROUND WITHIN": "BECKY CHAMBERS",
    "LIGHT FROM UNCOMMON STARS": "RYKA AOKI",
    "A MASTER OF DJINN": "P. DJÈLÍ CLARK",
    "PROJECT HAIL MARY": "ANDY WEIR",
    "SHE WHO BECAME THE SUN": "SHELLEY PARKER-CHAN",
    "NETWORK EFFECT": "MARTHA WELLS",
    "THE CITY WE BECAME": "N. K. JEMISIN",
    "PIRANESI": "SUSANNA CLARKE",
    "BLACK SUN": "REBECCA ROANHORSE",
    "THE RELENTLESS MOON": "MARY ROBINETTE KOWAL",
    "HARROW THE NINTH": "TAMSYN MUIR"
}
ARTHURCCLARKE = {
    "ANNIE BOT": "SIERRA GREER",
    "PRIVATE RITES": "JULIA ARMFIELD",
    "THE MINISTRY OF TIME": "KALIANE BRADLEY",
    "EXTREMOPHILE": "IAN GREEN",
    "SERVICE MODEL": "ADRIAN TCHAIKOVSKY",
    "THIRTEEN WAYS TO KILL LULABELLE ROCK": "MAUD WOOLF",
    "IN ASCENSION": "MARTIN MACINNES",
    "CHAIN-GANG ALL-STARS": "NANA KWAME ADJEI-BRENYAH",
    "THE TEN PERCENT THIEF": "LAVANYA LAKSHMINARAYAN",
    "THE MOUNTAIN IN THE SEA": "RAY NAYLER",
    "SOME DESPERATE GLORY": "EMILY TESH",
    "COREY FAH DOES SOCIAL MOBILITY": "ISABEL WAIDNER",

    "VENOMOUS LUMPSUCKER": "NED BEAUMAN",
    "THE RED SCHOLAR'S WAKE": "ALIETTE DE BODARD",
    "PLUTOSHINE": "LUCY KISSICK",
    "THE ANOMALY": "HERVÉ LE TELLIER",
    "THE CORAL BONES": "E.J. SWIFT",
    "METRONOME": "TOM WATSON",

    "DEEP WHEEL ORCADIA": "HARRY JOSEPHINE GILES",
    "KLARA AND THE SUN": "KAZUO ISHIGURO",
    "A DESOLATION CALLED PEACE": "ARKADY MARTINE",
    "A RIVER CALLED TIME": "COURTTIA NEWLAND",
    "WERGEN: THE ALIEN LOVE WAR": "MERCURIO D. RIVERA",
    "SKYWARD INN": "ALIYA WHITELEY",

    "THE ANIMALS IN THAT COUNTRY": "LAURA JEAN MCKAY",
    "THE CITY WE BECAME": "N. K. JEMISIN",
    "EDGE OF HEAVEN": "R. B. KELLY",
    "VAGABONDS": "HAO JINGFANG",
    "THE VANISHED BIRDS": "SIMON JIMENEZ",
    "THE INFINITE": "PATIENCE AGBABI"
}
NEBULA = {
    "WHEN WE WERE REAL": "DARYL GREGORY",
    "THE BUFFALO HUNTER HUNTER": "STEPHEN GRAHAM JONES",
    # "KATABASIS": "R.F. KUANG",
    "DEATH OF THE AUTHOR": "NNEDI OKORAFOR",
    "THE INCANDESCENT": "EMILY TESH",
    "SOUR CHERRY": "NATALIA THEODORIDOU",
    "WEARING THE LION": "JOHN WISWELL",

    "SOMEONE YOU CAN BUILD A NEST IN": "JOHN WISWELL",
    "THE BOOK OF LOVE": "KELLY LINK",
    "A SORCERESS COMES TO CALL": "T. KINGFISHER",
    "SLEEPING WORLDS HAVE NO MEMORY": "YAROSLAV BARSUKOV",
    "ASUNDER": "KERSTIN HALL",
    "RAKESFALL": "VAJRA CHANDRASEKERA",

    "THE SAINT OF BRIGHT DOORS": "VAJRA CHANDRASEKERA",
    "THE WATER OUTLAWS": "S.L. HUANG",
    "TRANSLATION STATE": "ANN LECKIE",
    "THE TERRAFORMERS": "ANNALEE NEWITZ",
    "SHIGIDI AND THE BRASS HEAD OF OBALUFON": "WOLE TALABI",
    "WITCH KING": "MARTHA WELLS",

    "LEGENDS & LATTES": "TRAVIS BALDREE",
    "SPEAR": "NICOLA GRIFFITH",
    "NETTLE AND BONE": "T. KINGFISHER",
    "BABEL": "R.F. KUANG",
    "NONA THE NINTH": "TAMSYN MUIR",
    "THE MOUNTAIN IN THE SEA": "RAY NAYLER",

    "THE UNBROKEN": "C.L. CLARK",
    "A MASTER OF DJINN": "P. DJÈLÍ CLARK",
    "MACHINEHOOD": "S.B. DIVYA",
    "A DESOLATION CALLED PEACE": "ARKADY MARTINE",
    "PLAGUE BIRDS": "JASON SANFORD"
}
LOCUS = {
    "THE MAN WHO SAW SECONDS": "ALEXANDER BOLDIZAR",
    "RAKESFALL": "VAJRA CHANDRASEKERA",
    "THE MERCY OF GODS": "JAMES S. A. COREY",
    "THE BEZZLE": "CORY DOCTOROW",
    "THE IMPOSITION OF UNNECESSARY OBSTACLES": "MALKA OLDER",
    "KINNING": "NISI SHAWL",
    "ALIEN CLAY": "ADRIAN TCHAIKOVSKY",
    "SERVICE MODEL": "ADRIAN TCHAIKOVSKY",
    "SPACE ODDITY": "CATHERYNNE M. VALENTE",
    "ABSOLUTION": "JEFF VANDERMEER",

    "THE JINN-BOT OF SHANTIPORT": "SAMIT BASU",
    "A FIRE BORN OF EXILE": "ALIETTE DE BODARD",
    "RED TEAM BLUES": "CORY DOCTOROW",
    "FURIOUS HEAVEN": "KATE ELLIOTT",
    "TRANSLATION STATE": "ANN LECKIE",
    "THE TERRAFORMERS": "ANNALEE NEWITZ",
    "STARTER VILLAIN": "JOHN SCALZI",
    "LORDS OF UNCREATION": "ADRIAN TCHAIKOVSKY",
    "SYSTEM COLLAPSE": "MARTHA WELLS",
    "THE ROAD TO ROSWELL": "CONNIE WILLIS",

    "A DESOLATION CALLED PEACE": "ARKADY MARTINE",
    "LIGHT FROM UNCOMMON STARS": "RYKA AOKI",
    "SHARDS OF EARTH": "ADRIAN TCHAIKOVSKY",
    "PROJECT HAIL MARY": "ANDY WEIR",
    "THE GALAXY, AND THE GROUND WITHIN": "BECKY CHAMBERS",
    "MACHINEHOOD": "S.B. DIVYA",
    "KLARA AND THE SUN": "KAZUO ISHIGURO",
    "LEVIATHAN FALLS": "JAMES S. A. COREY",
    "TERMINATION SHOCK": "NEAL STEPHENSON",
    "A PSALM FOR THE WILD-BUILT": "BECKY CHAMBERS",

    "NETWORK EFFECT": "MARTHA WELLS",
    "PIRANESI": "SUSANNA CLARKE",
    "THE CITY WE BECAME": "N. K. JEMISIN",
    "THE RELENTLESS MOON": "MARY ROBINETTE KOWAL",
    "HARROW THE NINTH": "TAMSYN MUIR",
    "THE LAST EMPEROX": "JOHN SCALZI",
    "THE DOORS OF EDEN": "ADRIAN TCHAIKOVSKY",
    "BLACK SUN": "REBECCA ROANHORSE",
    "AXIOM'S END": "LINDSAY ELLIS",
    "THE VANISHED BIRDS": "SIMON JIMENEZ",

    "THE SPACE BETWEEN WORLDS": "MICAIAH JOHNSON",
    "THE MINISTRY FOR THE FUTURE": "KIM STANLEY ROBINSON",
    "MEXICAN GOTHIC": "SILVIA MORENO-GARCIA",
    "THE ONCE AND FUTURE WITCHES": "ALIX E. HARROW",
    "BLACK SUN": "REBECCA ROANHORSE",
    "PIRANESI": "SUSANNA CLARKE",
    "THE INVISIBLE LIFE OF ADDIE LARUE": "V.E. SCHWAB",
    "NETWORK EFFECT": "MARTHA WELLS",
    "THE CITY WE BECAME": "N. K. JEMISIN",
    "THE DOORS OF EDEN": "ADRIAN TCHAIKOVSKY"
}
books.update(HUGO)
books.update(ARTHURCCLARKE)
books.update(NEBULA)
books.update(LOCUS)

from rdflib import Graph
graph = Graph()
graph.parse('content/hobbies/books.ttl', format='turtle')
bookstoread = graph.query('''
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
    }
    ''')
booksread = graph.query('''
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
        ?iri hpcom:book_status hpcom:book-read .
    }
    ''')
booksread = [(str(name).upper(), str(author).upper()) for name, author in booksread]
print(f"{len(booksread)} books already read from my list")
print(f"{len(books)} books to read from awards list")
for name, author in booksread:
    # print(f"{name=} {author=}")
    if name in books:
        # print(f"Duplicate: {name=} {author=}")
        del books[name]
print(f"{len(books)} books to read after removing already read books")
bookstoread = [(str(name).upper(), str(author).upper()) for name, author in bookstoread]
print(f"{len(bookstoread)} books unread that I do not own from my list")
for name, author in bookstoread:
    if name not in books:
        books[name] = author
    # else:
    #     print(f"Duplicate: {name=} {author=}")
print(f"{len(books)} books to read after adding unread books")

print('*' * 24)
print('Searching Dublin Library...')
print('*' * 24)
# pprint(books)
for title, author in books.items():
    # print(f"{title=} {author=}")
    response = send_request(headers, create_payload(author, title))
    match, status, available, link = parse_response(response, title)
    if status == 'ON_LOAN':
        status = '[R]' # reserve
    else:
        status = '[A]' # available
    if match:
        print(f"{status} :: {title} :: {author} :: {available} :: {link}")
    # else:
        # print(f"{title} - {author} :: no match")
