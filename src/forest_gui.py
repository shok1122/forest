import dash  
import dash_table
import dash_core_components as dcc 
import dash_html_components as html  

import forest_cui

def figure_citation_count(papers, keys):
    X = [0] * len(keys)
    Y = []
    for x in keys:
        Y.append(str(papers[x]['citation_count']))
    for i in range(len(keys)):
        X[i] = 'id:' + keys[i]
    fig = {
        'data': [
            {
                'x': X,
                'y': Y,
                'type': 'bar',
                'name': 'paper id'
            }
        ],
        'layout': {
            'title': 'citation count'
        }
    }
    return fig

def figure_reference_count(papers, keys):
    X = [0] * len(keys)
    Y = []
    for x in keys:
        Y.append(len(papers[x]['references']))
    for i in range(len(keys)):
        X[i] = 'id:' + keys[i]
    fig = {
        'data': [
            {
                'x': X,
                'y': Y,
                'type': 'bar',
                'name': 'paper id'
            }
        ],
        'layout': {
            'title': 'reference count'
        }
    }
    return fig

def figure_match_count(analyze, keys):
    X = [0] * len(keys)
    Y = []
    for x in keys:
        if str(x) in analyze:
            Y.append(analyze[str(x)]['count'])
    for i in range(len(keys)):
        X[i] = 'id:' + keys[i]
    fig = {
        'data': [
            {
                'x': X,
                'y': Y,
                'type': 'bar',
                'name': 'paper id'
            }
        ],
        'layout': {
            'title': 'match count'
        }
    }
    return fig

def create_columns(name):
    columns = {
        'id':name,
        'name':name
    }
    return columns

def create_style_cell_conditional(name_columns):
    return [
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in name_columns
    ]

def create_data(papers):
    data = [
        {
            'id':papers[k]['id'],
            'title':papers[k]['title']
        } for k in papers
    ]
    data.sort(key = lambda x: x['id'])
    for i,v in enumerate(data):
        v['index'] = i
    return data

def table_papers(papers):
    columns = [
        create_columns('index'),
        create_columns('id'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['title'])
    data = create_data(papers)
    return columns, data, style_cell_conditional

def forest(keywords, count = 1000, rank = 100, tier = 1, output_dir = 'cache', input_dir = None):
    papers, analyze = forest_cui.forest(keywords, count, rank, tier, output_dir, input_dir)
    keys = list(papers.keys())
    keys.sort()
    fig_cit_cnt = figure_citation_count(papers, keys)
    fig_ref_cnt = figure_reference_count(papers, keys)
    fig_disp_cnt = figure_match_count(analyze, keys)
    tbl_papers_c, tbl_papers_d, style_cell_conditional = table_papers(papers)
    # appという箱作り
    app = dash.Dash(__name__)
    # graph
    dcc.Graph()
    # appという箱に中身を詰める②
    app.layout = html.Div(
        children =[
            html.H1('Hello Dash',),
            dcc.Graph(
                id = 'citation count',
                figure = fig_cit_cnt
            ),
            dcc.Graph(
                id = 'reference count',
                figure = fig_ref_cnt
            ),
            dcc.Graph(
                id = 'match count',
                figure = fig_disp_cnt
            ),
            html.H1('AAA',),
            dash_table.DataTable(
                id='table-editing-simple',
                columns=tbl_papers_c,
                data=tbl_papers_d,
                style_cell_conditional = style_cell_conditional
            )
        ])
    app.run_server(debug=False)
