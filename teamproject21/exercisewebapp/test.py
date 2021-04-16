import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json


df= pd.DataFrame(data={'post_id':[1,2], 'group_id':[2,2], 'user_id':[1,2], 'date_posted':['10/12/2021','11/12/2021'], 'reps':[25,50]})

def create_plot(df):

    data = [
        go.Bar(
            x=df['date_posted'], # assign x as the dataframe column 'x'
            y=df['reps']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

