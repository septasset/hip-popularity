import bz2, os, sys, glob
import json, csv, re, datetime
import pickle
from joblib import Parallel, delayed
from tqdm import tqdm

import argparse

def bz2_csv_rows(fp):
    with bz2.open(fp, mode='rt') as bzfp:
        for line in tqdm(bzfp, desc="raw tweets bz2"):
            sp = line.split(',')
            yield sp
            
def read_write_file(infile, outfile):
    """
    {
        vid_1: tweetCounts,
        vid_2: tweetCounts,
        ...
    }
    """
    map_vid_tweetCounts = {}
    all_vids = []    
    all_dates = []

    counts = 0    
    for row in bz2_csv_rows(infile):
        counts += 1
            
        # ignore rate message rows
        if len(row) < 10:
            continue
        
        # get the date (yyyy-mm-dd)
        date = row[1].strip()

        vids = []
        # single vid is of length 11
        original_vids = row[7].strip()
        if original_vids != 'N':
            vids.extend(original_vids.split(";"))
        retweeted_vids = row[8].strip()
        if retweeted_vids != 'N':
            vids.extend(retweeted_vids.split(";"))
        quoted_vids = row[9].strip()
        if quoted_vids != 'N':
            vids.extend(quoted_vids.split(";"))
        
        for vid in vids:
            if vid not in map_vid_tweetCounts:
                map_vid_tweetCounts[vid] = 0
            map_vid_tweetCounts[vid] += 1
        
        all_vids.append(vids)
        all_dates.append(date)
    
    if outfile is not None:
        pickle.dump(map_vid_tweetCounts, open(outfile, "wb"))
        
def dirtodir_read_dump(indir, outdir, date_range=("2016-07-02", "2016-09-01")):
# def dirtodir_read_dump(indir, outdir, date_range=("2016-07-02", "2016-07-11")):
    date_start = datetime.datetime.strptime(date_range[0], "%Y-%m-%d")
    date_end   = datetime.datetime.strptime(date_range[1], "%Y-%m-%d")
    
    res = []
    for infile in glob.glob(indir + "/*.bz2"):
        date_str = os.path.split(infile)[1].split(".")[0]
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        if date >= date_start and date <= date_end:
            outfile = os.path.join(outdir, date_str + ".pik")
            res.append((infile, outfile))

    Parallel(n_jobs=20)(delayed(read_write_file)(x[0], x[1]) for x in res)
    
if __name__ == "__main__":
    """Example
    indir  = "/data4/u5941758/yt_tweets_2015_2019/tweet_stats"
    outdir = "/localdata/u6314203/daily_tweets"
    """
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--indir', type=str, required=True)
    args.add_argument('-o', '--outdir', type=str, required=True)
    ap = args.parse_args()

    t1 = datetime.datetime.now()
    dirtodir_read_dump(ap.indir, ap.outdir)
    t2 = datetime.datetime.now()
    print("Total time:{} seconds".format((t2-t1).total_seconds()))
    