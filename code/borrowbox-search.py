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


def load_books():
    books = {}
    with open('content/hobbies/bookstoread.csv', 'r') as fd:
        reader = csv.reader(fd)
        for row in reader:
            books[row[0]] = row[1]
    return books


if __name__ == '__main__':
    session, headers = create_session()
    books = load_books()
    hugo = {
        "Alien Clay": "Adrian Tchaikovsky",
        "Service Model": "Adrian Tchaikovsky",
        "The Ministry of Time": "Kaliane Bradley",
        "Someone You Can Build a Nest In": "John Wiswell",
        "A Sorceress Comes to Call": "T. Kingfisher",
        "The Tainted Cup": "Robert Jackson Bennett",
        "Some Desperate Glory": "Emily Tesh",
        "The Adventures of Amina al-Sirafi": "Shannon Chakraborty",
        "The Saint of Bright Doors": "Vajra Chandrasekera",
        "Starter Villain": "John Scalzi",
        "Translation State": "Ann Leckie",
        "Witch King": "Martha Wells",
        "Nettle & Bone": "T. Kingfisher",
        "The Daughter of Doctor Moreau": "Silvia Moreno-Garcia",
        "The Kaiju Preservation Society": "John Scalzi",
        "Legends & Lattes": "Travis Baldree",
        "Nona the Ninth": "Tamsyn Muir",
        "The Spare Man": "Mary Robinette Kowal",
        "A Desolation Called Peace": "Arkady Martine",
        "The Galaxy, and the Ground Within": "Becky Chambers",
        "Light From Uncommon Stars": "Ryka Aoki",
        "A Master of Djinn": "P. Djèlí Clark",
        "Project Hail Mary": "Andy Weir",
        "She Who Became the Sun": "Shelley Parker-Chan",
        "Network Effect": "Martha Wells",
        "The City We Became": "N. K. Jemisin",
        "Piranesi": "Susanna Clarke",
        "Black Sun": "Rebecca Roanhorse",
        "The Relentless Moon": "Mary Robinette Kowal",
        "Harrow the Ninth": "Tamsyn Muir"
    }
    arthurcclarke = {
        "Annie Bot": "Sierra Greer",
        "Private Rites": "Julia Armfield",
        "The Ministry of Time": "Kaliane Bradley",
        "Extremophile": "Ian Green",
        "Service Model": "Adrian Tchaikovsky",
        "Thirteen Ways to Kill Lulabelle Rock": "Maud Woolf",

        "In Ascension": "Martin MacInnes",
        "Chain-Gang All-Stars": "Nana Kwame Adjei-Brenyah",
        "The Ten Percent Thief": "Lavanya Lakshminarayan",
        "The Mountain in the Sea": "Ray Nayler",
        "Some Desperate Glory": "Emily Tesh",
        "Corey Fah Does Social Mobility": "Isabel Waidner",

        "Venomous Lumpsucker": "Ned Beauman",
        "The Red Scholar's Wake": "Aliette de Bodard",
        "Plutoshine": "Lucy Kissick",
        "The Anomaly": "Hervé Le Tellier",
        "The Coral Bones": "E.J. Swift",
        "Metronome": "Tom Watson",

        "Deep Wheel Orcadia": "Harry Josephine Giles",
        "Klara and the Sun": "Kazuo Ishiguro",
        "A Desolation Called Peace": "Arkady Martine",
        "A River Called Time": "Courttia Newland",
        "Wergen: The Alien Love War": "Mercurio D. Rivera",
        "Skyward Inn": "Aliya Whiteley",

        "The Animals in That Country": "Laura Jean McKay",
        "The City We Became": "N. K. Jemisin",
        "Edge of Heaven": "R. B. Kelly",
        "Vagabonds": "Hao Jingfang",
        "The Vanished Birds": "Simon Jimenez",
        "The Infinite": "Patience Agbabi"
    }
    nebula = {
        "When We Were Real": "Daryl Gregory",
        "The Buffalo Hunter Hunter": "Stephen Graham Jones",
        "Katabasis": "R.F. Kuang",
        "Death of the Author": "Nnedi Okorafor",
        "The Incandescent": "Emily Tesh",
        "Sour Cherry": "Natalia Theodoridou",
        "Wearing the Lion": "John Wiswell",

        "Someone You Can Build a Nest In": "John Wiswell",
        "The Book of Love": "Kelly Link",
        "A Sorceress Comes to Call": "T. Kingfisher",
        "Sleeping Worlds Have No Memory": "Yaroslav Barsukov",
        "Asunder": "Kerstin Hall",
        "Rakesfall": "Vajra Chandrasekera",

        "The Saint of Bright Doors": "Vajra Chandrasekera",
        "The Water Outlaws": "S.L. Huang",
        "Translation State": "Ann Leckie",
        "The Terraformers": "Annalee Newitz",
        "Shigidi and the Brass Head of Obalufon": "Wole Talabi",
        "Witch King": "Martha Wells",

        "Legends & Lattes": "Travis Baldree",
        "Spear": "Nicola Griffith",
        "Nettle and Bone": "T. Kingfisher",
        "Babel": "R.F. Kuang",
        "Nona the Ninth": "Tamsyn Muir",
        "The Mountain in the Sea": "Ray Nayler",

        "The Unbroken": "C.L. Clark",
        "A Master of Djinn": "P. Djèlí Clark",
        "Machinehood": "S.B. Divya",
        "A Desolation Called Peace": "Arkady Martine",
        "Plague Birds": "Jason Sanford"
    }
    locus = {
        "The Man Who Saw Seconds": "Alexander Boldizar",
        "Rakesfall": "Vajra Chandrasekera",
        "The Mercy of Gods": "James S. A. Corey",
        "The Bezzle": "Cory Doctorow",
        "The Imposition of Unnecessary Obstacles": "Malka Older",
        "Kinning": "Nisi Shawl",
        "Alien Clay": "Adrian Tchaikovsky",
        "Service Model": "Adrian Tchaikovsky",
        "Space Oddity": "Catherynne M. Valente",
        "Absolution": "Jeff VanderMeer",

        "The Jinn-Bot of Shantiport": "Samit Basu",
        "A Fire Born of Exile": "Aliette de Bodard",
        "Red Team Blues": "Cory Doctorow",
        "Furious Heaven": "Kate Elliott",
        "Translation State": "Ann Leckie",
        "The Terraformers": "Annalee Newitz",
        "Starter Villain": "John Scalzi",
        "Lords of Uncreation": "Adrian Tchaikovsky",
        "System Collapse": "Martha Wells",
        "The Road to Roswell": "Connie Willis",

        "A Desolation Called Peace": "Arkady Martine",
        "Light From Uncommon Stars": "Ryka Aoki",
        "Shards of Earth": "Adrian Tchaikovsky",
        "Project Hail Mary": "Andy Weir",
        "The Galaxy, and the Ground Within": "Becky Chambers",
        "Machinehood": "S.B. Divya",
        "Klara and the Sun": "Kazuo Ishiguro",
        "Leviathan Falls": "James S. A. Corey",
        "Termination Shock": "Neal Stephenson",
        "A Psalm for the Wild-Built": "Becky Chambers",

        "Network Effect": "Martha Wells",
        "Piranesi": "Susanna Clarke",
        "The City We Became": "N. K. Jemisin",
        "The Relentless Moon": "Mary Robinette Kowal",
        "Harrow the Ninth": "Tamsyn Muir",
        "The Last Emperox": "John Scalzi",
        "The Doors of Eden": "Adrian Tchaikovsky",
        "Black Sun": "Rebecca Roanhorse",
        "Axiom's End": "Lindsay Ellis",
        "The Vanished Birds": "Simon Jimenez",

        "The Space Between Worlds": "Micaiah Johnson",
        "The Ministry for the Future": "Kim Stanley Robinson",
        "Mexican Gothic": "Silvia Moreno-Garcia",
        "The Once and Future Witches": "Alix E. Harrow",
        "Black Sun": "Rebecca Roanhorse",
        "Piranesi": "Susanna Clarke",
        "The Invisible Life of Addie LaRue": "V.E. Schwab",
        "Network Effect": "Martha Wells",
        "The City We Became": "N. K. Jemisin",
        "The Doors of Eden": "Adrian Tchaikovsky"
    }
    books.update(hugo)
    books.update(arthurcclarke)
    books.update(nebula)
    books.update(locus)
    # pprint(books)
    for title, author in books.items():
        response = send_request(headers, create_payload(author, title))
        match, status, available, link = parse_response(response, title)
        if match:
            print(f"{title} - {author} :: {match} {status} {available} {link}")
        # else:
            # print(f"{title} - {author} :: no match")
