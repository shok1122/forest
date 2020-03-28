import dash  
import dash_core_components as dcc 
import dash_html_components as html  

import forest_cui

def figure_citation_count(papers):
    X = list(papers.keys())
    Y = []
    for x in X:
        Y.append(str(papers[x]['citation_count']))
    for i in range(len(X)):
        X[i] = 'id:' + X[i]
    print(X)
    print(Y)
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

def figure_reference_count(papers):
    X = list(papers.keys())
    Y = []
    for x in X:
        Y.append(len(papers[x]['references']))
    for i in range(len(X)):
        X[i] = 'id:' + X[i]
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

def figure_display_count(info):
    X = list(info.keys())
    Y = []
    for x in X:
        Y.append(info[x]['count'])
    for i in range(len(X)):
        X[i] = 'id:' + X[i]
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
            'title': 'display count'
        }
    }
    return fig

def forest(keywords, count = 1000, rank = 100, tier = 1, output_dir = 'cache', input_dir = None):
    papers, info = forest_cui.forest(keywords, count, rank, tier, output_dir, input_dir)
    fig_cit_cnt = figure_citation_count(papers)
    fig_ref_cnt = figure_reference_count(papers)
    fig_disp_cnt = figure_display_count(info)
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
                id = 'display count',
                figure = fig_disp_cnt
            )
        ])
    app.run_server(debug=True)

# 実行用③
if __name__=='__main__':
    app.run_server(debug=True)