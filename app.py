from pydoc import classname

from click import style
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table

# Load the dataset
avocado = pd.read_csv('data/avocado-updated.csv')


avocado[' index'] = range(1, len(avocado) + 1)
# Create the Dash app
app = dash.Dash()

# Set up the app layout
'''app.layout = html.Div(children=[
    html.H1(children='Avocado Prices Dashboard'),
    dcc.Dropdown(id='geo-dropdown',
                 options=[{'label': i, 'value': i}
                          for i in avocado['geography'].unique()],
                 value='New York'),
    dcc.Graph(id='price-graph')
])'''



app.layout = html.Div(children=[
                html.Div(className='row',  # Define the row element
                        children=[
                            html.Div(className='four columns div-user-controls',
                            children = [
                                html.H1(children='Avocado Dashboard',style={'color':'white'}),
                                dcc.Dropdown(id='geo-dropdown',
                                            options=[{'label': i, 'value': i}
                                                    for i in avocado['geography'].unique()],
                                            value='New York')
                            ], style={'color': 'black'}
                            ),  # Define the left element
                            html.Div(className='eight columns div-for-charts bg-grey',
                            children = [
                                    dcc.Graph(id='price-graph'),
                                    dcc.Graph(id="pie-chart"),
                                    dash_table.DataTable(
                                        id='table-filtering',
                                        columns=[
                                            {"name": i, "id": i} for i in sorted(avocado.columns)
                                        ],
                                        page_current=0,
                                        page_size=10,
                                        page_action='custom',

                                        filter_action='custom',
                                        filter_query=''
                                    )
                                    
                            ], style={'color': 'black'})  # Define the right element
                            ])

                        ])

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

# Set up the callback function
@app.callback(
    Output(component_id='price-graph', component_property='figure'),
    Input(component_id='geo-dropdown', component_property='value')
)
def update_graph(selected_geography):
    filtered_avocado = avocado[avocado['geography'] == selected_geography]
    line_fig = px.line(filtered_avocado,
                       x='date', y='average_price',
                       color='type',
                       title=f'Avocado Prices in {selected_geography}')
    return line_fig

@app.callback(
    Output("pie-chart", "figure"), 
    [Input(component_id='geo-dropdown', component_property='value')])
def generate_chart(selected_geography):
    filtered_avocado = avocado[avocado['geography'] == selected_geography]
    fig = px.pie(filtered_avocado, values='year', names='type',title=f'Avocado Type Ratio in {selected_geography}')
    return fig

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@app.callback(
    Output('table-filtering', "data"),
    Input('table-filtering', "page_current"),
    Input('table-filtering', "page_size"),
    Input('table-filtering', "filter_query"))
def update_table(page_current,page_size, filter):
    print(filter)
    filtering_expressions = filter.split(' && ')
    dff = avocado
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)