'''Code by Paul Ho'''
import pandas as pd
import numpy as np


class CrimeData:
    """
    Class for retrieving crime data
    """

    def __init__(self):
        self.crimedata = pd.DataFrame()
        self.get_data()
        self.widths = []
        self.crimes_list = []
        self.reduceddata = pd.DataFrame
        self.areas = []
        self.allareas = []

    def get_data(self):
        # Load data
        DATA_DIRECTORY = "Approved_datasets"
        crimeFile = 'statfreak/dashapp/data/MPS Borough Level Crime (most recent 24 months) (1).csv'
        self.crimedata = pd.read_csv(crimeFile, header=0)

    def process_data(self, area1, area2, area3):
        df = self.crimedata
        boroughs = [area1, area2, area3]
        boroughs.sort()
        self.areas = boroughs
        date = "202010"

        # Calculate totals
        df1 = df[df['LookUp_BoroughName'] == boroughs[0]]
        data1 = df1[date]
        total1 = data1.sum()

        df2 = df[df['LookUp_BoroughName'] == boroughs[1]]
        data2 = df2[date]
        total2 = data2.sum()

        df3 = df[df['LookUp_BoroughName'] == boroughs[2]]
        data3 = df3[date]
        total3 = data3.sum()

        # list all areas and store
        arealist = df['LookUp_BoroughName'].drop_duplicates()
        self.allareas = arealist.values.tolist()

        # widths = total number of cases
        self.widths = np.array([total1, total2, total3])

        # convert dataframes into percentages https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.divide.html
        df1[date] = df1[date].truediv(total1)
        df2[date] = df2[date].truediv(total2)
        df3[date] = df3[date].truediv(total3)

        # the data for October 2020 adapted from https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
        frames = [df1, df2, df3]
        data = pd.concat(frames)

        data.set_index(['MajorText', 'MinorText'])
        self.reduceddata = data

        # make a list of all "major" crimes from dataframe
        crimes = data['MajorText'].drop_duplicates()
        self.crimes_list = crimes.values.tolist()
