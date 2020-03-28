import json
from argparse import ArgumentParser

import func

def read_attribute(path):
    
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    
    return attr

def forest(keywords, count = 1000, rank = 100, tier = 1, output_dir = 'cache', input_dir = None):
    papers = {}
    forest = [{}] * tier
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
        with open(f'{output_dir}/papers.json', 'wt') as f:
            json.dump(papers, f)
        with open(f'{output_dir}/forest.json', 'wt') as f:
            json.dump(forest, f)
    else:
        with open(f'{input_dir}/papers.json', 'rt') as f:
            papers = f.read()
        with open(f'{input_dir}/forest.json', 'rt') as f:
            forest = f.read()

if __name__=='__main__':
    parser = ArgumentParser(
        prog = 'forest',
        usage = 'usage',
        description = 'description',
        add_help = True)
    parser.add_argument(
        '--output-dir',
        required = False,
        default = 'cache',
        help = 'output dir')
    parser.add_argument(
        '--input-dir',
        required = False,
        help = 'input dir')
    parser.add_argument(
        '-k', '--keywords',
        required = True,
        nargs = '*',
        help = 'keyword')
    parser.add_argument(
        '-c', '--count',
        default = 1000,
        type = int,
        help = 'count')
    parser.add_argument(
        '-r', '--rank',
        default = 100,
        type = int,
        help = 'rank')
    parser.add_argument(
        '-t', '--tier',
        default = 1,
        type = int,
        help = 'tier')
    args = parser.parse_args()
    forest(args.keywords, args.count, args.rank, args.tier, args.output_dir, args.input_dir)