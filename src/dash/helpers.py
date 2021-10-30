import dash
import dash_html_components as html

def render_cell(content, is_image):
    if is_image:
        return html.Img(src=content)
    else:
        return content


"""
"""
def generate_table_pics(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(render_cell(dataframe.iloc[i][col], i==0)) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
, style={'float': 'right','margin': 'auto', 'width': '50%'})



def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
, style={'float': 'right','margin': 'auto', 'width': '100%'})