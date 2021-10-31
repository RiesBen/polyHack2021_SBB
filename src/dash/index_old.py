import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

import plotly.express as px
px.set_mapbox_access_token(open(".mapbox_token").read())
import pandas as pd

from helpers import generate_table, generate_table_pics

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Dash Tabs component demo'),
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph'),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
    ]),
    html.Div(id='tabs-content-example-graph')
])

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
us_cities = us_cities.query("State in ['New York', 'Ohio']")

@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':

        # mock data 2B replaced
        train_dict = {'departure': ['14.00', '14.34', '15.20'], 'arrival': ['14:29', '15:11', '15.55'], \
            'from': ['HB', 'Bern', 'Basel'], 'to': ['Bern', 'Basel', 'Allschwil'], 'line': ['IC 14', 'R 5', 'T6'], \
                'track': ['1', '2', '-']}
        train_data = pd.DataFrame(data=train_dict)

        hike_dict = {'departure': ['16.00', '16.30'], 'arrival': ['16.30', '17.30'], 'POI': ['some location', 'some other location']}
        hike_data = pd.DataFrame(data=hike_dict)

        fig = px.line_mapbox(us_cities, lat="lat", lon="lon", color="State", zoom=3, height=500)

        fig.update_layout(mapbox_zoom=4, mapbox_center_lat = 41, \
            margin={"r":0,"t":0,"l":0,"b":0})
        return html.Table([
                html.Tr([
                    html.Td([
                        html.H3('Arrival'),
                        html.Div([
                            generate_table(train_data)
                        ]),
                        html.H3('Outdoor activity'),
                        html.Div([
                            generate_table(hike_data)
                        ]),
                        html.H3('Return'),
                        html.Div([
                            generate_table(train_data)
                        ])
                    ], style={'width': '40%'}),
                    html.Td([
                        html.H3('Tab content 1'),
                        dcc.Graph(
                            id='graph-1-tabs',
                            figure=fig
                        )
                    ])
                ])
        ], style={'float': 'right','margin': 'auto', 'width': '100%'})
    elif tab == 'tab-2-example-graph':
        picsum = 'https://picsum.photos/300/200'
        d = {'col1': [picsum, 'second line'], 'col2': [picsum, 'whatever comes here']}
        df = pd.DataFrame(data=d)
        all_options = ['first', 'second', 'third']
        return html.Div([ 
            html.Div(
            [
                dcc.Dropdown(
                    id="demo-dropdown",
                    options=[
                        {"label": "Upload Scores", "value": "upload_scores"},
                        {"label": "Analyze Portfolios", "value": "analyze_portfoliio"},
                        {
                            "label": "Generate Data for IC Engine",
                            "value": "gen_data_ic_engine",
                        },
                    ],
                    placeholder="Select a task...",
                    # style={"width": "50%"},  NOT HERE
                ),
                html.Div(id="dd-output-container"),
            ],
            style={"width": "50%", "align-items": "center", "justify-content": "center"},
        ),
        generate_table_pics(df)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)