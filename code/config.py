import logging
logging.basicConfig(
    level=logging.INFO, format='%(levelname)s - %(funcName)s :: %(lineno)d - %(message)s')
DEBUG = logging.debug
INFO = logging.info
# logging.disable(logging.DEBUG)

FLAG_VALIDATE_CONSTRAINTS = True
LOCAL_PATH = '../'  # path where generated data will be stored

CONTENT = {
    'site': {
        'iripath': 'https://harshp.com/me',
        'files': [
            'vocab.ttl',
            'views.ttl',
            'content/site.ttl',
        ]
    },
    'me': {
        'iripath': 'https://harshp.com/me',
        'files': [
            '../me.ttl'
        ]
    },
    'tags': { 
        'iripath': 'https://harshp.com/tags',
        'files': [ 'content/tags.ttl' ]
    },
    'blog': { 
        'iripath': 'https://harshp.com/blog',
        'files': [ 'content/blog/blog.ttl' ] 
    },
    'poems': { 
        'iripath': 'https://harshp.com/poems',
        'files': [ 'content/poems/poems.ttl' ] },
    'stories': { 
        'iripath': 'https://harshp.com/stories',
        'files': [ 'content/stories/stories.ttl' ] },
    'dev': { 
        'iripath': 'https://harshp.com/dev',
        'files': [ 'content/dev/dev.ttl' ] },
    'research': { 
        'iripath': 'https://harshp.com/research',
        'files': [ 
            'content/research/blog/research_blog.ttl',
            'content/research/research.ttl',
            'content/research/publications/publications.ttl',
            'content/research/publications/drafts/drafts.ttl',
            'content/research/presentations/presentations.ttl',
            'content/research/publications/authors.ttl',
            'content/research/publications/venues.ttl',
            'content/research/supervision/supervision.ttl',
            'content/research/projects/phd/phd.ttl',
            'content/research/projects/protect/protect.ttl',
            'content/research/projects/risky/risky.ttl',
            'content/research/projects/paecg/paecg.ttl',
            'content/research/projects/cost-dkg-stsm/cost-dkg-stsm.ttl',
            'content/research/projects/hsbooster/hsbooster.ttl',
            'content/research/projects/standict26/standict26.ttl',
            'content/research/projects/adra-e/adra-e.ttl',
            'content/research/projects/edu4standards/edu4standards.ttl',
            'content/research/projects/hse-dpia/hse-dpia.ttl',
            'content/research/projects/empower-fidelity/empower-fidelity.ttl',
            'content/research/projects/harness/harness.ttl',
            'content/research/projects/recitals/recitals.ttl',
            'content/research/projects/aisi-companions/aisi-companions.ttl',
            # 'content/research/funding-proposals.ttl'
        ]
    },
    'hobbies': {
        'iripath': 'https://harshp.com/hobbies',
        'files': [
            'content/hobbies/books.ttl',
            'content/hobbies/book_lists.ttl',
            'content/hobbies/games.ttl',
            'content/hobbies/tea.ttl'
        ]
    }
}