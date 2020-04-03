import requests

def invoke_api(url, headers):

    response = requests.get(
        url,
        headers = headers
    )

    return response

def invoke_evaluate(token, expr, attr, count = 10, offset = 0, model = 'latest'):
    options = ''
    if expr  is not None: options += f'expr={expr}&'
    if attr  is not None: options += f'attributes={attr}&'
    options += f'model={model}&'
    options += f'count={count}&'
    options += f'offset={offset}&'
    options = options[:-1]

    url = f'https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{options}'
    headers = {
        'Content-Type' : 'application/json',
        'Ocp-Apim-Subscription-Key' : token
    }

    print(f"url: {url}")
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
    retval = [{} for i in range(l)]
    for i,a in enumerate(authors):
        r = retval[i]
        r['name'] = a['DAuN']
        r['affiliation'] = a['DAfN']
    return retval

def pub_type_name(pt):
    return ['Unknown',
        'Journal',
        'Patent',
        'Conference',
        'Book',
        'Book',
        'Book',
        'Dataset',
        'Repository'][pt]

def parse_entities(entities, papers):
    count = 0
    for e in entities:
        id = str(e['Id'])
        if id in papers:
            continue
        # papers
        p = {}
        p['abst'] = parse_abstract(e['IA']) if 'IA' in e else 'Unknown'
        p['authors'] = parse_authors(e['AA']) if 'AA' in e else 'Unknown'
        p['citation_count'] = int(e['CC']) if 'CC' in e else 'Unknown'
        p['conference'] = {'id':e['C']['CId'],'name':e['C']['CN']} if 'C' in e else 'Unknown'
        p['id'] = id if 'Id' in e else 'Unknown'
        p['journal-id'] = e['J']['JId'] if 'J' in e and 'JId' in e else 'Unknown'
        p['journal-name'] = e['J']['JN'] if 'J' in e and 'JN' in e else 'Unknown'
        p['pub-type'] = e['Pt'] if 'Pt' in e else 'Unknown'
        p['pub-name_f'] = e['VFN'] if 'VFN' in e else 'Unknown'
        p['pub-name_s'] = e['VSN'] if 'VSN' in e else 'Unknown'
        p['publisher'] = e['PB'] if 'PB' in e else 'Unknown'
        p['volume'] = int(e['V']) if 'V' in e else 'Unknown'
        p['year'] = int(e['Y']) if 'Y' in e else '1000'
        p['title'] = e['DN'] if 'DN' in e else 'Unknown'
        p['references'] = list(map(lambda x: str(x), e['RId'])) if 'RId' in e else []
        p['citcon'] = e['CitCon'] if 'CitCon' in e else 'Unknown'
        papers[id] = p
        count += 1
    return count
