import json
import os

import func

def read_attribute(path):
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    return attr

def dump_papers(papers, path_dir):
    with open(f'{path_dir}/papers.json', 'wt') as f:
        json.dump(papers, f)

def load_papers(papers, path_dir):
    path = f'{path_dir}/papers.json'
    if os.path.exists(path):
        with open(path, 'rt') as f:
            papers = json.load(f)
    return papers

def fetch_papers(keyword_list, year, count, token, cache_dir):
    papers = dict()
    field_keyword = 'Composite(And('
    title_keyword = 'And('
    title_keyword_tmp = []
    for keyword in keyword_list:
        field_keyword += f"F.FN=='{keyword}',"
        title_keyword_tmp.append(
            'And(' + ','.join(list(map(lambda x: f"W=='{x}'", keyword.split()))) + ')'
        )
    title_keyword = 'Or(' + ','.join(title_keyword_tmp) + ')'
    field_keyword = field_keyword[:-1] + '))'
    title_keyword = title_keyword[:-1] + ')'
    expr = f"And(Or(Pt=='1',Pt=='3'),Y>={year},Or({title_keyword},{field_keyword}))"
    attr = read_attribute('asset/attributes')

    response = func.invoke_evaluate(token, expr, attr, count)
    func.parse_entities(response['entities'], papers)

    dump_papers(papers, cache_dir)

    return papers

if __name__=='__main__':
    with open('cache/subscription.key', 'rt') as f:
        token = f.read()
    fetch_papers(['blockchain', 'cyber physical system'], 2019, 10, token, 'test')