import dash
from dash import html
import pandas as pd
from index import setup_callbacks
import plotly.express as px
px.set_mapbox_access_token(open(".mapbox_token").read())

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
    num = len(dataframe.columns)
    setup_callbacks(num)
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
def get_trips_df(n_clicks, start_date, start_loc, dest_loc, start_time):
    if n_clicks == 0:
        return pd.DataFrame()
    else:
        picsum = 'https://picsum.photos/200/150'
        d = {'col1': [picsum, start_loc], 'col2': [picsum, start_time], 'col3': [picsum, dest_loc]}
        df = pd.DataFrame(data=d)
        return df

"""
get nicely formatted train arrival df
"""
def get_arrival_df():
    # mock data 2B replaced
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
    hike_dict = {'departure': ['16.00', '16.30'], 'arrival': ['16.30', '17.30'], 'POI': ['some location', 'some other location']}
    hike_data = pd.DataFrame(data=hike_dict)
    return hike_data

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