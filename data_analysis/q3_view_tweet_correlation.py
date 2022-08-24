from __future__ import print_function, division
import os, bz2, json, time, sys, csv
from datetime import timedelta, datetime

import math
import collections
import numpy as np
import pandas as pd
import matplotlib as mpl

from matplotlib import pyplot as plt
from tqdm import tqdm

from util_read import engage_read, read_vids, engage_tweets_read, merge_engage_tweets, engage_metadata, compute_period_daily

import pickle

file_vids_filter_all = "/home/users/u6314203/pyProject/hip-popularity/data/engage16/filtered/vids_filter_all.csv" 
engage_dataset_base = "/localdata/u6314203/dataset_engage16/tweeted_videos" 
tweets_dataset_base = "/localdata/u6314203/dataset_tweets_engage/dataset_tweets_fixTZ"
out_base = "/localdata/u6314203/view_tweet_correlation"

categories_eligible = ["autos", "comedy","education","entertainment", \
                       "film","gaming","howto","music",\
                       "news","people","science","sports",\
                       "travel"]

vids_filter_all = read_vids(file_vids_filter_all)

############################################################################################################################

# merged_dataset = dict()
# for category in categories_eligible[:]:
#     engage_dataset = engage_read(engage_dataset_base, category)
#     tweets_dataset = engage_tweets_read(tweets_dataset_base, category)
    
#     curr_merged = merge_engage_tweets(engage_dataset, tweets_dataset)
#     merged_dataset.update(curr_merged)
    
# print(f"Total size: {len(merged_dataset)}")

# pickle.dump(merged_dataset, open(os.path.join(out_base, "merged_dataset(view_tweet_all_categories)" + ".pik"), "wb"))

# stats = compute_period_daily(merged_dataset)
# pickle.dump(stats, open(os.path.join(out_base, "stats(view_tweet_all_categories)" + ".pik"), "wb"))

############################################################################################################################

merged_dataset = pickle.load(open(os.path.join(out_base, "merged_dataset(view_tweet_all_categories)" + ".pik"), "rb"))
stats = pickle.load(open(os.path.join(out_base, "stats(view_tweet_all_categories)" + ".pik"), "rb"))
print("load completed!")

# plot4
def log_scale(arr_att1, arr_att2):
    arr1 = np.array(arr_att1)
    arr2 = np.array(arr_att2)
    
    arr1[arr1 <= 0] = np.nan
    arr2[np.isnan(arr1)] = np.nan
    
    arr1 = np.log10(arr1)
    return arr1, arr2

fig = plt.figure(figsize=(16, 8))

daily_views_lt, daily_tweets_lt = stats["daily_views_lt"], stats["daily_tweets_lt"]
ax = fig.add_subplot(121)
ax.scatter(daily_views_lt, daily_tweets_lt, s = 6.0)
ax.set_xlabel("daily views (long-term)")
ax.set_ylabel("daily tweets (long-term)")

daily_views_lt_log, daily_tweets_lt = log_scale(daily_views_lt, daily_tweets_lt)
ax = fig.add_subplot(122)
ax.scatter(daily_views_lt_log, daily_tweets_lt, s = 6.0)
ax.set_xlabel("daily views in log scale (long-term)")
ax.set_ylabel("daily tweets (long-term)")

plt.savefig(f"{out_base}/figs/log_views")

# # plot1
# fig = plt.figure(figsize=(16, 16))

# daily_views_lt, daily_shares_lt = stats["daily_views_lt"], stats["daily_shares_lt"]
# ax = fig.add_subplot(221)
# ax.scatter(daily_views_lt, daily_shares_lt, s = 6.0)
# ax.set_xlabel("daily views (long-term)")
# ax.set_ylabel("daily shares (long-term)")

# perc_views_lt, daily_shares_lt = stats["perc_views_lt"], stats["daily_shares_lt"]
# ax = fig.add_subplot(222)
# ax.scatter(perc_views_lt, daily_shares_lt, s = 6.0)
# ax.set_xlabel("views percent (long-term)")
# ax.set_ylabel("daily shares (long-term)")

# daily_views_lt, daily_tweets_lt = stats["daily_views_lt"], stats["daily_tweets_lt"]
# ax = fig.add_subplot(223)
# ax.scatter(daily_views_lt, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("daily views (long-term)")
# ax.set_ylabel("daily tweets (long-term)")

# perc_views_lt, daily_tweets_lt = stats["perc_views_lt"], stats["daily_tweets_lt"]
# ax = fig.add_subplot(224)
# ax.scatter(perc_views_lt, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("views percent (long-term)")
# ax.set_ylabel("daily tweets (long-term)")

# plt.savefig(f"{out_base}/figs/basic")

# # plot2
# def outlier_remove_empirical(arr_att1, arr_att2):
#     arr1 = np.array(arr_att1)
#     arr2 = np.array(arr_att2)
    
#     arr1[arr1 < 0] = np.nan
#     arr1[arr1 > 250000] = np.nan
#     arr2[np.isnan(arr1)] = np.nan
    
#     arr2[arr2 < 0] = np.nan
#     arr2[arr2 > 25] = np.nan
#     arr1[np.isnan(arr2)] = np.nan
#     return arr1, arr2
# fig = plt.figure(figsize=(16, 8))

# daily_views_lt, daily_tweets_lt = stats["daily_views_lt"], stats["daily_tweets_lt"]
# ax = fig.add_subplot(121)
# ax.scatter(daily_views_lt, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("daily views (long-term)")
# ax.set_ylabel("daily tweets (long-term)")

# daily_views_lt, daily_tweets_lt = outlier_remove_empirical(stats["daily_views_lt"], stats["daily_tweets_lt"])
# ax = fig.add_subplot(122)
# ax.scatter(daily_views_lt, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("daily views (long-term) (bottom-left)")
# ax.set_ylabel("daily tweets (long-term) (bottom-left)")

# plt.savefig(f"{out_base}/figs/bottom-left_zoom-in")

# # plot3
# def percentile_views(viewcounts, promotions):
#     n = len(viewcounts)
#     arr = [(viewcounts[i], i) for i in range(n)]
#     arr.sort()
#     views_percentile = [(j+1)/n for j in range(n)]
#     promotions_reordered = [promotions[x[1]] for x in arr]
#     return views_percentile, promotions_reordered
# fig = plt.figure(figsize=(16, 8))

# daily_views_lt, daily_tweets_lt = stats["daily_views_lt"], stats["daily_tweets_lt"]
# ax = fig.add_subplot(121)
# ax.scatter(daily_views_lt, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("daily views (long-term)")
# ax.set_ylabel("daily tweets (long-term)")

# views_percentile, daily_tweets_lt = percentile_views(stats["daily_views_lt"], stats["daily_tweets_lt"])
# ax = fig.add_subplot(122)
# ax.scatter(views_percentile, daily_tweets_lt, s = 6.0)
# ax.set_xlabel("views percentile (long-term)")
# ax.set_ylabel("daily tweets (long-term)")

# plt.savefig(f"{out_base}/figs/percentile")
