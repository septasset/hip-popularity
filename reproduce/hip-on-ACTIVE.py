from __future__ import print_function, division
import os, bz2, json, time, argparse
from datetime import timedelta

import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import sys
sys.path.insert(0, '../')
from pyhip import HIP

# python hip-on-ACTIVE.py --batchSize 400 --batchNo 
# actually take 15 hrs

dataset_path = "../data/active-dataset.json.bz2"
output_path = "../output/active_res"
vidsOrder_path = "../data/active-dataset-vids-order.json"

attributes = ["YoutubeID","numTweet","numShare","numSubscriber","watchTime","dailyViewcount",\
              "description","title","channelId","channelTitle","category","uploadDate","duration",\
              "definition","dimension","caption","regionRestriction.blocked",\
              "regionRestriction.allowed","topicIds","relevantTopicIds","totalShare",\
              "totalViewcount","totalTweet","dailyTweets"]

def parse_args():
    parser = argparse.ArgumentParser(description='Reproduce HIP on ACTIVE')
    parser.add_argument('--batchSize',
                    help='subset size',
                    required=True,
                    type=int)    
    parser.add_argument('--batchNo',
                        help='which subset of ACTIVE to train-test',
                        required=True,
                        type=int)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    start_time = time.time()
    
    # load ACTIVE from json
    with bz2.BZ2File(dataset_path) as f:
        dataset = json.loads(f.readline())

    # prepare dataset for HIP train and test
    active_videos = {}
    for video in dataset:
        active_videos[video['YoutubeID']] = (video['numShare'], video['dailyViewcount'], video['watchTime'],\
                                             video['category'])

    # define train-test params
    num_train = 90
    num_test = 30
    num_initialization = 25
    size = args.batchSize # expect to take 8hr for 400 videos
    bNo = args.batchNo
    # deterministic vids      
    with open(vidsOrder_path, "r") as f:
        tmpt = json.loads(f.readline())
    vids = tmpt["videoIds"]
    
    # train-test, write results
    ress = {}
    count = 0
    for test_vid in vids[bNo*size:bNo*size+size]:
        daily_share, daily_view, daily_watch, cate = active_videos[test_vid]
        hip_model = HIP()
        hip_model.initial(daily_share, daily_view, num_train, num_test, num_initialization)
        hip_model.fit_with_bfgs(False)

        hip_params = hip_model.get_parameters()
        hip_predict = hip_model.predict(hip_model.get_parameters_abbr(), hip_model.x[:num_train+num_test])
        res = {
            "category":cate,
            "hipParams":hip_params.tolist(), 
            "predictViewcount":hip_predict.tolist(),
            "dailyViewcount":hip_model.y[:num_train+num_test],
        }
        ress[test_vid] = res
        count+=1
        if count % (size//20) == 0:
            print(">>> Progress: {}/{}".format(count, size))

    with open("{}_{}_{}.json".format(output_path, bNo*size, bNo*size+size), "w") as outfile:
        json.dump(ress, outfile)

    print('>>> Total time of {1} videos: {0}'.format(str(timedelta(seconds=time.time() - start_time)), size)[:-3])

if __name__ == '__main__':
    main()