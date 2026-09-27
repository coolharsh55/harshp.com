import csv
from collections import namedtuple

import sys
if sys.platform == 'linux':
    FILEPATH = '/home/harsh/GoogleDrive/RESEARCH/media/media-mentions.csv'
elif sys.platform == 'darwin':
    FILEPATH = '/Users/harsh/GoogleDrive/RESEARCH/media/media-mentions.csv'
else:
    raise Exception(f'Unsupported {sys.platform=}')

Entry = namedtuple('Entry',
    ('date', 'venue', 'link', 'title', 'byline', 'type', 'comment'))

with open(FILEPATH) as fd:
    reader = csv.reader(fd)
    next(reader)
    data = reversed([
        Entry(*(value.strip() for value in row))
            for row in reader
    ])

# print(data)

TEMPLATE = '''<li>
    <a href="{x.link}">{x.venue} - {x.title} ({x.date})</a><br/>
    <small><i>{x.comment}</i></small>
</li>'''

for x in data:
    # print(x.title)
    print(TEMPLATE.format(x=x))