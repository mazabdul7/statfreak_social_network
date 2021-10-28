'''Code by Toby Katerbau'''
import pandas as pd
import matplotlib.pyplot as plt
import plotly_express as px
import plotly.graph_objects as go
import json


def matplotlib_graph():
    df_crime = pd.read_csv(
        "statfreak/dashapp/data/MPS Borough Level Crime (most recent 24 months) (1).csv")
    df_personal_well_being = pd.read_excel(
        "statfreak/dashapp/data/personal-well-being-borough.xlsx", "Anxiety")

    df_crime['average_crime'] = df_crime.mean(axis=1)
    df_crime = df_crime[['LookUp_BoroughName', 'average_crime']]
    df_crime = df_crime.groupby(
        'LookUp_BoroughName', as_index=False).average_crime.mean()
    df_crime.rename(columns={'LookUp_BoroughName': 'Borough'}, inplace=True)
    df_personal_well_being.rename(
        columns={'Unnamed: 1': 'Borough'}, inplace=True)
    df_personal_well_being = df_personal_well_being[[
        'Borough', '2018/19', 'Unnamed: 38', 'Unnamed: 39', 'Unnamed: 40']]
    df = pd.merge(df_crime, df_personal_well_being, on="Borough")

    #Averaging out the anxiety was done by multiplying the scores by their population
    df['average_anxiety'] = (2*df['2018/19'] + 5.5*df['Unnamed: 38'] +
                             7.5*df['Unnamed: 39'] + 9.5*df['Unnamed: 40'])/100
    df = df.drop(columns=['2018/19', 'Unnamed: 38',
                          'Unnamed: 39', 'Unnamed: 40'])

    fig = plt.figure(figsize=[7, 5])
    ax = plt.subplot(111)
    ax.plot(df['average_crime'], df['average_anxiety'], 'xr')
    ax.set_title('Showing How Population Anxiety and Crime are Related')
    ax.set_xlabel('Average Crime')
    ax.set_ylabel('Average Anxiety')
    ax.set_facecolor('aliceblue')
    ax.grid('on', color='lightsteelblue', linestyle='dashed')
    fig.savefig('toby_matplotlib.png')


def plot_plotly_go_graph(room_type):
    df_crime = pd.read_csv(
        "statfreak/dashapp/data/MPS Borough Level Crime (most recent 24 months) (1).csv")
    df_crime['average_crime'] = df_crime.mean(axis=1)
    df_crime = df_crime[['LookUp_BoroughName', 'average_crime']]
    df_crime = df_crime.groupby(
        'LookUp_BoroughName', as_index=False).average_crime.mean()
    df_crime.sort_values('average_crime', inplace=True)
    df_crime.rename(columns={'LookUp_BoroughName': 'Borough'}, inplace=True)
    boroughs = df_crime.Borough.unique()

    tables = {'Room': 'Table2.1',
              'Studio': 'Table2.2',
              'One Bedroom': 'Table2.3',
              'Two Bedrooms': 'Table2.4',
              'Three Bedrooms': 'Table2.5',
              'Four or more Bedrooms': 'Table2.6'}

    table_number = tables[room_type]
    df_rental_prices = pd.read_excel(
        'statfreak/dashapp/data/privaterentalmarketstatistics11122020.xls', table_number, skiprows=6)
    df_rental_prices = df_rental_prices[df_rental_prices.Area.isin(boroughs)]
    df_rental_prices = df_rental_prices[[
        'Area', 'Mean', 'Lower quartile', 'Upper quartile']]
    df_rental_prices.rename(
        columns={'Area': 'Borough', 'Mean': 'Mean Rent'}, inplace=True)
    df = pd.merge(df_rental_prices, df_crime, on='Borough')
    df.sort_values('average_crime', inplace=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["average_crime"], y=df['Mean Rent'], mode='markers+text',
                             hovertemplate='Crime: %{x:.2f}'+'<br>Price: %{y:.2f}', text=df['Borough']))
    fig.update_layout(
        title_text=f'Average rent price of {room_type} against the crime rates in the borough',
        height=700
    )
    fig.update_traces(textposition='top center')
    fig.update_xaxes(title='Average number of Crimes committed per month')
    fig.update_yaxes(title='Mean rent prices')

    return fig


def plot_plotly_map(borough_selected, crimes_selected):
    mapbox_token = "pk.eyJ1IjoidG9ieWxvYnkxMiIsImEiOiJja2xkbW9hcnYxMHdtMndzNG1kZmluMzRrIn0.-DR2q688bSOEXj3ls3IK_g"
    px.set_mapbox_access_token(mapbox_token)
    geojson = 'london_boroughs.json'
    df_crime = pd.read_csv(
        "statfreak/dashapp/data/MPS Borough Level Crime (most recent 24 months) (1).csv")
    df_location = pd.read_excel(
        "statfreak/dashapp/data/personal-well-being-borough.xlsx", "Summary - Mean Scores")

    columns = list(df_location.columns)
    first = columns[0]
    df_location = df_location[[
        first, 'Unnamed: 1', 'Unnamed: 37', 'Unnamed: 38']]
    df_location.rename(columns={first: 'Area_code', 'Unnamed: 1': 'Borough',
                                'Unnamed: 37': 'latitude', 'Unnamed: 38': 'longitude'}, inplace=True)
    df_crime.rename(
        columns={'LookUp_BoroughName': 'Borough', 'MinorText': 'Crime'}, inplace=True)

    with open('statfreak/dashapp/data/london_boroughs.json') as json_file:
        geojson = json.load(json_file)

    df_crime['mean'] = df_crime.mean(axis=1)
    df_crime = df_crime[['Crime', 'Borough', 'mean']]

    df = pd.merge(df_crime, df_location, on='Borough')
    fig = px.choropleth_mapbox(df, geojson=geojson, color="mean",
                               locations="Borough", featureidkey="properties.name",
                               center=dict(lat=51.5, lon=0.1278), hover_name="Borough", opacity=0.5,
                               title="Average crime rates in London over the last 24 months",
                               range_color=[0, 600],
                               height=700
                               )
    df2 = df[['Area_code', 'Borough', 'Crime', 'mean']]
    df2 = df2[df2.Borough == borough_selected]

    df2 = df2[df2['Crime'].isin(crimes_selected)]

    fig2 = px.bar(df2, x='Crime', y='mean',
                  title=f'Some of the average crime rates in {borough_selected} over the last 24 months')

    return fig, fig2


plot_plotly_go_graph('Studio')
