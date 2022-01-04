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

def area_between_scatter_lines(line1, line2, xs):
    """
    """
    area = 0
    for i in range(len(line1)-1):
        dots1 = line1[i:i+2]
        dots2 = line2[i:i+2]
        distance = xs[i+1] - xs[i]
        area += 0.5*((dots1[0]-dots2[0])+(dots1[1]-dots2[1]))*distance
    return abs(area)

"""
Plots
"""
def plot_popPerc_totalViews(days, df_total_views, pop_percs_gt, fig):
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
        
    ax = fig.add_subplot(111)
    ax.boxplot(popPerc_eval)
    ax.set_ylabel("Popularity percentile day@{}".format(days[0]), color="blue")
    ax.set_xlabel("Popularity percentile day@{}".format(days[1]), color="blue")
    ax.set_xticks([k*2 for k in range(1, noBins//2+1)])
    ax.set_xticklabels(['{0:.2f}'.format(k*2*bin_width) for k in range(1, noBins//2+1)])
    return total_views_binned
    
def plot_fixed_window(days, df, test_category, fig, title, average_daily = True):
    """
    :return: (vids-in-each-bin, xs, yss)
    """
    by = "average-daily" if average_daily else "period-total"    
    index = df.index
    
    data = [dict() for x in days[1:]]
    res = dict()
    
    for i in index:
        if average_daily:
            short_term = "{:.1f}".format(df.loc[i, days[0]] - math.log(days[0], 10))
        else:
            short_term = "{:.1f}".format(df.loc[i, days[0]])        
        for j, d in enumerate(days[1:]):
            if average_daily:
                long_term = df.loc[i, d] - math.log(days[j+1]-days[j], 10)
            else:
                long_term = df.loc[i, d]
                
            if short_term not in data[j]:
                data[j][short_term]=[]
            data[j][short_term].append(long_term)
        if float(short_term) not in res:
            res[float(short_term)] = []
        res[float(short_term)].append(i)
                                         
    ax = fig.add_subplot(111)
    lines = []
    xs = [float(x) for x in list(data[0].keys())]
    xs.sort()
    
    yss = []
    for j in range(len(data)):
        ys = [np.mean(data[j][str(x)]) for x in xs]
        yss.append(ys)
        line = ax.plot(xs, ys, label = "{} - {}".format(days[j], days[j+1]))
        lines.append(line)

    ax.set_ylabel("Long-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_xlabel("Short-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_title(title, color="blue", fontsize=18)
    ax.legend(fontsize ="xx-large")    
    ax.plot(xs, xs, color="grey", linestyle="--", linewidth=1)
    
    xs_count = [len(data[0][str(x)]) for x in xs]
    ax2 = ax.twinx()
    ax2.plot(xs, xs_count, color="violet", linestyle="-.")
    ax2.set_ylabel("#Videos in Short-term bin", color="violet", fontsize=16)
    
    ax.set_yticks(np.linspace(np.floor(ax.get_ybound()[0]), np.ceil(ax.get_ybound()[1]), \
                         1+int(np.ceil(ax.get_ybound()[1]) - np.floor(ax.get_ybound()[0]))))
    ax2.set_ylim(0, ax2.get_ylim()[1])
    new_y = np.linspace(0, ax2.get_yticks()[-1], ax.get_yticks().size)
    new_y = np.linspace(0, new_y[1], 6).tolist() + new_y.tolist()[1:]
    ax2.set_yticks(new_y)
    ax.grid(which="both", color="silver", linestyle="--", linewidth=1)
    
    return res, xs, yss
   
"""Modified from plot_fixed_window"""
def plot_fixed_window_double_log(days, df, test_category, fig, title, average_daily = True):
    """
    :return: (vids-in-each-bin, xs, yss)
    """
    by = "average-daily" if average_daily else "period-total"    
    index = df.index
    
    data = [dict() for x in days[1:]]
    res = dict()
    
    for i in index:
        if average_daily:
            short_term = "{:.1f}".format(df.loc[i, days[0]] - math.log(days[0], 10))
        else:
            short_term = "{:.1f}".format(df.loc[i, days[0]])        
        for j, d in enumerate(days[1:]):
            if average_daily:
                long_term = df.loc[i, d] - math.log(days[j+1]-days[j], 10)
            else:
                long_term = df.loc[i, d]
                
            if short_term not in data[j]:
                data[j][short_term]=[]
            data[j][short_term].append(long_term)
        if float(short_term) not in res:
            res[float(short_term)] = []
        res[float(short_term)].append(i)
                                         
    ax = fig.add_subplot(111)
    lines = []
    xs = [float(x) for x in list(data[0].keys())]
    xs.sort()
    
    yss = []
    for j in range(len(data)):
        ys = [np.mean(data[j][str(x)]) for x in xs]
        yss.append(ys)
        line = ax.plot(xs, ys, label = "{} - {}".format(days[j], days[j+1]))
        lines.append(line)

    ax.set_ylabel("Long-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_xlabel("Short-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_title(title, color="blue", fontsize=18)
    ax.legend(fontsize ="xx-large")    
    ax.plot(xs, xs, color="grey", linestyle="--", linewidth=1)
    
    xs_count = [len(data[0][str(x)]) for x in xs]
    ax2 = ax.twinx()
    ax2.plot(xs, [math.log(count, 10) for count in xs_count], color="violet", linestyle="-.")
    ax2.set_ylabel("#Videos in Short-term bin", color="violet", fontsize=16)
    
    ax.set_yticks(np.linspace(np.floor(ax.get_ybound()[0]), np.ceil(ax.get_ybound()[1]), \
                         1+int(np.ceil(ax.get_ybound()[1]) - np.floor(ax.get_ybound()[0]))))
    ax2.set_ylim(0, ax2.get_ylim()[1])
    new_y = np.linspace(0, ax2.get_yticks()[-1], ax.get_yticks().size)
    new_y = np.linspace(0, new_y[1], 6).tolist() + new_y.tolist()[1:]
    ax2.set_yticks(new_y)
    ax.grid(which="both", color="silver", linestyle="--", linewidth=1)
    
    return res, xs, yss
    
def plot_fixed_window_bin_smooth(days, df, test_category, fig, title, average_daily = True, smooth_times = 1):
    """
    :param smooth_times: 1 means 0.1
    :return: (vids-in-each-bin, yss)
    """
    tmpt = [[], []]
    by = "average-daily" if average_daily else "period-total"    
    index = df.index
    
    data = [dict() for x in days[1:]]
    res = dict()
    
    for i in index:
        if average_daily:
            short_term = df.loc[i, days[0]] - math.log(days[0], 10)
        else:
            short_term = df.loc[i, days[0]]
            
        # bin smooth           
        scale = 0.1*smooth_times
        short_term_float = (short_term // (scale)) * scale
        short_term = "{:.1f}".format(short_term_float)
            
        for j, d in enumerate(days[1:]):
            if average_daily:
                long_term = df.loc[i, d] - math.log(days[j+1]-days[j], 10)
            else:
                long_term = df.loc[i, d]
                
            if short_term not in data[j]:
                data[j][short_term]=[]
            data[j][short_term].append(long_term)
        if float(short_term) not in res:
            res[float(short_term)] = []
        res[float(short_term)].append(i)
                                         
    ax = fig.add_subplot(111)
    lines = []
    xs = [float(x) for x in list(data[0].keys())]
    xs.sort()
        
    yss = []    
    for j in range(len(data)):
        ys = [np.mean(data[j][str(x)]) for x in xs]
        yss.append(ys)
        line = ax.plot(xs, ys, label = "{} - {}".format(days[j], days[j+1]))
        lines.append(line)

    ax.set_ylabel("Long-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_xlabel("Short-term {} views(log)".format(by), color="blue", fontsize=16)
    ax.set_title(title, color="blue", fontsize=18)
    ax.legend(fontsize ="xx-large")    
    ax.plot(xs, xs, color="grey", linestyle="--", linewidth=1)
    
    xs_count = [len(data[0][str(x)]) for x in xs]
    ax2 = ax.twinx()
    ax2.plot(xs, xs_count, color="violet", linestyle="-.")
    ax2.set_ylabel("#Videos in Short-term bin", color="violet", fontsize=16)
    
    ax.set_yticks(np.linspace(np.floor(ax.get_ybound()[0]), np.ceil(ax.get_ybound()[1]), \
                         1+int(np.ceil(ax.get_ybound()[1]) - np.floor(ax.get_ybound()[0]))))
    ax2.set_ylim(0, ax2.get_ylim()[1])
    new_y = np.linspace(0, ax2.get_yticks()[-1], ax.get_yticks().size)
    new_y = np.linspace(0, new_y[1], 6).tolist() + new_y.tolist()[1:]
    ax2.set_yticks(new_y)
    ax.grid(which="both", color="silver", linestyle="--", linewidth=1)
    
    return res, xs, yss 
    
        