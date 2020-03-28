import requests

class Author:
    def __init__(self):
        self.name = ''
        self.affiliation = ''

class Conference:
    def __init__(self):
        self.id = -1
        self.name = ''

class Journal:
    def __init__(self):
        self.id = -1
        self.name = ''

class Publication:
    def __init__(self):
        self.type = ''
        self.name_f = ''
        self.name_s = ''
        self.publisher = ''
        self.volume = -1
        self.year = -1

class Paper:
    def __init__(self):
        self.tier = -1
        self.title = ''
        self.id = -1
        self.authors = []
        self.citation_count = -1
        self.abstract = ''
        self.conference = Conference()
        self.journal = Journal()
        self.publication = Publication()
        self.references = []

class Branch:
    def __init__(self):
        self.id = -1
        self.branches = []

class Tree:
    def __init__(self):
        self.id = -1
        self.branches = []

def invoke_api(url, headers):

    response = requests.get(
        url,
        headers = headers
    )

    return response

def invoke_evaluate(token, expr, attr, count = 10, model = 'latest'):

    options = ''
    if expr  is not None: options += f'expr={expr}&'
    if model is not None: options += f'model={model}&'
    if count is not None: options += f'count={count}&'
    if attr  is not None: options += f'attributes={attr}&'
    options = options[:-1]

    url = f'https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{options}'
    headers = {
        'Content-Type' : 'application/json',
        'Ocp-Apim-Subscription-Key' : token
    }

    response = invoke_api(url, headers)

    return response.json()

def parse_abstract(info):

    l = info['IndexLength']
    abst = [''] * l

    tmp = info['InvertedIndex']
    for k in tmp:
        for v in tmp[k]:
            abst[v] = k
    
    return ' '.join(abst)

def parse_authors(authors):

    l = len(authors)
    retval = [Author()] * l
    for a in authors:
        r = retval[int(a['S']) - 1]
        r.name = a['DAuN']
        r.affiliation = a['DAfN']
    return retval

def publication_type(pt):
    return ['Unknown',
        'Journal',
        'Patent',
        'Conference',
        'Book',
        'Book',
        'Book',
        'Dataset',
        'Repository'][pt]

def parse_publication(e, publication):
    if 'Pt'  in e: publication.type = e['Pt']
    if 'VFN' in e: publication.name_f = e['VFN']
    if 'VSN' in e: publication.name_f = e['VSN']
    if 'PB'  in e: publication.publisher = e['PB']
    if 'V'   in e: publication.volume = e['V']
    if 'Y'   in e: publication.year = e['Y']

def parse_entities(entities, papers, forest):
    for e in entities:
        p = Paper()
        if 'IA' in e: p.abstract = parse_abstract(e['IA'])
        if 'AA' in e: p.authors = parse_authors(e['AA'])
        if 'CC' in e: p.citation_count = e['CC']
        if 'C'  in e:
            p.conference.id   = e['C']['CId']
            p.conference.name = e['C']['CN']
        if 'Id' in e: p.id = e['Id']
        if 'J'  in e:
            p.journal.id   = e['J']['JId']
            p.journal.name = e['J']['JN']
        parse_publication(e, p.publication)
        if 'DN'  in e: p.title = e['DN']
        if 'RId' in e: p.references = e['RId']
        papers[e['Id']] = p

