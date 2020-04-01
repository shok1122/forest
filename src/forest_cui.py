import json

import func

def read_attribute(path):
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    return attr

def count_appearance(id, analyze):
    if id in analyze:
        analyze[id]['appearance_count'] += 1
    else:
        analyze[id] = {'appearance_count':1}

def forest(keywords, count = 1000, rank = 100, year = 2019, tier = 1, output_dir = 'cache', input_dir = None):
    papers = {}
    forests = [{} for i in range(tier)]
    analyze = {}
    if input_dir is None:
        field_keyword = 'Composite(And('
        title_keyword = 'And('
        title_keyword_tmp = []
        for keyword in keywords:
            field_keyword += f"F.FN=='{keyword}',"
            title_keyword_tmp.append(
                'And(' + ','.join(list(map(lambda x: f"W=='{x}'", keyword.split()))) + ')'
            )
        title_keyword = 'Or(' + ','.join(title_keyword_tmp) + ')'
        field_keyword = field_keyword[:-1] + '))'
        title_keyword = title_keyword[:-1] + ')'
        expr = f"And(Or(Pt=='1',Pt=='3'),Y>={year},Or({title_keyword},{field_keyword}))"
        attr = read_attribute('asset/attributes')
        with open('cache/subscription.key', 'rt') as f:
            token = f.read()

        response = func.invoke_evaluate(token, expr, attr, count)
        func.parse_entities(response['entities'], papers, forests[0])

        next_list = []
        for v in forests[0].values():
            for vv in v:
                if vv not in next_list: next_list.append(vv)

        for i in range(1, tier):
            while 0 < len(next_list):
                expr = 'Or(' + ','.join(list(map(lambda x: f'Id={x}', next_list[0:100]))) + ')'
                response = func.invoke_evaluate(token, expr, attr, count)
                func.parse_entities(response['entities'], papers, forests[i])
                del next_list[0:100]
            next_list = []
            for v in forests[i].values():
                for vv in v:
                    if vv not in next_list: next_list.append(vv)

        for f in forests:
            for id in f.keys():
                count_appearance(id, analyze)
                for v in f[id]:
                    count_appearance(v, analyze)
        with open(f'{output_dir}/papers.json', 'wt') as f:
            json.dump(papers, f)
        with open(f'{output_dir}/forests.json', 'wt') as f:
            json.dump(forests, f)
        with open(f'{output_dir}/analyze.json', 'wt') as f:
            json.dump(analyze, f)
    else:
        with open(f'{input_dir}/papers.json', 'rt') as f:
            papers = json.load(f)
        with open(f'{input_dir}/forests.json', 'rt') as f:
            forests = json.load(f)
        with open(f'{input_dir}/analyze.json', 'rt') as f:
            analyze = json.load(f)
    return papers, analyze, forests

if __name__=='__main__':
    forest(['blockchain', 'cyber physical system'])