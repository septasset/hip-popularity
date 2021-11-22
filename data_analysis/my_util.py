import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

filter_thres = 10

def total_at_no_filter(days, series, vids, accumulate=False):
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
    df_viewcount_eval = total_at_no_filter(days, viewcounts, vids, accumulate)
    
    pop_perc_col = np.linspace(0, 1, len(df_viewcount_eval.index))
    pop_percs = []
    for day in days:
        df_viewcount_sort = df_viewcount_eval.loc[:,[day]].sort_values(by=[day], inplace=False)
        df_viewcount_sort[day] = pop_perc_col
        pop_percs.append(df_viewcount_sort)
    return pop_percs

def total_at(days, series, vids, accumulate=False):
    """ compute total number of a series(views/shares...) at several evaluation days
    :return: a dataframe
    :param accumulate: when false, sum from last day to current day
    """
    series_eval = []
    vids_filter = []
    for i in range(len(series)):
        flag_filter = False
        if accumulate:
            series_accu = [np.sum(series[i][:day]) for day in days]
        else:
            series_accu = []
            for j in range(len(days)):
                if j==0: 
                    eval_sum = np.sum(series[i][:days[j]])
                    eval_avg = eval_sum / days[j]
                else: 
                    eval_sum = np.sum(series[i][days[j-1]:days[j]])
                    eval_avg = eval_sum / (days[j]-days[j-1])
                if eval_avg <= filter_thres:
                    flag_filter = True
                    break
                series_accu.append(eval_sum)
        if not flag_filter:
            series_eval.append(series_accu)
            vids_filter.append(vids[i])
    
    df_series_eval = pd.DataFrame(series_eval, columns =days, index = vids_filter)
    return df_series_eval

def total_log_at(days, series, vids, accumulate=False):
    """ compute total number at log scale of a series(views/shares...) at several evaluation days
    :return: a dataframe
    :param accumulate: when false, sum from last day to current day
    """
    series_eval = []
    vids_filter = []
    for i in range(len(series)):
        flag_filter = False
        if accumulate:
            series_accu = [np.sum(series[i][:day]) for day in days]
        else:
            series_accu = []
            for j in range(len(days)):
                if j==0: 
                    eval_sum = np.sum(series[i][:days[j]])
                    eval_avg = eval_sum / days[j]
                else: 
                    eval_sum = np.sum(series[i][days[j-1]:days[j]])
                    eval_avg = eval_sum / (days[j]-days[j-1])
                if eval_avg <= filter_thres:
                    flag_filter = True
                    break
                series_accu.append(math.log(eval_sum, 10))
        if not flag_filter:
            series_eval.append(series_accu)
            vids_filter.append(vids[i])
    
    df_series_eval = pd.DataFrame(series_eval, columns =days, index = vids_filter)
    return df_series_eval

"""
Plots
"""
def plot_popPerc_totalViews(days, df_total_views, pop_percs_gt):
    """ assume days to be of length 2
    """
    noBins = 40
    bin_width = 1.0 / noBins
    popPerc_eval = [[] for x in range(noBins)]
    for i in range(len(days)):
        total_views_binned = [[] for x in range(noBins)]
        total_views_log_space = [math.log(max(df_total_views.loc[vid, days[i]], 1), 10) for vid in pop_percs_gt[i].index]
        for j in range(len(pop_percs_gt[i][days[i]])):
            pop_perc = pop_percs_gt[i][days[i]][j]
            noBin = min(int(np.floor(pop_perc / bin_width)), noBins-1)
            total_views_binned[noBin].append(total_views_log_space[j])
#             if noBin==39 and total_views_log_space[j]<3.333:
#                 print(pop_perc)
            if i==1:
                vid = (pop_percs_gt[i].index)[j]
                popPerc_eval[noBin].append(pop_percs_gt[0][days[0]].loc[vid])

        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        ax.boxplot(total_views_binned)
        ax.set_ylabel("Log of total views", color="blue")
        ax.set_title("day@{}".format(days[i]), color="blue")
        ax.set_xticks([k*2 for k in range(1, noBins//2+1)])
        ax.set_xticklabels(['{0:.2f}'.format(k*2*bin_width) for k in range(1, noBins//2+1)])
    
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.boxplot(popPerc_eval)
    ax.set_ylabel("Popularity percentile day@{}".format(days[0]), color="blue")
    ax.set_xlabel("Popularity percentile day@{}".format(days[1]), color="blue")
    ax.set_xticks([k*2 for k in range(1, noBins//2+1)])
    ax.set_xticklabels(['{0:.2f}'.format(k*2*bin_width) for k in range(1, noBins//2+1)])
    return total_views_binned
    
def plot_fixed_window(days, df, test_category):    
    data = [dict() for x in days[1:]]
    index = df.index
    
    for i in index:
        for j, d in enumerate(days[1:]):
            short_term = "{:.1f}".format(df.loc[i, days[0]])
            if short_term not in data[j]:
                data[j][short_term]=[]   
            data[j][short_term].append(df.loc[i, d])
                                     
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    lines = []
    for j in range(len(data)):
        xs = [float(x) for x in list(data[j].keys())]
        xs.sort()
        ys = [np.mean(data[j][str(x)]) for x in xs]
        line = ax.plot(xs, ys, label = "{} - {}".format(days[j], days[j+1]))
        lines.append(line)
#         if j == len(data)-1:
#             print(xs[-5:])
#             print([data[j][str(x)] for x in xs][-5:])
    ax.set_ylabel("Long-term average daily views(log)", color="blue", fontsize=16)
    ax.set_xlabel("Short-term average daily views(log)", color="blue", fontsize=16)
    ax.set_title("All of {}({})".format(test_category, len(df.index)), color="blue", fontsize=18)
    ax.legend(fontsize ="xx-large")
    plt.savefig('figs/{}.png'.format(test_category))
    
    
    
    
    
    
    