import copy
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import networkx as nx
import json
import pandas as pd
from dash.dependencies import Input, Output, State

import forest_core
import func

COLOR_VALUE = 0
COLOR_VALUE_MAX = 100

COLOR_LIST = [
    "slateblue", "steelblue", "royalblue", "blue", "deepskyblue", "cyan",
    "lightseagreen", "limegreen", "yellowgreen", "gold", "darkorange",
    "sandybrown", "red", "hotpink", "darkviolet", "forestgreen", "mediumvioletred",
    "dimgray", "black"
]

#G = nx.DiGraph()
Figure = go.Figure(
    layout = go.Layout(
        title = 'Papers network',
        titlefont_size = 16,
        height = 800,
        showlegend = False,
        hovermode = 'closest',
        margin = dict(b=20, l=5, r=5, t=40),
        clickmode = 'event+select'
    )
)


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
            'id':str(papers[k]['id']) if 'id' in papers[k] else 'Unknown',
            'year':papers[k]['year'] if 'year' in papers[k] else 'Unknown',
            'type': func.pub_type_name(int(papers[k]['pub-type'])) if 'pub-type' in papers[k] else 'Unknown',
            'publication':papers[k]['pub-name_f'] if 'pub-name_f' in papers[k] else 'Unknown',
            'citation_count':papers[k]['citation_count'] if 'citation_count' in papers[k] else 'Unknown',
            'title':papers[k]['title'] if 'title' in papers[k] else 'Unknown',
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
        create_columns('type'),
        create_columns('publication'),
        create_columns('citation_count'),
        create_columns('title')
    ]
    style_cell_conditional = create_style_cell_conditional(['publication','title'])
    data = create_data(papers)
    return columns, data, style_cell_conditional

def generate_columns(df):
    return [
        {'id':v, 'name':v} for v in df.columns
    ]

def generate_table(df):
    columns =  generate_columns(df)
    data = df.to_dict('records')
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

def get_color():
    global COLOR_VALUE
    color = COLOR_LIST[COLOR_VALUE]
    COLOR_VALUE += 1
    if len(COLOR_LIST) <= COLOR_VALUE:
        COLOR_VALUE = 0
    return color

def create_papers_network(paper_list):
    G = nx.DiGraph()
    global Figure
    # add references as edge
    if 0 < len(paper_list):
        for id in paper_list:
            G.add_node(id)
            if 'references' not in paper_list[id]:
                continue
            for ref in paper_list[id]['references']:
                G.add_edge(id, ref)
                #list_edge.append((id, ref))
    #else:
    #    G = nx.DiGraph()
    
    pos = nx.spring_layout(G)
    for n in G.nodes:
        G.nodes[n]['pos'] = copy.deepcopy(pos[n])

    color = get_color()

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    edge_trace = go.Scatter(
        x = edge_x, y = edge_y,
        line = dict(width = 0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    paper_id = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        paper_id.append(node)
    node_trace = go.Scatter(
        x = node_x, y = node_y,
        mode = 'markers',
        hoverinfo='text',
        marker = dict(
            # showscale = True,
            colorscale = 'mygbm',
            reversescale = True,
            color = [],
            size = 10
        ),
        customdata = paper_id,
        line_width = 2
    )

    color = 0
    for node, adjacencies in enumerate(G.adjacency()):
        if 0 < len(adjacencies[1]):
            color = get_color()
        node_trace['marker']['color'] += tuple([color])

    Figure.add_traces(
        data = [edge_trace, node_trace]
    )

    return Figure

def forest(cache_dir):

    papers = forest_core.load_papers(cache_dir)

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
    app.layout = html.Div(
        children =[
            html.Div(html.H1('Token')),
            html.Div(children='token'), dcc.Input(id='fetch-paper-token', type='text', value=''),
            html.Div(
                [
                    html.H1('Fetch Papers'),
                    html.Div(id='fetch-paper-error', style = {'color':'red'})
                ]
            ),
            html.Div(children='keywords'), dcc.Input(id='fetch-paper-keywords', type='text', value=''),
            html.Div(children='year'),     dcc.Input(id='fetch-paper-year', type='text', value=''),
            html.Div(children='count'),    dcc.Input(id='fetch-paper-count', type='text', value=''),
            html.Div(children='id'), dcc.Input(id='fetch-paper-id', type='text', value=''),
            html.Button(id='fetch-paper-button', children='Fetch'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='fetch-paper-result-table'
                )
            ),
            html.Div(
                html.H1('Fetch Reference Papers')
            ),
            html.Div(children='id'), dcc.Input(id='fetch-reference-paper-id', type='text', value=''),
            html.Button(id='fetch-reference-paper-button', children='Fetch'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='fetch-reference-paper-result-table'
                )
            ),
            html.H1('Link',),
            dcc.Input(id='link-input', type='text', value='paperid'),
            html.Button(id='link-button', children='Create'),
            html.Br(),
            html.A(id='link-microsoft-url', children='microsoft academic'),
            html.Br(),
            html.A(id='link-google-url', children='google scholar'),
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
            html.H1('CitedBy Search',),
            dcc.Input(id='citedby-search-input', type='text', value='id'),
            html.Button(id='citedby-search-button', children='Search'),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='citedby-search-table'
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
            html.H2(
                id='papers-info-all-count',
                children='...'
            ),
            html.Button(id='papers-info-all-update-button', n_clicks=0, children='Update'),
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
            html.H1('Papers network',),
            html.Div(
                html.H2('Selecte Paper (ID)')
            ),
            dcc.Input(id='paper-network-graph-update-input', type='text', value=''),
            html.Button(id='paper-network-graph-update-button', n_clicks=0, children='Update'),
            html.Div(
                dcc.Graph(
                    id = 'paper-network-graph'
                )
            ),
            html.Div(
                html.H2('Selected Paper')
            ),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='selected-node-info-table'
                )
            ),
            html.Div(
                html.H2('Abstract')
            ),
            html.Div(
                id='selected-paper-abstract'
            ),
            html.Div(
                html.H2('References')
            ),
            html.Div(
                dash_table.DataTable(
                    **default_table_settings,
                    id='selected-paper-references-info-table'
                )
            ),

            html.H1('__END__',)
        ])

    @app.callback(
        [
            Output('link-microsoft-url', 'href'),
            Output('link-google-url', 'href'),
        ],
        [
            Input('link-button', 'n_clicks')
        ],
        [
            State('link-input', 'value')
        ]
    )
    def create_link(n_clicks, id):
        if id not in papers:
            return "invalid id", "invalid id"
        # microsoft academic
        url_m = f"https://academic.microsoft.com/paper/{id}"
        # google scholar
        url_g = f"https://scholar.google.com/scholar?q={'+'.join(papers[id]['title'].split())}"
        return url_m, url_g

    @app.callback(
        [
            Output('selected-node-info-table', 'data'),
            Output('selected-node-info-table', 'columns'),
            Output('selected-node-info-table', 'style_cell_conditional'),
            Output('selected-paper-references-info-table', 'data'),
            Output('selected-paper-references-info-table', 'columns'),
            Output('selected-paper-references-info-table', 'style_cell_conditional'),
            Output('selected-paper-abstract', 'children'),
        ],
        [
            Input('paper-network-graph', 'clickData')
        ]
    )
    def display_click_data(clickData):
        clicked_id = clickData['points'][0]['customdata']
        p = dict()
        p[clicked_id] = papers[clicked_id] if clicked_id in papers else {'id':  clicked_id}
        c1, d1, s1 = table_papers(p)
        ref_papers = {}
        if 'references' in papers[clicked_id]:
            for ref in papers[clicked_id]['references']:
                ref_papers[ref] = papers[ref] if ref in papers else {'id': ref}
        else:
            ref_papers[ref] = {'id':ref}
        c2, d2, s2 = table_papers(ref_papers)
        abstract = papers[clicked_id]['abst'] if 'abst' in papers[clicked_id] else 'Not yet fetched...'
        return d1, c1, s1, d2, c2, s2, abstract
    
    @app.callback(
        Output('paper-network-graph', 'figure'),
        [
            Input('paper-network-graph-update-button', 'n_clicks')
        ],
        [
            State('paper-network-graph-update-input', 'value')
        ]
    )
    def updat_paper_network_graph(n_clicks, paper_id):
        figure = create_papers_network({paper_id:papers[paper_id]}) if 0 < len(paper_id) else create_papers_network('')
        return figure

    @app.callback(
        [
            Output('papers-info-all', 'data'),
            Output('papers-info-all-count', 'children'),
        ],
        [
            Input('papers-info-all-update-button', 'n_clicks')
        ],
    )
    def update_papers_info_all(n_clicks):
        papers = forest_core.get_papers()
        _, d, _ = table_papers(papers)
        return d, len(papers)

    @app.callback(
        [
            Output('fetch-paper-result-table', 'data'),
            Output('fetch-paper-result-table', 'columns'),
            Output('fetch-paper-result-table', 'style_cell_conditional'),
            Output('fetch-paper-error', 'children')
        ],
        [
            Input('fetch-paper-button', 'n_clicks')
        ],
        [
            State('fetch-paper-keywords', 'value'),
            State('fetch-paper-year', 'value'),
            State('fetch-paper-count', 'value'),
            State('fetch-paper-id', 'value'),
            State('fetch-paper-token', 'value'),
        ]
    )
    def fetch_paper_keyword(n_clicks, keywords, year, count, ids, token):

        merged_id_list = None

        if 0 == len(token):
            return None, None, None, 'Token !!!!'

        if 0 < len(ids):
            id_list = ids.split(',')
            merged_id_list = forest_core.fetch_papers_with_id(id_list, token, cache_dir)
        else:
            if 0 == len(keywords):
                return None, None, None, "Keyword or ID !!!!"
            keyword_list = list(map(lambda a: str(a).lower(), keywords.split(',')))
            merged_id_list = forest_core.fetch_papers_with_keyword(keyword_list, year, int(count), token, cache_dir)

        merged_papers = {}
        for id in merged_id_list:
            merged_papers[id] = papers[id]

        c, d, s = table_papers(merged_papers)

        return d, c, s, ""

    @app.callback(
        [
            Output('fetch-reference-paper-result-table', 'data'),
            Output('fetch-reference-paper-result-table', 'columns'),
            Output('fetch-reference-paper-result-table', 'style_cell_conditional')
        ],
        [
            Input('fetch-reference-paper-button', 'n_clicks')
        ],
        [
            State('fetch-reference-paper-id', 'value'),
            State('fetch-paper-token', 'value'),
        ]
    )
    def fetch_paper_keyword(n_clicks, target_id, token):

        merged_id_list = None

        if 0 == len(target_id):
            return

        id_list = []
        for id in papers[target_id]['references']:
            id_list.append(id)
        merged_id_list = forest_core.fetch_papers_with_id(id_list, token, cache_dir)

        merged_papers = {}
        for id in merged_id_list:
            merged_papers[id] = papers[id]

        c, d, s = table_papers(merged_papers)

        return d, c, s

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
            Output('keyword-search-table', 'columns'),
            Output('keyword-search-table', 'style_cell_conditional'),
        ],
        [
            Input('keyword-search-button', 'n_clicks')
        ],
        [
            State('keyword-search-input', 'value'),
        ]
    )
    def update_search_paper_table(n_clicks, inputs):
        found_papers = {}
        id_list = []
        for input in inputs.split(','):
            for id in papers:
                if input.lower() not in papers[id]['title'].lower(): continue
                if input.lower() not in papers[id]['abst'].lower(): continue
                if id in id_list: continue
                found_papers[id] = papers[id]
                id_list.append(id)
        c, d, s = table_papers(found_papers)
        return d, c, s

    @app.callback(
        [
            Output('citedby-search-table', 'data'),
            Output('citedby-search-table', 'columns')
        ],
        [
            Input('citedby-search-button', 'n_clicks')
        ],
        [
            State('citedby-search-input', 'value'),
        ]
    )
    def update_citedby_search_paper_table(n_clicks, target_id):
        citedby_list = []
        for id in papers:
            if target_id in papers[id]['references']:
                citedby_list.append(
                    create_paper_info(papers[id], exclude = ['abst', 'references', 'journal-id', 'pub-name_s', 'citcon'])
                )
        df = pd.DataFrame(citedby_list)
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

