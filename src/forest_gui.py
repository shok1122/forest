import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
from dash.dependencies import Input, Output, State

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

def figure_appearance_count(analyze, keys):
    X = [0] * len(keys)
    Y = []
    for x in keys:
        if x in analyze:
            Y.append(analyze[x]['appearance_count'])
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
            'title': 'appearance count'
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

def create_data(papers, analyze):
    data = [
        {
            'id':papers[k]['id'],
            'year':papers[k]['year'],
            'publication':papers[k]['pub-name_f'],
            'appearance_count':analyze[k]['appearance_count'],
            'citation_count':papers[k]['citation_count'],
            'title':papers[k]['title']
        } for k in papers
    ]
    data.sort(key = lambda x: x['id'])
    for i,v in enumerate(data):
        v['index'] = i
    return data

def create_data_forest(papers, analyze, forest):
    data = []
    for parent_id in forest:
        parent = papers[parent_id]
        parent_analyze = analyze[parent_id]
        for child_id in forest[parent_id]:
            child = papers[child_id]
            child_analyze = analyze[child_id]
            data.append({
                'parent': parent['id'],
                'p_title': parent['title'],
                'p_year': parent['year'],
                'p_appearance_count': parent_analyze['appearance_count'],
                'p_citation_count': parent['citation_count'],
                'id': child['id'],
                'year': child['year'],
                'appearance_count': child_analyze['appearance_count'],
                'citation_count': child['citation_count'],
                'title': child['title']
            })
    data.sort(key = lambda x: x['parent'])
    for i,v in enumerate(data):
        v['index'] = i
    return data

def table_forest(papers, analyze, forest):
    columns = [
        create_columns('index'),
        create_columns('parent'),
        create_columns('p_title'),
        create_columns('p_year'),
        create_columns('p_appearance_count'),
        create_columns('p_citation_count'),
        create_columns('id'),
        create_columns('year'),
        create_columns('appearance_count'),
        create_columns('citation_count'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['p_title','title'])
    data = create_data_forest(papers, analyze, forest)
    return columns, data, style_cell_conditional

def table_papers(papers, analyze):
    columns = [
        create_columns('index'),
        create_columns('id'),
        create_columns('year'),
        create_columns('publication'),
        create_columns('appearance_count'),
        create_columns('citation_count'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['publication','title'])
    data = create_data(papers, analyze)
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

def paper_to_str(paper, exclude = []):
    retval = {}
    for k in paper:
        if k in exclude: continue
        s = ''
        if k == 'authors':
            s = ','.join(list(map(lambda x: x['name'], paper[k])))
        elif k == 'conference' and 'Unknown' != paper[k]:
            s = paper[k]['name']
        else:
            s = str(paper[k])
        retval[k] = s
    return retval

def forest(keywords, count = 1000, rank = 100, year = 2019, tier = 1, output_dir = 'cache', input_dir = None):
    papers, analyze, forests = forest_cui.forest(
        keywords,
        count = count,
        rank = rank,
        year = year,
        tier = tier,
        output_dir = output_dir,
        input_dir = input_dir)
    keys = list(papers.keys())
    keys.sort()
    fig_cit_cnt = figure_citation_count(papers, keys)
    fig_ref_cnt = figure_reference_count(papers, keys)
    fig_appearance_cnt = figure_appearance_count(analyze, keys)
    tbl_papers_tier0_c, tbl_papers_tier0_d, tbl_papers_tier0_style = table_forest(papers, analyze, forests[0])
    tbl_papers_all_c, tbl_papers_all_d, tbl_papers_all_style = table_papers(papers, analyze)
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
                id = 'appearance count',
                figure = fig_appearance_cnt
            ),
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
                    id='keyword-search-table',
                    style_cell={
                        'height': 'auto',
                        'minWidth': '0px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                    },
                    sort_action = 'native',
                    export_format ='csv'
                )
            ),
            html.H1('Compare Paper Info.',),
            dcc.Input(id='input-paper-1', type='text', value='p-id-1'),
            dcc.Input(id='input-paper-2', type='text', value='p-id-2'),
            html.Button(id='compare-paper-button', n_clicks=0, children='Compare'),
            html.Div(
                dash_table.DataTable(
                    id='compare-paper-table',
                    style_cell={
                        'height': 'auto',
                        'minWidth': '0px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                    }
                )
            ),
            html.H1('Papers Info. (Tier0)',),
            dash_table.DataTable(
                id='papers-info-tier0',
                columns=tbl_papers_tier0_c,
                data=tbl_papers_tier0_d,
                style_cell_conditional = tbl_papers_tier0_style,
                sort_action = 'native',
                export_format ='csv',
                virtualization = True
            ),
            html.H1('Papers Info. (All)',),
            html.H2(
                ' | '.join([x['name'] for x in tbl_papers_all_c])
            ),
            dash_table.DataTable(
                id='papers-info-all',
                columns=tbl_papers_all_c,
                data=tbl_papers_all_d,
                style_cell_conditional = tbl_papers_all_style,
                sort_action = 'native',
                export_format ='csv',
                virtualization = True
            ),
            html.H1('Paper Info. (JSON)',),
            dcc.Input(id='paper-info-json-input', type='text', value='0'),
            html.Button(id='paper-info-json-button', n_clicks=0, children='Show'),
            html.Div(id='paper-info-json'),

            html.H1('__END__',)
        ])

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
            print(input)
            for id in papers:
                if input.lower() not in papers[id]['title'].lower(): continue
                if input.lower() not in papers[id]['abst'].lower(): continue
                if id in id_list: continue
                result.append(
                    paper_to_str(papers[id], exclude=['abst', 'references', 'journal-id', 'pub-name_s', 'citcon'])
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

