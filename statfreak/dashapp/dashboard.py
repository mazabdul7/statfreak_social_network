'''Code by Paul Ho, Mazin Abdulmahmood'''
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from statfreak.dashapp.generatefig import generatefig
from dash.dependencies import Output, Input


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    bed_list = ["Studio", "One Bedroom", "Two Bedroom",
                "Three Bedroom", "Four+ Bedroom"]
    gen = generatefig()
    dash_app.layout = html.Div(children=[
        dbc.Row([
            html.Br(),
            dbc.Col(width=4, children=[
                dbc.FormGroup([
                    html.H4("Select Room Count"),
                    dcc.Dropdown(id="bed_select", options=[
                        {"label": x, "value": x} for x in bed_list], value="Studio")
                ]),
                html.Div([
                    dbc.Card(body=True, className="bg-light text-dark", children=[
                        html.H4("Quartile Statistics"),
                        html.H6("Select an area"),
                        html.Br(),
                        dcc.Dropdown(id="area_select", options=[
                            {"label": x, "value": x} for x in gen.getareas()], value="Camden"),
                        html.Br(),
                        html.Div(id="stats")
                    ])
                ])
            ]),
            dbc.Col(width=8, children=[
                html.Div(id="output-panel", className=""),
                html.Br(),
                dbc.Card(body=True, className="bg-white text-dark", children=[
                    html.Div(id="piechart", style={
                         'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                ]),
            ])
        ]),
    ])

    init_callbacks(dash_app)

    return dash_app.server


def init_callbacks(app):
    @app.callback(Output("output-panel", "children"), [Input("bed_select", "value")])
    def update_graph(bed_select):
        initclass = generatefig()
        fig = initclass.genfig(bednumber=bed_select)
        graph = dcc.Graph(figure=fig)
        return graph

    @app.callback([Output("stats", "children"), Output("piechart", "children")], [Input("area_select", "value"), Input("bed_select", "value")])
    def render_stats(area_select, bed_select):
        stats = []
        initclass = generatefig()
        fig = initclass.genstats(bednumber=bed_select, area=area_select)
        fig2, fig3 = initclass.bestpartysize(area=area_select)
        graph = dcc.Graph(figure=fig)
        graph2 = dcc.Graph(figure=fig2)
        graph3 = dcc.Graph(figure=fig3)

        panel = [
            graph,
            html.Br(),
            html.H6("Average rent price per person: £%d" %
                    (initclass.pricepp), className="card-title text-justify"),
            graph2,
            html.H6("We recommend a group size of %s which works out to £%d per person." % (initclass.lowestsize, initclass.lowestppp), className="card-title text-justify")]

        return panel, graph3
