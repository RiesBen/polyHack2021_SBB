import dash, os
from dash import html
import datetime
import pandas as pd
import plotly.express as px
from src.backend.searchRankedTrips import backend_storage

px.set_mapbox_access_token(open(".mapbox_token").read())

d = dash.Dash()
backend = backend_storage()
outLim = 4
def render_cell(content, is_image):
    if is_image:
        return html.Img(src=content)
    else:
        return content


def render_button(content, id):
    return html.Button(children=content, id=id, n_clicks=0)

"""
"""
def generate_table_pics(dataframe, max_rows=3):
    return html.Table(
        # Header
        [html.Tr([html.Th(render_button(col, 'trip_' + str(colnum))) for colnum,col in enumerate(dataframe.columns)])] +
        # Body
        [html.Tr([
            html.Td(render_cell(dataframe.iloc[i][col], i==0)) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
, style={'float': 'left','margin': 'auto', 'width': '50%'})


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
, style={'float': 'right','margin': 'auto', 'width': '100%'})

"""
Call backend API to get relevant trips to pd.DataFrame
Here we make mock df just to show that things are being updated
"""
def get_trips_df(n_clicks, start_date, start_loc, dest_loc, dest_rad, start_time, limit_output=outLim, offset=0):
    #print(start_date, start_time, start_loc, dest_loc, dest_rad)
    format=[256,128]
    if n_clicks == 0:
        from src.backend.utils import get_pictures
        ranked_data = backend.get_switzerland_rankings()
        d = {}
        if(ranked_data.shape[0]>offset):
            for i, row in list(ranked_data.iterrows())[offset:]:
                if(len(d)>=limit_output):
                    break
                else:
                    if(not isinstance(row['images'], float)):
                        d.update({row.title: [get_pictures(row, url_mode=True, limit_pics=1, format=format)[0],
                                 row['startingPointDescr']]})
        return pd.DataFrame(d)

    elif(start_loc is not None and dest_loc is not None):
        if(start_time is None):
            start_time = datetime.time()
        else:
            start_time = datetime.time.fromisoformat(start_time)
        if(start_date is None):
            start_date = datetime.date()
        else:
            start_date = datetime.date.fromisoformat(start_date)
        if (dest_rad is not None):
            dest_rad = 5

        start_datetime = datetime.datetime.combine(start_date, start_time)
        from src.backend.utils import get_pictures
        d = {}
        ranked_data = backend.get_trips_ranking(startLocation=start_loc, starting_time=start_datetime,
                                                destination=dest_loc, destination_radius=dest_rad * 1000)

        if (ranked_data.shape[0] > offset):
            for i, row in list(ranked_data.iterrows())[offset:]:
                if (len(d) >= limit_output):
                    break
                else:
                    if (not isinstance(row['images'], float)):
                        d.update({row.title: [get_pictures(row, url_mode=True, limit_pics=1, format=format)[0],
                                              row['startingPointDescr']]})
        df = pd.DataFrame(data=d)
        return df
    else:
        pass

"""
get nicely formatted train arrival df
"""
def get_arrival_df():
    # mock data 2B replaced
    selected_trip = backend.get_selected_trip()

    if(selected_trip is not None):
        print("FUNFUNFUN")
        departure = [datetime.datetime.fromisoformat(trip['segments'][0]["stops"][0]["departureDateTime"]).strftime('%H:%M') for trip in selected_trip['tripsToDestination']]
        arrival = [datetime.datetime.fromisoformat(trip['segments'][-1]["stops"][-1]["arrivalDateTime"]).strftime('%H:%M') for trip in selected_trip['tripsToDestination']]

        track = [trip['segments'][0]["stops"][0]["departureTrack"] for trip in selected_trip['tripsToDestination']]
        name_from = [trip['segments'][0]["stops"][0]["name"] for trip in selected_trip['tripsToDestination']]
        name_to = [trip['segments'][-1]["stops"][-1]["name"] for trip in selected_trip['tripsToDestination']]

        train_dict = {'departure': departure, 'arrival': arrival, \
            'from': name_from, 'to': name_to, 'track': track}
    else:
        train_dict = {'departure': ['14.00', '14.34', '15.20'], 'arrival': ['14:29', '15:11', '15.55'], \
            'from': ['HB', 'Bern', 'Basel'], 'to': ['Bern', 'Basel', 'Allschwil'], 'line': ['IC 14', 'R 5', 'T6'], \
                'track': ['1', '2', '-']}
    train_data = pd.DataFrame(data=train_dict)
    return train_data


"""
same for return trip
"""
def get_return_df():
    return get_arrival_df()


"""
get trip data
"""
def get_activity_df():
    selected_trip = backend.get_selected_trip()
    print(selected_trip)
    if(selected_trip is not None):
        duration = str(datetime.timedelta(minutes=selected_trip['time']['min']))
        startDesc = selected_trip['startingPointDescr']
        difficulty = selected_trip['rating']['difficulty']
        ascent = selected_trip['elevation']['ascent']
        descent = selected_trip['elevation']['descent']
        length = selected_trip['length']/1000

        #print(storage.selected_trip)
        hike_dict = {'duration': [duration], 'startDesc': [startDesc],  'length': [length], 'descent':[descent], 'ascent':[ascent], "difficutly":[difficulty]}
        hike_data = pd.DataFrame(data=hike_dict)
    else:
        hike_data = pd.DataFrame({})
    return hike_data


def update_map(num):
    selected_trip = num

"""
render map
lat: latitude
lon: longitude
route_type: train or trail (change this to whatever the input df looks like)
"""
def render_map(data):
    #us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
    #us_cities = us_cities.query("State in ['New York', 'Ohio']")
    fig = px.line_mapbox(data, lat="lat", lon="lon", color="route_type", zoom=3, height=500)
    fig.update_layout(mapbox_zoom=4, mapbox_center_lat = 41, \
                            margin={"r":0,"t":0,"l":0,"b":0})
    return fig


from dash import dcc
from datetime import date

def build_explor():
    struct = html.Td([
        #html.H3('Explore'),
        html.Div([
        dcc.Input(id="start_loc", type="text", placeholder="start location", style={'marginRight': '10px'}),
        dcc.Input(id="dest_loc", type="text", placeholder="destination", style={'marginRight': '10px'}),
        dcc.Input(id="dest_rad", type="number", placeholder="radius km", min=1, max=100, step=1,
                  style={'marginRight': '10px'}),
        dcc.DatePickerSingle(
            id='start_date',
            date=date.today()
        ),
        dcc.Input(
            id="start_time",
            type="text",
            placeholder="HH:MM",
        ),
        html.Button(children='Submit', id='submit-val', n_clicks=0),
        ], style={'horizontalAlign':"center"}),
        html.Div([
            html.Div([])
        ], id='trips'),
        html.Div([
            html.Div([])
        ], id='trips2'),
        html.Div([
            html.Div([])
        ], id='trips3')
    ], style={'width': '50%', 'verticalAlign': 'top', 'textAlign': 'center'})

    return struct

def build_plan():
    struct =  html.Tr([
                    html.Td([
                    #html.H1('Planning'),
                    html.H2('Activity'),
                    html.H3('Route'),
                    html.Div([
                        generate_table(get_activity_df())
                    ]),
                    html.H3('Map'),
                    html.Div([
                        dcc.Graph(
                            id='map-graph',
                            figure=render_map(pd.DataFrame(columns=['lat', 'lon', 'route_type']))
                        )
                    ], id='map'),
                    ], style={'width': '50%', 'verticalAlign': 'top'}),
                    html.Td([
                    html.H2('Getting There'),
                    html.H3('Arrival'),
                    html.Div([
                        generate_table(get_arrival_df())
                    ]),
                    html.H3('Return'),
                    html.Div([
                        generate_table(get_return_df())
                    ])
                    ], style={'width': '50%', 'verticalAlign': 'top', 'margin':"1%"}),
                ], style={"width": "100%", "align-items": "top", "justify-content": "center", 'verticalAlign': 'top'})
    return struct
