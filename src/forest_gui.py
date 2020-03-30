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
            'year':papers[k]['publication']['year'],
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
                'p_year': parent['publication']['year'],
                'p_appearance_count': parent_analyze['appearance_count'],
                'p_citation_count': parent['citation_count'],
                'id': child['id'],
                'year': child['publication']['year'],
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
        create_columns('appearance_count'),
        create_columns('citation_count'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['title'])
    data = create_data(papers, analyze)
    return columns, data, style_cell_conditional

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
            html.H1('Papers Info. (Tier0)',),
            dash_table.DataTable(
                id='papers-info-tier0',
                columns=tbl_papers_tier0_c,
                data=tbl_papers_tier0_d,
                style_cell_conditional = tbl_papers_tier0_style,
                sort_action = 'native',
                export_format ='csv'
            ),
            html.H1('Papers Info. (All)',),
            dash_table.DataTable(
                id='papers-info-all',
                columns=tbl_papers_all_c,
                data=tbl_papers_all_d,
                style_cell_conditional = tbl_papers_all_style,
                sort_action = 'native',
                export_format ='csv'
            )
        ])
    app.run_server(debug=False)
