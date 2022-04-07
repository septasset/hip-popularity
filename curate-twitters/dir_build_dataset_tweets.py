import bz2, os, sys, glob
import json, csv, re, datetime
import pickle
from joblib import Parallel, delayed
from tqdm import tqdm

import argparse

from dir_dump_daily_tweets import dirtodir_read_dump

def read_vids(inpath):
    res = dict()
    with open(inpath, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row)==0: continue
            category = row[0]
            vids = row[1:]
            res[category] = set(vids)
    return res

def find_category(vid, map_category_vids):
    for cat, vid_set in map_category_vids.items():
        if vid in vid_set:
            return cat
    return None

def build_dataset(indir, outdir, vids_path):
    dataset = dict()
    
    # engage vids
    map_category_vids = read_vids(vids_path)
    # whether videos in engage dataset
    num_not_in_engage = 0
    total = 0
    
    # files sorted by date ascending
    daily_tweets_files = glob.glob(indir + "/*.pik")
    daily_tweets_files.sort(key=lambda x:datetime.datetime.strptime(os.path.split(x)[1].split(".")[0], "%Y-%m-%d"))
    
    for infile in tqdm(daily_tweets_files, desc="daily tweets files"):
        date_str = os.path.split(infile)[1].split(".")[0]
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        date_aligned = date - datetime.timedelta(days=1)
        
        daily_tweets = pickle.load(open(infile, "rb"))
        for vid, tweetCounts in daily_tweets.items():
            total += 1
            cat = find_category(vid, map_category_vids) 
            if cat is None: 
                num_not_in_engage += 1
                continue                
            if cat not in dataset:
                dataset[cat] = dict()
                
            if vid not in dataset[cat]:
                dataset[cat][vid] = {
                    "day_zero": date_aligned.strftime("%Y-%m-%d"),
                    "days": [0],
                    "tweets": [tweetCounts]
                }
            else:
                offset_day = (date_aligned - datetime.datetime.strptime(dataset[cat][vid]["day_zero"], "%Y-%m-%d")).days
                dataset[cat][vid]["days"].append(offset_day)
                dataset[cat][vid]["tweets"].append(tweetCounts)
    
    # write to disk
    for category, data in tqdm(dataset.items(), desc="Write dataset"):       
        outfile = os.path.join(outdir, "{}.json".format(category))
        with open(outfile, "w") as f:
            json.dump(data, f)

if __name__ == "__main__":
    """Example
    indir           = "/data4/u5941758/yt_tweets_2015_2019/tweet_stats"
    intermediatedir = "/localdata/u6314203/daily_tweets"
    vidsfile        = "/home/users/u6314203/pyProject/hip-popularity/data/engage16/filtered/vids_filter_all.csv"
    outdir          = "/localdata/u6314203/dataset_tweets"
    python dir_build_dataset_tweets.py -i /data4/u5941758/yt_tweets_2015_2019/tweet_stats -m /localdata/u6314203/daily_tweets -v /home/users/u6314203/pyProject/hip-popularity/data/engage16/filtered/vids_filter_all.csv -o /localdata/u6314203/dataset_tweets
    """
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--indir', type=str, required=True)
    args.add_argument('-m', '--intermediatedir', type=str, required=True)
    args.add_argument('-v', '--vidsfile', type=str, required=True)
    args.add_argument('-o', '--outdir', type=str, required=True)
    ap = args.parse_args()
    
    t1 = datetime.datetime.now()
    dirtodir_read_dump(ap.indir, ap.intermediatedir)
    t2 = datetime.datetime.now()
    print("Total time step 1:{} seconds".format((t2-t1).total_seconds()))
    
    build_dataset(ap.intermediatedir, ap.outdir, ap.vidsfile)
    t3 = datetime.datetime.now()    
    print("Total time step 2:{} seconds".format((t3-t2).total_seconds()))
    