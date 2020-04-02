import json
import os
import copy

import func

g_attr = ''
master_papers = dict()

def get_papers():
    global master_papers
    return master_papers

def read_attribute(path):
    global g_attr
    if 0 == len(g_attr):
        with open(path, mode='rt') as f:
            lines = list(f)
            g_attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    return g_attr

def dump_master_papers(path_dir):
    global master_papers
    with open(f'{path_dir}/papers.json', 'wt') as f:
        json.dump(master_papers, f)

def merge_papers(papers):
    merged_id_list = []
    for id in papers:
        if id not in master_papers:
            master_papers[id] = copy.deepcopy(papers[id])
            merged_id_list.append(id)
    return merged_id_list

def load_papers(path_dir):
    global master_papers
    path = f'{path_dir}/papers.json'
    if os.path.exists(path):
        with open(path, 'rt') as f:
            master_papers = json.load(f)
    return master_papers

def fetch_papers(keyword_list, year, count, token, cache_dir):
    papers_tmp = dict()
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
    func.parse_entities(response['entities'], papers_tmp)

    merged_id_list = merge_papers(papers_tmp)
    dump_master_papers(cache_dir)

    return merged_id_list

def fetch_papers_with_id(id_list, token, cache_dir):
    papers_tmp = dict()
    
    expr = 'Or(' + ','.join(map(lambda a: 'Id='+a, id_list)) + ')'
    attr = read_attribute('asset/attributes')

    response = func.invoke_evaluate(token, expr, attr, len(id_list))
    func.parse_entities(response['entities'], papers_tmp)

    merged_id_list = merge_papers(papers_tmp)
    dump_master_papers(cache_dir)

    return merged_id_list

if __name__=='__main__':
    with open('cache/subscription.key', 'rt') as f:
        token = f.read()
    fetch_papers(['blockchain', 'cyber physical system'], 2019, 10, token, 'test')