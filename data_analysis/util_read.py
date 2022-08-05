from __future__ import print_function, division
import os, bz2, json, time, sys, csv
from datetime import timedelta

import math
import numpy as np
import pandas as pd
import matplotlib as mpl

from matplotlib import pyplot as plt
from tqdm import tqdm

def engage_read(category, eval_days = [90, 135, 180, 225, 270]):    
    with open(os.path.join(engage_dataset_base, "{}.json".format(category)), "r") as f:
        dataset_json = f.readlines()
    dataset = {}
    
    vids_set = set()
    for line in tqdm(dataset_json, desc="{} in engage".format(category)):
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