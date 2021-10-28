'''Code by Paul Ho, Mazin Abdulmahmood, Toby Katerbau'''
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from statfreak.dashapp.toby_graphs import plot_plotly_go_graph, plot_plotly_map
from dash.dependencies import Output, Input
from statfreak.dashapp.my_dash_app_data import CrimeData
from statfreak.dashapp.my_plotly_go_file import WellbeingChart


bed_list = ["Studio", "One Bedroom", "Two Bedrooms",
            "Three Bedrooms", "Four or more Bedrooms"]
boroughs = ['Barking and Dagenham', 'Barnet', 'Bexley', 'Brent', 'Bromley', 'Camden', 'Croydon', 'Ealing',
            'Enfield', 'Greenwich', 'Hackney', 'Hammersmith and Fulham', 'Haringey', 'Harrow', 'Havering',
            'Hillingdon', 'Hounslow', 'Islington', 'Kensington and Chelsea', 'Kingston upon Thames', 'Lambeth',
            'Lewisham', 'Merton', 'Newham', 'Redbridge', 'Richmond upon Thames', 'Southwark', 'Sutton', 'Tower Hamlets',
            'Waltham Forest', 'Wandsworth', 'Westminster']
crimes = ['Arson', 'Criminal Damage', 'Burglary - Business and Community', 'Burglary - Residential', 'Drug Trafficking',
          'Possession of Drugs', 'Absconding from Lawful Custody', 'Bail Offences', 'Bigamy', 'Dangerous Driving', 'Disclosure, Obstruction, False or Misleading State',
          'Exploitation of Prostitution', 'Forgery or Use of Drug Prescription', 'Fraud or Forgery Associated with Driver Records', 'Going Equipped for Stealing',
          'Handling Stolen Goods', 'Making, Supplying or Possessing Articles for use i', 'Obscene Publications', 'Other Forgery', 'Other Notifiable Offences', 'Perjury',
          'Perverting Course of Justice', 'Possession of False Documents', 'Profitting From or Concealing Proceeds of Crime', 'Soliciting for Prostitution',
          'Threat or Possession With Intent to Commit Crimina', 'Other Firearm Offences', 'Possession of Article with Blade or Point', 'Possession of Firearm with Intent',
          'Possession of Firearms Offences', 'Possession of Other Weapon', 'Other Offences Against the State, or Public Order', 'Public Fear Alarm or Distress',
          'Racially or Religiously Aggravated Public Fear, Al', 'Violent Disorder', 'Robbery of Business Property', 'Robbery of Personal Property', 'Other Sexual Offences',
          'Rape', 'Bicycle Theft', 'Other Theft', 'Shoplifting', 'Theft from Person', 'Aggravated Vehicle Taking', 'Interfering with a Motor Vehicle',
          'Theft from a Motor Vehicle', 'Theft or Taking of a Motor Vehicle', 'Homicide', 'Violence with Injury', 'Violence without Injury']

fig, fig2 = plot_plotly_map('Barking and Dagenham', ['Criminal Damage', 'Burglary - Business and Community', 'Possession of Drugs',
                                                     'Theft from Person', 'Violence with Injury'])
graph = dcc.Graph(figure=fig)
graph2 = dcc.Graph(figure=fig2)
data = CrimeData()
area1 = "Brent"
area2 = "Haringey"
area3 = "Camden"
data.process_data(area1, area2, area3)
wb = WellbeingChart()
fig4 = wb.create_radar_chart("Brent", "Camden")


def init_dashboard(flask_app):
    """Create a Plotly Dash dashboard."""

    dash_app = dash.Dash(server=flask_app,
                         routes_pathname_prefix="/dashapp2/",
                         external_stylesheets=[dbc.themes.BOOTSTRAP],
                         )

    dash_app.layout = dbc.Container(fluid=True, children=[
        html.Div(children=[
            html.H4(children='Crime Statistics in London'),
            dbc.Row([
                dbc.Col(width={'size': 4}, children=[
                    html.Div([
                        dbc.Card(
                            html.H6('Use the dropdown menu to select crimes'),
                        )
                    ]),
                    dcc.Dropdown(
                        id='crimes-selected',
                        options=[{'label': x, 'value': x} for x in crimes],
                        value=['Criminal Damage', 'Burglary - Business and Community', 'Possession of Drugs',
                               'Theft from Person', 'Violence with Injury'],
                        multi=True
                    ),
                    dcc.Graph(
                        id='bar-chart'
                    ),
                ]),

                dbc.Col(width=8, children=[
                    dbc.FormGroup([
                        html.H6(
                            'Hover over the area you want to see more detailed crime statistics for')
                    ]),
                    dcc.Graph(
                        id='chloropleth-map',
                        hoverData={'points': [
                            {'location': 'Barking and Dagenham'}]}
                    ),
                ])
            ]),
            dbc.Row([
                dbc.Col(children=[
                    html.H4('Comparison of average wellbeing statistics')
                ])
            ]),
            dbc.Row([
                dbc.Col(width=3, children=[
                    dbc.FormGroup([
                        html.H6("Select Areas"),
                        dcc.Dropdown(id="area_select_radar1", options=[{"label": x, "value": x} for x in data.allareas],
                                     value="Brent"),
                        dcc.Dropdown(id="area_select_radar2", options=[{"label": x, "value": x} for x in data.allareas],
                                     value="Camden"),
                    ]),

                ]),
                dbc.Col(width=9, children=[
                    html.Div(id="output-panel"),
                    dcc.Graph(id="radar-chart"),
                ]),
            ]),
        ])
    ])
    init_callbacks(dash_app)
    return dash_app.server


def init_callbacks(dash_app):
    @dash_app.callback(
        Output("chloropleth-map", "figure"),
        [Input('chloropleth-map', 'hoverData'),
         Input('crimes-selected', 'value')])
    def update_graph(borough_selected, crimes):
        fig, fig2 = plot_plotly_map(borough_selected, crimes)
        return fig

    @dash_app.callback(
        Output("bar-chart", "figure"),
        [Input('chloropleth-map', 'hoverData'),
         Input('crimes-selected', 'value')])
    def update_bar_chart(hover_data, crimes):
        hover_location = hover_data['points'][0]['location']
        fig, fig2 = plot_plotly_map(hover_location, crimes)
        return fig2

    @dash_app.callback(
        Output("rent-crime-graph", 'figure'),
        [Input('room-selected', 'value')])
    def update_go_plot(room_select):
        fig = plot_plotly_go_graph(room_select)
        return fig

    @dash_app.callback(Output("radar-chart", "figure"), [Input("area_select_radar1", "value"),
                                                         Input("area_select_radar2", "value")])
    def render_output_panel(area_select_radar1, area_select_radar2):
        fig4 = wb.create_radar_chart(area_select_radar1, area_select_radar2)
        return fig4
