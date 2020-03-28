import json

import func

def read_attribute(path):
    
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    
    return attr

def forest(keywords, count = 1000, rank = 100, tier = 1, output_dir = 'cache', input_dir = None):
    papers = {}
    forest = [{}] * tier
    info = {}
    if input_dir is None:
        field_keyword = 'Composite(And('
        title_keyword = 'And('
        for keyword in keywords:
            field_keyword += f"F.FN=='{keyword}',"
            for k in keyword.split(' '):
                title_keyword += f"W=='{k}',"
        field_keyword = field_keyword[:-1] + '))'
        title_keyword = title_keyword[:-1] + ')'
        expr = f'Or({title_keyword},{field_keyword})'
        attr = read_attribute('asset/attributes')
        with open('cache/subscription.key', 'rt') as f:
            token = f.read()
        for i in range(tier):
            response = func.invoke_evaluate(token, expr, attr, count)
            e = response['entities']
            func.parse_entities(e, papers, forest[i])
        for t in forest:
            for id in t.keys():
                for v in t[id]:
                    if str(v) in info:
                        info[str(v)]['count'] += 1
                    else:
                        print('new')
                        info[str(v)] = {'count':1}
        with open(f'{output_dir}/papers.json', 'wt') as f:
            json.dump(papers, f)
        with open(f'{output_dir}/forest.json', 'wt') as f:
            json.dump(forest, f)
    else:
        with open(f'{input_dir}/papers.json', 'rt') as f:
            papers = json.load(f)
        with open(f'{input_dir}/forest.json', 'rt') as f:
            forest = json.load(f)
    return papers, info

if __name__=='__main__':
    forest(['blockchain', 'cyber physical system'])