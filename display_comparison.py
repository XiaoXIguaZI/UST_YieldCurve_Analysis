# Please run each cell, the result will be under output/merge


#%% Import python packages & functions
# magic %reset resets by erasing variables, etc. 

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.io as pio
pio.renderers.default='svg'
pio.renderers.default='browser'
import importlib as imp
import time as time

import DateFunctions_1 as dates
import discfact as df
imp.reload(dates)
imp.reload(df)





#%% Merge Python & Fortran curves
'''
Comparison list:
1. opt_NormY_est_OTR vs opt_LnY_est_OTR [2000, 1987][pwcf, pwtf]
2. opt_NormY_est_OTR vs opt_SqrtY_est_OTR [2000, 1987][pwcf, pwtf]
3. opt_NormY_est_OTR vs YTW_OTR [1987][pwcf, pwtf]
4. pycurve vs YTW_OTR [1987][pwcf, mix]
5. pycurve vs YTW_forb [2000][pwcf]
6. YTW_newb vs YTW_OTR [1987][pwcf, pwtf]
7. YTW_OTR vs opt_LnY_est_OTR [1987][pwcf, pwtf]


'''

# Define path
OUTPUT_DIR = 'output'
estpythfile = 'test1987opt_LnY_est_OTR'
pythlab = '1987opt_LnY_est_OTR'
estfortdir = 'test1987YTW_OTR'
estfortfile = 'test1987YTW_OTR'
fortlab ='1987YTW_OTR'

# Read in data
df_curve_python = pd.read_pickle(os.path.join(OUTPUT_DIR, estpythfile, f'{estpythfile}_curve.pkl'))
df_curve_fortran = pd.read_pickle(os.path.join(OUTPUT_DIR, estfortdir, f'{estfortfile}_curve.pkl'))


# Add new index and columns to define py_fort
def add_coding_index(df, coding):
    
    df['coding'] = coding  # add column
    df = df.set_index(pd.Index([coding] * len(df), name='output_ind'), append=True)  # add index
    df['pair_ind'] = df.index.get_level_values('output_ind') + ', ' + df.index.get_level_values('type_ind')
    df['pair'] = df['pair_ind']
    df = df.set_index('pair_ind', append=True)
    return df.reorder_levels(['output_ind', 'type_ind', 'pair_ind', 'quotedate_ind'])  # adjust priority levels


df_curve_python = add_coding_index(df_curve_python, pythlab)
df_curve_fortran = add_coding_index(df_curve_fortran, fortlab)

# Merge dataset
df_curve_merge = pd.concat([df_curve_python, df_curve_fortran], axis=0, join='outer')

# Generate .pkl & .csv
merge_dir = os.path.join(OUTPUT_DIR, 'merge')
os.makedirs(merge_dir, exist_ok=True)


# df_curve_merge.to_pickle(os.path.join(merge_dir, 'merge.pkl'))
# df_curve_merge.to_csv(os.path.join(merge_dir, 'merge.csv'), index=False)

# Check for index level
# df_curve_merge.index.get_level_values('pair_ind').unique()

# Check for missing data
# df_curve_merge.xs(20000131, level='quotedate_ind')






#%%  Graphing function for comparing two curve types

def plot_fwdrate_wrapper(output_dir, estfile, curve_df, curve_comparisons, plot_points_yr, taxflag=False, sqrtscale=False, yield_to_worst=True, start_date=None, end_date=None, pltshow=False):
    """Plot and export to png in created folders for each curve comparison."""
    
    # curve_df = df_curve_merge
    # output_dir = OUTPUT_DIR
    # Filter dates
    if start_date is not None and end_date is not None:
        curve_df = curve_df.loc[(curve_df.index.get_level_values('quotedate_ind') >= start_date) &
                                (curve_df.index.get_level_values('quotedate_ind') <= end_date)]
    
    # Call max_min function
    curve_df = find_max_min_fwd_rate(curve_df)

    # Set drawing points in days
    curve_points_day = plot_points_yr * 365.25
    
    # Loop through the comparison sets to create file path
    for curve_comparison in curve_comparisons:
        comparison_name_1 = '_'.join(curve_comparison).replace(', ', '_')
        comparison_name_2 = ' VS '.join([item.replace(', ', '_') for item in curve_comparison])
        path = f"{output_dir}/{estfile}/{comparison_name_1}"
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created")

        #  Loop through quotedate to print figures
        for date in curve_df.index.get_level_values('quotedate_ind').unique():
            julian_date = dates.YMDtoJulian(date) 
            plot_points = julian_date + curve_points_day
            try:
                curves_all = curve_df.xs(date, level='quotedate_ind')
            except KeyError:
                print(f"Skipping {date}: data not available")
                continue
            
            plt.figure()

            for comparison_pair in curve_comparison:

                xcurvedf = curves_all[curves_all.index.get_level_values('pair_ind') == comparison_pair]
                y_max = xcurvedf.reset_index(drop=True)['max_5yr'].iloc[0]
                y_min = xcurvedf.reset_index(drop=True)['min_5yr'].iloc[0]

                
                curve = xcurvedf.reset_index(drop=True).iloc[0].iloc[:4]
            
                # Calculate yield using discount factor
                term1 = df.discFact(plot_points + 1, curve)
                term2 = df.discFact(plot_points, curve)
                result = -365 * np.log(term1 / term2)

                if sqrtscale:
                    plt.plot(np.sqrt(plot_points_yr), 100 * result, label=f'{comparison_pair} - {date}')
                else:
                    plt.plot(plot_points_yr, 100 * result, label=f'{comparison_pair} - {date}')
                
                
            plt.ylim(y_min * 100 - 0.8 * abs(y_min * 100), y_max * 100 + 0.1 * abs(y_max * 100))
            
            # Set x-axis: sqrt root ticks and labeling
            if sqrtscale:
                x1 = max(plot_points_yr)
                if x1 > 20:
                    plt.xticks(ticks=np.sqrt([0.25, 1, 2, 5, 10, 20, 30]), labels=['0.25', '1', '2', '5', '10', '20', '30'])
                elif x1 > 10:
                    plt.xticks(ticks=np.sqrt([0.25, 1, 2, 5, 10, 20]), labels=['0.25', '1', '2', '5', '10', '20'])
                elif x1 > 5:
                    plt.xticks(ticks=np.sqrt([0.25, 1, 2, 5, 7, 10]), labels=['0.25', '1', '2', '5', '7', '10'])
                else:
                    plt.xticks(ticks=np.sqrt([0.25, 1, 2, 3, 5]), labels=['0.25', '1', '2', '3', '5'])
                plt.xlabel('Maturity (Years, SqrRt Scale)')
            else:
                plt.xlabel('Maturity (Years)')
            
            # Set title, label, and grid
            plt.title(f'Forward Rates for {comparison_name_2} on {date}')
            plt.ylabel('Rate')
            plt.legend()
            plt.grid(True)
            
            # Save the plot
            full_path = os.path.join(path, f'{date}_fwd_{comparison_name_1}.png')
            plt.savefig(full_path)
            if pltshow:
                plt.show()
            plt.close()



# Utility function for finding max and min during 5 yr period
def find_max_min_fwd_rate(curve_df):

    curve_df = curve_df.reset_index()
    curve_df['quotedate_ind'] = curve_df['quotedate_ind'].astype(int).astype(str)
    curve_df['year'] = pd.to_datetime(curve_df['quotedate_ind'], format='%Y%m%d').dt.year
    curve_df['5_year_bin'] = (curve_df['year'] // 5) * 5

    # Extract the max and min from the rates
    curve_df['max_rate'] = curve_df['rates'].apply(lambda x: max(x))
    curve_df['min_rate'] = curve_df['rates'].apply(lambda x: min(x))
    
    # Calculate 5-year rolling max and min for each ctype group
    curve_df['max_5yr'] = curve_df.groupby(['type_ind', 'output_ind', '5_year_bin'])['max_rate'].transform('max')
    curve_df['min_5yr'] = curve_df.groupby(['type_ind', 'output_ind', '5_year_bin'])['min_rate'].transform('min')

    curve_df = curve_df.drop(['year'], axis=1)
    curve_df['quotedate_ind'] = curve_df['quotedate_ind'].astype(int)
    curve_df.set_index(['output_ind', 'type_ind','pair_ind', 'quotedate_ind'], inplace=True, drop=True)

    return curve_df



#%% Main script - Define user inputs and create plots 
### Be consistent with the inputs in calcFwds.py when running each estimation

### Option-related inputs - THESE SHOULD BE TAKEN FROM THE CURVE FILE
yield_to_worst = False # if True, ignore yvolsflg, yvols, opt_type; if False - w/ opt & est calls
yvolsflg = False  # if True - est yvols; if False - must give a reasonale yvols and will not estimate yvols
yvols = 0.35  # set the reasonable start for option vol, LnY, NormY, LnP should be around 0.35, 0.01, 0.06 - Too small will fail; or as the starting value for yvols estimation
opt_type="LnY"  # The value of opt_type must be LnY, NormY, SqrtY or LnP


## Other inputs
tax = False   # if False - no tax; if True - estimate all bonds with their taxability
calltype = 0  # 0 to keep all bonds, 1 for callable bonds, 2 for non-callable bonds
curvetypes =  ['pwcf','pwtf']  # ['pwcf', 'pwlz', 'pwtf'] 
wgttype = 1
lam1 = 1
lam2 = 2
sqrtscale = True
durscale = False
twostep = False
parmflag = True
padj = False
padjparm = 0
fortran = False  # True - if for displaying the FORTRAN results, else defaults to Python
pltshow = False  # Flag to control whether to show plots on interactive screen


## Breaks
base_breaks = np.array([round(7/365.25,4), round(14/365.25,4), round(35/365.25,4), 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])  # 0.0833,
base_breaks = np.array([round(7/365.25,4), round(14/365.25,4), round(21/365.25,4), round(28/365.25,4),
                        round(35/365.25,4), 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])
table_breaks_yr = np.array([0.0833, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])  


## Plot points
curve_points_yr1 = np.arange(.01,4,.01)
curve_points_yr2 = np.arange(4.01,32,.01)
curve_points_yr3 = np.arange(0,32,.01)

plot_points_yr = np.arange(.01,30,.01)
plot_points_yr = np.arange(0,32,.01)  # np.arange(.01,4,.01), np.arange(4.01,32,.01)
plot_points_yr = np.round(np.arange(.01,30,.01)*365.25) / 365.25
plot_points_yr = np.concatenate((np.arange(0, 2, 1/365.25), 
                                 np.arange(2, 5, 0.01), 
                                 np.arange(5, 30, 0.02)))


## Additional report inputs
# ctype = 'pwtf'  # or False, for displaying in the report
ctype = 'pwcf'  # or False, for displaying in the report
tax = False
padjparm = None
date = 20240924  # The date when the curve estimation is run, not when the reports are made



#%%  Create forward curve animation

# Import fwd curve
estfile = 'merge'
df_curve = df_curve_merge

# Start and end date
start_date = 19870101
end_date =   19880101
# start_date = 20000101
# end_date =   20010101

# Comparison
# outputtypes = [fortlab,pythlab]
# curvetypes = ['pwcf', 'pwtf']
curve_comparisons = [['1987opt_LnY_est_OTR, pwtf', '1987YTW_OTR, pwtf'], ['1987opt_LnY_est_OTR, pwcf', '1987YTW_OTR, pwcf']]
plot_fwdrate_wrapper(OUTPUT_DIR, estfile, df_curve_merge, curve_comparisons, plot_points_yr, False, sqrtscale, yield_to_worst, start_date, end_date, pltshow=pltshow)







#%% Now merge the two dataframes and, modify (and make a new version for) the 'plot_fwdrate_wrapper' and create the new graphs

# The gaol is 
#  1) Merge the two dataframes (python curves and fortran curves) with a new index to spcify fortran vs python curve
#  2) modify (and make a new function) for 'plot_fwdrate_wrapper' which will plot a fortran and python curve on the same graph
#  3) Write out the new graphs, but to a new directory under 'output' so that you do not overwrite the original graphs







# %%
