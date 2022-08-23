from __future__ import print_function, division
import os, bz2, json, time, sys, csv
from datetime import timedelta, datetime

import math
import numpy as np
import pandas as pd
import matplotlib as mpl

from matplotlib import pyplot as plt
from tqdm import tqdm

def engage_read(engage_dataset_base, category, eval_days = [90, 135, 180, 225, 270]):    
    with open(os.path.join(engage_dataset_base, "{}.json".format(category)), "r") as f:
        dataset_json = f.readlines()
    dataset = {}
    
    vids_set = set()
    for line in dataset_json:
        record = json.loads(line)
        try:        
            day = [int(x) for x in record['insights']['days'].split(",")]                        
            if len(day) < eval_days[-1]: # filter out videos of short history
                continue                
            vals = {
                "day_zero": record['insights']['startDate'], 
                "days": day, 
                "viewCounts": [int(x) for x in record['insights']['dailyView'].split(",")],
                "shares": [int(x) for x in record['insights']['dailyShare'].split(",")],
            }
        except:
            continue
        dataset[record['id']] = vals
        
        if record['id'] in vids_set: 
            continue
        else: 
            vids_set.add(record['id'])
    print("Engage {} size: {}".format(category, len(dataset.keys())))
    return dataset

def engage_tweets_read(tweets_dataset_base, test_category):
    with open(os.path.join(tweets_dataset_base, test_category+".json"), "r") as f:
        dataset_json = f.readlines()
        
    dataset = json.loads(dataset_json[0])
    print(f"Tweets {test_category} size: {len(dataset.keys())}")
    return dataset

def read_vids(inpath):
    res = dict()
    with open(inpath, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row)==0: continue
            category = row[0]
            vids = row[1:]
            res[category] = vids
    
    report = []
    for cat, vids in res.items():
        report.append(f"{cat}:{len(vids)}")
    print("Vids(filtered) in each category:\n"+"; ".join(report))
    return res

def merge_engage_tweets(engage_dataset, tweets_dataset):
    merged_dataset = dict()
    for key, vals in engage_dataset.items():
        if key not in tweets_dataset:
            continue
        day_zero, days, viewCounts, shares = vals["day_zero"], vals["days"], vals["viewCounts"], vals["shares"]        
        dz, ds, tweets = tweets_dataset[key]["day_zero"], tweets_dataset[key]["days"], tweets_dataset[key]["tweets"]
        dz_diff = (datetime.strptime(day_zero, "%Y-%m-%d") - datetime.strptime(dz, "%Y-%m-%d")).days
        
        new_days, new_viewCounts, new_shares, new_tweets = [], [], [], []
        p1, p2 = 0, 0
        for d in range(days[-1]+1):
            while p1 < len(days) and days[p1] < d:
                p1 += 1
            while p2 < len(ds) and ds[p2]-dz_diff < d:
                p2 += 1
            if (p1 < len(days) and days[p1] == d) | (p2 < len(ds) and ds[p2]-dz_diff == d):
                new_days.append(d)
                if p1 < len(days) and days[p1] == d:
                    new_viewCounts.append(viewCounts[p1])
                    new_shares.append(shares[p1])
                else:
                    new_viewCounts.append(0)
                    new_shares.append(0)
                if p2 < len(ds) and ds[p2]-dz_diff == d:
                    new_tweets.append(tweets[p2])
                else:
                    new_tweets.append(0)
        
        merged_dataset[key] = {
            "day_zero": day_zero, 
            "days": new_days, 
            "viewCounts": new_viewCounts,
            "shares": new_shares,
            "tweets": new_tweets,
        }        
    
    print(f"Merged size: {len(merged_dataset.keys())}")
    return merged_dataset

def engage_metadata(engage_dataset_base, category, eval_days = [90, 135, 180, 225, 270]):    
    with open(os.path.join(engage_dataset_base, "{}.json".format(category)), "r") as f:
        dataset_json = f.readlines()
    dataset = {}
    
    vids_set = set()
    for line in dataset_json:
        record = json.loads(line)
        try:        
            day = [int(x) for x in record['insights']['days'].split(",")]                        
            if len(day) < eval_days[-1]: # filter out videos of short history
                continue                
            vals = {
                "title": record['snippet']['title'], 
                "channelTitle": record['snippet']['channelTitle'], 
                "categoryId": record['snippet']['categoryId'],
                "detectLang": record['snippet']['detectLang'],
#                 "description": record['snippet']['description'],
            }
        except:
            continue
        dataset[record['id']] = vals
        
        if record['id'] in vids_set: 
            continue
        else: 
            vids_set.add(record['id'])
#     print("Engage {} size: {}".format(category, len(dataset.keys())))
    return dataset

def compute_period_daily(merged_dataset, timepoint = 90):
    stats = {
        "vids": [],
        "daily_views": [], "daily_shares": [], "daily_tweets": [],
        "daily_views_st": [], "daily_views_lt": [],
        "daily_shares_st": [], "daily_shares_lt": [],
        "daily_tweets_st": [], "daily_tweets_lt": [],
        "perc_views_lt": [], 
    }
    
    for vid, vals in merged_dataset.items():
        days = vals["days"]
        left, right = 0, len(days) - 1
        while left <= right:
            mid = (left+right)//2
            if mid <= 90:
                left = mid + 1
            else:
                right = mid - 1
        
        stats["vids"].append(vid)
        stats["daily_views"].append(np.mean(vals["viewCounts"]))
        stats["daily_shares"].append(np.mean(vals["shares"]))
        stats["daily_tweets"].append(np.mean(vals["tweets"]))
        stats["daily_views_st"].append(np.mean(vals["viewCounts"][:left]))
        stats["daily_views_lt"].append(np.mean(vals["viewCounts"][left:]))
        stats["daily_shares_st"].append(np.mean(vals["shares"][:left]))
        stats["daily_shares_lt"].append(np.mean(vals["shares"][left:]))
        stats["daily_tweets_st"].append(np.mean(vals["tweets"][:left]))
        stats["daily_tweets_lt"].append(np.mean(vals["tweets"][left:]))
        stats["perc_views_lt"].append(np.sum(vals["viewCounts"][left:])/np.sum(vals["viewCounts"]))

    return stats