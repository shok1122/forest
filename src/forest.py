import func

def read_attribute(path):
    
    with open(path, mode='rt') as f:
        lines = list(f)
        attr = ','.join(list(map(lambda x: x.rstrip(), lines)))
    
    return attr

def forest(keyword, count = 1000, rank = 100, tier = 1, input_dir = ""):

    field_keyword = 'Composite(And('
    title_keyword = 'And('

    for kw in keyword:
        field_keyword += f"F.FN=='{kw}',"
        for k in kw.split(' '):
            title_keyword += f"W=='{k}',"
    
    field_keyword = field_keyword[:-1] + ')'
    title_keyword = title_keyword[:-1] + ')'

    expr = f'Or({title_keyword},{field_keyword})'

    attr = read_attribute('asset/attributes')

    with open('cache/subscription.key', 'rt') as f:
        token = f.read()

    func.invoke(token, expr, attr, count)

if __name__=='__main__':
    func.print_str('Hello')
    forest(['blockchain'])