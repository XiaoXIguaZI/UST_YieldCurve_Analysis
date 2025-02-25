

#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.io as pio
import plotly.graph_objs as go
pio.renderers.default='svg'
pio.renderers.default='browser'
import importlib as imp
import time as time

import DateFunctions_1 as dates
import discfact as df
imp.reload(dates)
imp.reload(df)

OUTPUT_DIR = 'data'
LAB = 'parbd_rate'
df = pd.read_csv(os.path.join(OUTPUT_DIR, f'{LAB}.csv'))




# %%
# def pull_timeseries(df, ctype_value, lab):

#     df['quotedate'] = df['quotedate'].astype(int).astype(str)
#     df['quotedate'] = pd.to_datetime(df['quotedate'], format='%Y%m%d')
#     filtered_df = df[df['ctype'] == ctype_value]

#     output_dir = 'output/time_series'
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    

    
#     maturities = ['10.0YR', '30.0YR']
#     for maturity in maturities:
#         plt.plot(filtered_df['quotedate'], filtered_df[maturity], label=maturity)

#     plt.title(f'Time Series: {lab}, {ctype_value}')
#     plt.xlabel('Quotedate')
#     plt.ylabel('Values')

#     plt.grid(True)
#     plt.gca().set_xscale('linear')
#     plt.gca().set_yscale('linear')

#     date_format = DateFormatter("%Y-%m-%d")
#     plt.gca().xaxis.set_major_formatter(date_format)
    
#     plt.xticks(rotation=45)
#     plt.legend()
#     plt.tight_layout()
    
#     output_path = os.path.join(output_dir, f'{lab}_10&30.png')
#     plt.savefig(output_path)

#     plt.show()
#     plt.close()



def pull_timeseries(df, ctype_value, lab):
    
    df['quotedate'] = df['quotedate'].astype(int).astype(str)
    df['quotedate'] = pd.to_datetime(df['quotedate'], format='%Y%m%d')
    filtered_df = df[df['ctype'] == ctype_value]
    
    output_dir = 'output/time_series'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # maturities = ['2.0YR', '5.0YR', '10.0YR', '30.0YR']
    maturities = df.columns[2:13].tolist()
    fig = go.Figure()

    for maturity in maturities:
        maturity = str(maturity)
        fig.add_trace(go.Scatter(
            x=filtered_df['quotedate'],
            y=filtered_df[maturity],
            mode='lines+markers',
            name=maturity,
            hovertemplate='%{x|%Y-%m-%d}<br>Value: %{y:.2f}'
        ))

    fig.update_layout(
        title=f'Time Series: {lab}, {ctype_value}',
        xaxis_title='Quotedate',
        yaxis_title='Values',
        xaxis=dict(rangeslider=dict(visible=True)),
        yaxis=dict(fixedrange=False)
    )

    output_path = os.path.join(output_dir, f'{lab}_all.html')
    fig.write_html(output_path)  # html
    fig.show()




# %%
ctype_value = 'pwcf'
pull_timeseries(df, ctype_value, LAB)

# %%
