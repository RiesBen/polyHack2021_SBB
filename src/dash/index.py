import dash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc

import plotly.express as px
px.set_mapbox_access_token(open(".mapbox_token").read())
import pandas as pd
from datetime import date

from helpers import generate_table, generate_table_pics, get_activity_df, get_arrival_df, get_return_df, get_trips_df, render_map, update_map, build_explor, build_plan, outLim

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

app.enable_dev_tools(debug=True, dev_tools_props_check=False)

app.layout = html.Div([
        html.H1('SBB Explor', style={"background":"#f0111c", "color":'#ffffff',  "width":"100%", "height":"12%", "padding":"2%"}),
        dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
            dcc.Tab(label='Explore!', value='tab-1-example-graph'),
            dcc.Tab(label='Plan!', value='tab-2-example-graph'),
        ]),
        html.Div(id='tabs-content-example-graph')
    ])


@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return build_explor()
    elif tab == 'tab-2-example-graph':
        return build_plan()



"""
update trips once input submitten
"""

@app.callback(
    Output("trips", "children"),
    Input("submit-val", 'n_clicks'),
    Input("start_date", "date"),
    State("start_loc", "value"),
    State("dest_loc", "value"),
    State("dest_rad", "value"),
    State("start_time", "value")
)
def update_output(n_clicks, start_date, start_loc, dest_loc, dest_rad, start_time):
    new_df = get_trips_df(n_clicks, start_date, start_loc, dest_loc, dest_rad,  start_time)
    return generate_table_pics(new_df)

@app.callback(
    Output("trips2", "children"),
    Input("submit-val", 'n_clicks'),
    Input("start_date", "date"),
    State("start_loc", "value"),
    State("dest_loc", "value"),
    State("dest_rad", "value"),
    State("start_time", "value")
)
def update_output(n_clicks, start_date, start_loc, dest_loc, dest_rad, start_time):
    new_df = get_trips_df(n_clicks, start_date, start_loc, dest_loc, dest_rad,  start_time, offset=outLim   )
    return generate_table_pics(new_df)

"""
update map & routes once trip selected
"""
'''
@app.callback(
    Output('map', 'children'),
    Input('trip_0', 'n_clicks')
)
def update_map_0(n_clicks):
    if n_clicks > 0:
        update_map(0)

@app.callback(
    Output('map', 'children'),
    Input('trip_1', 'n_clicks')
)
def update_map_1(n_clicks):
    if n_clicks > 0:
        update_map(1)

@app.callback(
    Output('map', 'children'),
    Input('trip_2', 'n_clicks')
)
def update_map_2(n_clicks):
    if n_clicks > 0:
        update_map(2)

@app.callback(
    Output('map', 'children'),
    Input('trip_3', 'n_clicks')
)
def update_map_3(n_clicks):
    if n_clicks > 0:
        update_map(3)

@app.callback(
    Output('map', 'children'),
    Input('trip_4', 'n_clicks')
)
def update_map_4(n_clicks):
    if n_clicks > 0:
        update_map(4)
'''


if __name__ == '__main__':
    app.run_server(debug=True)

