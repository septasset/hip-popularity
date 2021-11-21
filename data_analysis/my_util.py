import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def total_at(days, series, vids, accumulate=True):
    """ compute total number of a series(views/shares...) at several evaluation days
    :return: a dataframe
    :param accumulate: when false, sum from last day to current day
    """
    series_eval = []
    for i in range(len(series)):
        if accumulate:
            series_accu = [np.sum(series[i][:day]) for day in days]
        else:
            series_accu = []
            for j in range(len(days)):
                if j==0: series_accu.append(np.sum(series[i][:days[j]]))
                else: series_accu.append(np.sum(series[i][days[j-1]:days[j]]))        
        series_eval.append(series_accu)
    
    df_series_eval = pd.DataFrame(series_eval, columns =days, index = vids)
    return df_series_eval

def pop_perc_at(days, viewcounts, vids, accumulate=True):
    """ compute popularity percentile for a series at several evaluation days
    :param days: list, time points(from day 0) to chop and compute popularity percentile 
    :param viewcounts: list, viewcount history for multiple videos
    :param accumulate: when false, sum from last day to current day
    :return: list of dataframe
    """
    df_viewcount_eval = total_at(days, viewcounts, vids, accumulate)
    
    pop_perc_col = np.linspace(0, 1, len(df_viewcount_eval.index))
    pop_percs = []
    for day in days:
        df_viewcount_sort = df_viewcount_eval.loc[:,[day]].sort_values(by=[day], inplace=False)
        df_viewcount_sort[day] = pop_perc_col
        pop_percs.append(df_viewcount_sort)
    return pop_percs

"""
Plots
"""
noBins = 40
def plot_popPerc_totalViews(days, df_total_views, pop_percs_gt):
    """
    return pop_perc@days[1] in the bin of pop_perc@days[0]
    """
    bin_width = 1.0 / noBins
    popPerc_eval = [[] for x in range(noBins)]
    for i in range(len(days)):
        total_views_binned = [[] for x in range(noBins)]
        total_views_log_space = [math.log(max(df_total_views.loc[vid, days[i]], 1), 10) for vid in pop_percs_gt[i].index]
        for j in range(len(pop_percs_gt[i][days[i]])):
            pop_perc = pop_percs_gt[i][days[i]][j]
            noBin = min(int(np.floor(pop_perc / bin_width)), noBins-1)
            total_views_binned[noBin].append(total_views_log_space[j])
            if i==1:
                vid = (pop_percs_gt[i].index)[j]
                popPerc_eval[noBin].append(pop_percs_gt[0][days[0]].loc[vid])

        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        ax.boxplot(total_views_binned)
        ax.set_ylabel("Total views(log)", color="blue")
        ax.set_title("day@{}".format(days[i]), color="blue")
        ax.set_xticks([k*2 for k in range(1, noBins//2+1)])
        ax.set_xticklabels(['{0:.2f}'.format(k*2*bin_width) for k in range(1, noBins//2+1)])
        if i == len(days)-1:
            ax.set_xlabel("Popularity percentile", color="blue")
    return total_views_binned, popPerc_eval

def plot_popPerc_totalViews_Tvs2T(days, popPerc_eval):
    bin_width = 1.0 / noBins
    
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.boxplot(popPerc_eval)
    ax.set_ylabel("Popularity percentile day@{}".format(days[0]), color="blue")
    ax.set_xlabel("Popularity percentile day@{}".format(days[1]), color="blue")
    ax.set_xticks([k*2 for k in range(1, noBins//2+1)])
    ax.set_xticklabels(['{0:.2f}'.format(k*2*bin_width) for k in range(1, noBins//2+1)])
    

    
    
    
    
    
    
    