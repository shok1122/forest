import json

import func

def read_attribute(path):
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    return attr

def forest(keywords, count = 1000, rank = 100, year = 2019, tier = 1, output_dir = 'cache', input_dir = None):
    papers = {}
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
        func.parse_entities(response['entities'], papers)

        with open(f'{output_dir}/papers.json', 'wt') as f:
            json.dump(papers, f)
    else:
        with open(f'{input_dir}/papers.json', 'rt') as f:
            papers = json.load(f)
    return papers

if __name__=='__main__':
    forest(['blockchain', 'cyber physical system'])