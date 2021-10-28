'''Code by Paul Ho'''
import plotly.graph_objects as go
import pandas as pd


class WellbeingChart:
    """Create the Wellbeing Radar chart to be used in the dashboard"""

    def __init__(self):
        self.create_radar_chart("Brent", "Camden")
        self.allareas = []

    def create_radar_chart(self, borough1, borough2):
        boroughs = [borough1, borough2]

        wellbeing = 'statfreak/dashapp/data/personal-well-being-borough.xlsx'
        df = pd.read_excel(
            wellbeing, sheet_name='Summary - Mean Scores', skiprows=0, header=[0, 1])
        df2 = df.xs('2018/19', axis=1, level=1, drop_level=False)
        df2.columns = df2.columns.droplevel(level=1)
        areas = df.xs('Area', axis=1, level=1, drop_level=False)
        areas.columns = areas.columns.droplevel(level=0)
        self.allareas = areas["Area"].to_list()

        df3 = pd.concat([areas, df2.reindex(areas.index)], axis=1)
        df3.drop(0)
        df3 = df3[0: 33]
        df3 = df3.set_index("Area")
        categories = df2.columns.to_list()
        
        fig = go.Figure()

        for borough in boroughs:
            fig.add_trace(go.Scatterpolar(
                r=df3.loc[borough].to_list(),
                theta=categories,
                fill='toself',
                name=borough
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True
        )

        return fig
