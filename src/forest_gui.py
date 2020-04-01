import copy
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
from dash.dependencies import Input, Output, State

import forest_cui

def create_XY(data, get_Y):
    id_list = list(data.keys())
    id_list.sort()
    X = list(map(lambda a: 'id:'+a, id_list))
    Y = []
    for id in id_list:
        Y.append(get_Y(data[id]))
    return { 'X': X, 'Y': Y }

def create_bar_graph(name, X, Y):
    return {
        'data': [
            {
                'x': X,
                'y': Y,
                'type': 'bar',
                'name': name
            }
        ],
    }
        
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
            'year':papers[k]['year'],
            'publication':papers[k]['pub-name_f'],
            'citation_count':papers[k]['citation_count'],
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
        create_columns('year'),
        create_columns('publication'),
        create_columns('citation_count'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['publication','title'])
    data = create_data(papers)
    return columns, data, style_cell_conditional

def include_in(keyword, target):
    return '●' if keyword in target else ''

def generate_table_html(df, style = {}):
    return html.Table(
        # Header
        [html.Tr(
            [html.Th('')] + [html.Th(col, style=style) for col in [f"paper{i}" for i in df.columns]])
        ] +
        # Body
        [html.Tr(
            [html.Td(df.index[i])] + [html.Td(df.iloc[i][col], style=style) for col in df.columns]
        ) for i in range(len(df))]
    )

def generate_columns(df):
    return [
        {'id':v, 'name':v} for v in df.columns
    ]

def generate_table(df):
    columns =  generate_columns(df)
    data = df.to_dict('records')
    return data, columns

def generate_table_transpose(df):
    df = df.T
    columns =  generate_columns(df)
    columns.insert(0, {'id':'info','name':'info'})
    data = df.to_dict('records')
    for i in range(len(data)):
        data[i]['info'] = df.index[i]
    return data, columns

def create_paper_info(paper, exclude = []):
    retval = {}
    for k in paper:
        if k in exclude: continue
        s = ''
        if k == 'authors':
            s = ','.join(list(map(lambda x: x['name'], paper[k])))
        elif k == 'conference' and 'Unknown' != paper[k]:
            s = paper[k]['name']
        else:
            s = paper[k]
        retval[k] = s
    return retval

def forest(cache_dir):

    papers = dict()
    papers = forest_cui.load_papers(
        papers,
        cache_dir)

    keys = list(papers.keys())
    keys.sort()
    tbl_papers_all_c, tbl_papers_all_d, tbl_papers_all_style = table_papers(papers)
    # appという箱作り
    app = dash.Dash(__name__)
    # graph
    dcc.Graph()
    # appという箱に中身を詰める②
    default_table_settings = {
        'style_cell': {
            'height': 'auto',
            'whiteSpace': 'normal'
        },
        'style_table': {
            'maxHeight': '600px',
            'overflowY': 'scroll'
        },
        'sort_action': 'native',
        'export_format': 'csv'
    }
    graph_title_style = {
        'textAlign': 'center'
    }
    graph_info_style = {
        'textAlign': 'center',
        'color': 'limegreen'
    }
    app.layout = html.Div(
        children =[
            html.Div(
                html.H1('Fetch Papers')
            ),
            html.Div(children='keywords'), dcc.Input(id='fetch-paper-keywords', type='text', value=''),
            html.Div(children='year'),     dcc.Input(id='fetch-paper-year', type='text', value=''),
            html.Div(children='count'),    dcc.Input(id='fetch-paper-count', type='text', value=''),
            html.Div(children='token'),    dcc.Input(id='fetch-paper-token', type='text', value=''),
            html.Button(id='fetch-paper-button', children='Fetch'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='fetch-paper-result-table'
                )
            ),
            html.H1('Link',),
            dcc.Input(id='link-input', type='text', value='paperid'),
            html.A('Microsoft Academic', id='link-url', href = 'https://academic.microsoft.com/paper/2103863878'),
            html.H1('Abstract',),
            dcc.Input(id='abst-input', type='text', value='paperid'),
            html.Button(id='abst-button', children='Search'),
            html.Div(
                id='abst-text'
            ),
            html.H1('Keyword Search (SEP:,)',),
            dcc.Input(id='keyword-search-input', type='text', value='keyword'),
            html.Button(id='keyword-search-button', children='Search'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='keyword-search-table'
                )
            ),
            html.H1('Compare Paper Info.',),
            dcc.Input(id='input-paper-1', type='text', value='p-id-1'),
            dcc.Input(id='input-paper-2', type='text', value='p-id-2'),
            html.Button(id='compare-paper-button', n_clicks=0, children='Compare'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='compare-paper-table'
                )
            ),
            html.H1('Papers Info. (All)',),
            html.H2(
                ' | '.join([x['name'] for x in tbl_papers_all_c])
            ),
            dash_table.DataTable(
                **default_table_settings,
                id='papers-info-all',
                columns=tbl_papers_all_c,
                data=tbl_papers_all_d,
                style_cell_conditional = tbl_papers_all_style
            ),
            html.H1('Paper Info. (JSON)',),
            dcc.Input(id='paper-info-json-input', type='text', value='0'),
            html.Button(id='paper-info-json-button', n_clicks=0, children='Show'),
            html.Div(id='paper-info-json'),

            html.H1('__END__',)
        ])

    @app.callback(
        [
            Output('fetch-paper-result-table', 'data'),
            Output('fetch-paper-result-table', 'columns'),
            Output('papers-info-all', 'data')
        ],
        [
            Input('fetch-paper-button', 'n_clicks')
        ],
        [
            State('fetch-paper-keywords', 'value'),
            State('fetch-paper-year', 'value'),
            State('fetch-paper-count', 'value'),
            State('fetch-paper-token', 'value'),
        ]
    )
    def fetch_paper(n_clicks, keywords, year, count, token):
        # ignore blank keywords
        if 0 == len(keywords): return
        keyword_list = keywords.split(',')
        print(keyword_list)
        
        fetch_papers = forest_cui.fetch_papers(keyword_list, year, count, token, cache_dir)

        new_id_list = []
        new_papers = []
        for k in fetch_papers:
            if k not in papers:
                papers[k] = copy.deepcopy(fetch_papers[k])
                new_id_list.append(k)
        for id in new_id_list:
            new_papers.append(
                create_paper_info(papers[id], exclude = ['abst', 'references', 'journal-id', 'pub-name_s', 'citcon'])
            )
        df = pd.DataFrame(new_papers)
        fetch_paper_result_data, fetch_paper_result_columns = generate_table(df)
        
        _, d, _ = table_papers(papers)

        return fetch_paper_result_data, fetch_paper_result_columns, d

    @app.callback(
        [
            Output('link-url', 'children'),
            Output('link-url', 'href')
        ],
        [
            Input('link-input', 'value')
        ]
    )
    def update_link(input):
        url = f'https://academic.microsoft.com/paper/{input}'
        return url, url

    @app.callback(
        [
            Output('compare-paper-table', 'data'),
            Output('compare-paper-table', 'columns')
        ],
        [
            Input('compare-paper-button', 'n_clicks')
        ],
        [
            State('input-paper-1', 'value'),
            State('input-paper-2', 'value')
        ]
    )
    def compare_paper(n_clicks, input1, input2):
        p1 = { k: str(papers[input1][k]) for k in papers[input1] }
        p2 = { k: str(papers[input2][k]) for k in papers[input2] }
        df = pd.DataFrame({
            k : [p1[k],p2[k]] for k in p1
        })
        df = df.T
        columns =  generate_columns(df)
        columns.insert(0, {'id':'info','name':'info'})
        data = df.to_dict('records')
        for i in range(len(data)):
            data[i]['info'] = df.index[i]
        return data, columns

    @app.callback(
        Output('abst-text', 'children'),
        [ Input('abst-button', 'n_clicks') ],
        [ State('abst-input', 'value') ]
    )
    def update_abst_text(n_clicks, input):
        return papers[input]['abst'] if input in papers else "Unknown"

    @app.callback(
        [
            Output('keyword-search-table', 'data'),
            Output('keyword-search-table', 'columns')
        ],
        [
            Input('keyword-search-button', 'n_clicks')
        ],
        [
            State('keyword-search-input', 'value'),
        ]
    )
    def update_search_paper_table(n_clicks, inputs):
        result = []
        id_list = []
        for input in inputs.split(','):
            for id in papers:
                if input.lower() not in papers[id]['title'].lower(): continue
                if input.lower() not in papers[id]['abst'].lower(): continue
                if id in id_list: continue
                result.append(
                    create_paper_info(papers[id], exclude = ['abst', 'references', 'journal-id', 'pub-name_s', 'citcon'])
                )
                id_list.append(id)
        df = pd.DataFrame(result)
        data, columns = generate_table(df)
        return data, columns
    
    @app.callback(
        Output('paper-info-json', 'children'),
        [
            Input('paper-info-json-button', 'n_clicks')
        ],
        [
            State('paper-info-json-input', 'value')
        ]
    )
    def update_paper_info_json(n_clicks, paper_id):
        return html.Table(html.Pre(
            json.dumps(papers[paper_id], indent=4)
            ))

    app.run_server(debug=False)

