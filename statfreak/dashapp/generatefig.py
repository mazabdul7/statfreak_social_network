'''Code by Paul Ho, Mazin Abdulmahmood'''
import numpy as np
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt


class generatefig:
    def __init__(self):
        self.upperquartile = 0
        self.lowerquartile = 0
        self.arealist = ['Barking and Dagenham', 'Barnet', 'Bexley', 'Brent', 'Bromley', 'Camden', 'Croydon', 'Ealing',
                         'Enfield', 'Greenwich', 'Hackney', 'Hammersmith and Fulham', 'Haringey', 'Harrow', 'Havering', 'Hillingdon',
                         'Hounslow', 'Islington', 'Kensington and Chelsea', 'Kingston upon Thames', 'Lambeth', 'Lewisham', 'Merton',
                         'Newham', 'Redbridge', 'Richmond upon Thames', 'Southwark', 'Sutton', 'Tower Hamlets', 'Waltham Forest', 'Wandsworth',
                         'Westminster']
        self.bed_map = {
            "Studio": ['Table2.2', 1],
            "One Bedroom": ['Table2.3', 1],
            "Two Bedroom": ['Table2.4', 2],
            "Three Bedroom": ['Table2.5', 3],
            "Four+ Bedroom": ['Table2.6', 4]}
        self.average = 0
        self.pricepp = 0
        self.lowestppp = 0
        self.lowestsize = ""

    def getareas(self):
        return self.arealist

    #Generates the map box plot - takes input of bednumber from the dropdown
    def genfig(self, bednumber):
        df = pd.read_excel('statfreak/dashapp/data/privaterentalmarketstatistics11122020.xls',
                           sheet_name=self.bed_map[bednumber][0], skiprows=6)
        rows = list(range(218, 252))
        rows.remove(219)
        rows.remove(232)
        df = df.iloc[rows, list(range(3, 9))]
        df = df.sort_values('Area', ascending=True)
        df = df.reset_index(drop=True)

        #Get latitude and longitude of areas from the wellbeing dataset
        dfloc = pd.read_excel('statfreak/dashapp/data/personal-well-being-borough.xlsx',
                              sheet_name='Summary - Mean Scores', skiprows=1)
        # Extract Lat and Long data
        dfloc = dfloc.iloc[list(range(0, 34)), [37, 38]]
        dfloc = dfloc.drop([0, 1])
        dfloc = dfloc.reset_index(drop=True)

        #Merge location info to rental data
        df['Latitude'] = dfloc['Latitude']
        df['Longitude'] = dfloc['Longitude']
        df.iloc[:, list(range(1, 6))] = np.array(
            df.iloc[:, list(range(1, 6))], dtype=np.float64)

        token = "pk.eyJ1IjoibWF6YWJkdWwiLCJhIjoiY2trMWh1aXRsMHJhMjJxbzU0eTYzbTI5ZiJ9.DIP735c0I4CbxFHmTtNBCw"
        fig = px.scatter_mapbox(
            df,
            lat=df.Latitude,
            lon=df.Longitude,
            size="Median",
            hover_name="Area",
            color="Median",
            color_discrete_sequence=["brwnyl"],
            size_max=14,
            zoom=10,
            title="Median price of rent by borough"
        )
        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig.update_layout(
            margin={"r": 15, "t": 0, "l": 15, "b": 0}, height=550)

        return fig

    #Generates Quartile graph
    #Takes input of bed size and the chosen borough
    def genstats(self, bednumber, area):
        df = pd.read_excel('statfreak/dashapp/data/privaterentalmarketstatistics11122020.xls',
                           sheet_name=self.bed_map[bednumber][0], skiprows=6)
        rows = list(range(218, 252))
        rows.remove(219)
        rows.remove(232)
        df = df.iloc[rows, list(range(3, 9))]
        df = df.sort_values('Area', ascending=True)
        df = df.reset_index(drop=True)

        #Extract the data relating to the chosen area into a seperate dataframe
        dfsingle = df.loc[df['Area'] == area]

        #Set our statistics from the data
        self.upperquartile = dfsingle["Upper quartile"].iloc[0]
        self.lowerquartile = dfsingle["Lower quartile"].iloc[0]
        self.average = dfsingle["Mean"].iloc[0]
        self.pricepp = self.average/self.bed_map[bednumber][1]

        layout = go.Layout(showlegend=True, plot_bgcolor="#ffffff",
                           width=400, height=400, margin=dict(t=10, b=10))
        fig = go.Figure(layout=layout)

        #Add the data trace based on the median pricing and the interquartile range through the use of error bars
        fig.add_trace(go.Scatter(
            x=dfsingle.Area, y=dfsingle.Median,
            mode='markers',
            name='Median Price',
            marker_symbol="line-ew",
            error_y=dict(
                type='constant',
                symmetric=False,
                value=np.array(dfsingle["Upper quartile"])[0],
                valueminus=np.array(dfsingle["Lower quartile"])[0],
                color='Thistle',
                thickness=1.5,
                width=8,
            ),
            marker=dict(color='DarkSlateGrey', size=35,
                        line=dict(color='black', width=5)),
            # Custom text template with £ sign
            text=str("£") + str(np.array(dfsingle.Median)[0])
        ))
        fig.add_trace(go.Scatter(
            x=dfsingle.Area, y=dfsingle.Mean,
            mode='markers',
            name='Mean Price',
            marker_symbol="line-ew-open",
            marker=dict(color='SkyBlue', size=35,
                        line=dict(color='black', width=5)),
            text=[str("£") + str(np.array(dfsingle.Mean)[0])]
        ))
        #Add the upper quartile text with position equal to the quartile marker +10 y-shift
        fig.add_annotation(x=0, y=(dfsingle.Median.iloc[0] + np.array(dfsingle["Upper quartile"])[0]),
                           text="Upper Quartile",
                           showarrow=False,
                           yshift=10,
                           font=dict(
            size=8,
        ),
            opacity=0.5)
        #Add the lower quartile text with position equal to the quartile marker -10 y-shift
        fig.add_annotation(x=0, y=(dfsingle.Median.iloc[0] - np.array(dfsingle["Lower quartile"])[0]),
                           text="Lower Quartile",
                           showarrow=False,
                           yshift=-10,
                           font=dict(
            size=8,
        ),
            opacity=0.5)
        fig.update_yaxes(title_font=dict(size=14, color='#CDCDCD'),
                         tickfont=dict(color='#CDCDCD', size=12), tickprefix="£",
                         showgrid=True, gridwidth=1, gridcolor='#CDCDCD')
        fig.update_xaxes(tickfont=dict(color='#CDCDCD', size=12),
                         showline=True, linewidth=2, linecolor='#CDCDCD')

        return fig

    #Generates the scatter plot for comparing the room sizes and also generates the availability pie chart
    #Takes input of borough name
    def bestpartysize(self, area):
        df = pd.read_excel(
            'statfreak/dashapp/data/privaterentalmarketstatistics11122020.xls', sheet_name='Table2.2', skiprows=6)
        rows = list(range(218, 252))
        rows.remove(219)
        rows.remove(232)
        df = df.iloc[rows, [3]]
        df = df.sort_values('Area', ascending=True)
        df = df.reset_index(drop=True)
        df2 = df.copy()

        for roomsize in self.bed_map:
            dfsample = pd.read_excel('statfreak/dashapp/data/privaterentalmarketstatistics11122020.xls',
                                     sheet_name=self.bed_map[roomsize][0], skiprows=6)
            dfsample = dfsample.iloc[rows, [3, 4, 5]]
            dfsample = dfsample.sort_values('Area', ascending=True)
            dfsample = dfsample.reset_index(drop=True)
            df2[roomsize] = dfsample["Count of rents"]
            df[roomsize] = dfsample["Mean"]/self.bed_map[roomsize][1]

        #Using the selected area we take a slice of that areas data from the main dataframes
        dfsingle = df.loc[df['Area'] == area]
        dfsingle2 = df2.loc[df['Area'] == area]

        #Code for Scatter Plot
        # Find minimum room sizing price for reccomnedation
        best_size = dfsingle.columns[np.argmin(
            dfsingle.iloc[:, list(range(1, 6))])+1]
        self.lowestsize = self.bed_map[best_size][1]
        self.lowestppp = dfsingle[best_size].iloc[0]

        x = ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom", "4+ Bedroom"]
        y = [dfsingle["Studio"].iloc[0], dfsingle["One Bedroom"].iloc[0], dfsingle["Two Bedroom"].iloc[0],
             dfsingle["Three Bedroom"].iloc[0], dfsingle["Four+ Bedroom"].iloc[0]]

        layout = go.Layout(title="Average price per person per room size",
                           showlegend=False, plot_bgcolor="#ffffff", width=400, height=300)
        fig = go.Figure(layout=layout)

        #Plot the scatter plot
        fig.add_trace(go.Scatter(x=x, y=y, name=dfsingle.Area.iloc[0],

                                 line=dict(color='Thistle', width=1.5),
                                 marker=dict(color='skyblue', size=9, opacity=0.8, line=dict(color='black', width=3))))
        fig.update_yaxes(title_font=dict(size=14, color='#CDCDCD'),
                         tickfont=dict(color='#CDCDCD', size=12), tickprefix="£",
                         showgrid=False, gridwidth=1, gridcolor='#CDCDCD')
        fig.update_xaxes(tickfont=dict(color='#CDCDCD', size=12),
                         showline=True, linewidth=2, linecolor='#CDCDCD')

        #Code for pie chart of counts of rent
        vals = [dfsingle2["Studio"].iloc[0], dfsingle2["One Bedroom"].iloc[0], dfsingle2["Two Bedroom"].iloc[0],
                dfsingle2["Three Bedroom"].iloc[0], dfsingle2["Four+ Bedroom"].iloc[0]]
        pull_values = [0, 0, 0, 0, 0]
        colors = ['#ff6666', '#ffcc99', '#99ff99', '#66b3ff', '#c2c2f0']
        text_colour = ["Black", "Black", "Black", "Black", "Black"]

        #Make reccomended size white text and pull slice from pie chart
        text_colour[self.lowestsize] = "White"
        pull_values[self.lowestsize] = 0.1

        #Create the pie chart with our custom layout and also the pulled slice giving it white text so it stands out
        fig2 = go.Figure(data=[go.Pie(labels=x, values=vals, textinfo='label+percent', marker_colors=colors,
                                      textposition='inside', hoverinfo='none', pull=pull_values, textfont={"color": text_colour})])
        fig2.update_layout(title_text='Breakdown of availability of room sizes', plot_bgcolor="#ffffff", showlegend=False, width=470, height=470,
                           margin=dict(t=30, b=0, l=10, r=10))

        return fig, fig2
