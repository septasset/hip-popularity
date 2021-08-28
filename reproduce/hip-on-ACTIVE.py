from __future__ import print_function, division
import os, bz2, json, time
from datetime import timedelta

import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import sys
sys.path.insert(0, '../')
from pyhip import HIP

dataset_path = "../data/active-dataset.json.bz2"
output_path = "../output/active_res.json"

attributes = ["YoutubeID","numTweet","numShare","numSubscriber","watchTime","dailyViewcount",\
              "description","title","channelId","channelTitle","category","uploadDate","duration",\
              "definition","dimension","caption","regionRestriction.blocked",\
              "regionRestriction.allowed","topicIds","relevantTopicIds","totalShare",\
              "totalViewcount","totalTweet","dailyTweets"]
# load ACTIVE from json
with bz2.BZ2File(dataset_path) as f:
    dataset = json.loads(f.readline())
    
# prepare dataset for HIP train and test
active_videos = {}
for video in dataset:
    active_videos[video['YoutubeID']] = (video['numShare'], video['dailyViewcount'], video['watchTime'],\
                                         video['category'])

start_time = time.time()

# define train-test params
num_train = 90
num_test = 30
num_initialization = 25
size = 50

# train-test, write results
ress = {}
vids = list(active_videos.keys())
for test_vid in vids[:size]:
    daily_share, daily_view, daily_watch, cate = active_videos[test_vid]
    hip_model = HIP()
    hip_model.initial(daily_share, daily_view, num_train, num_test, num_initialization)
    hip_model.fit_with_bfgs()

    hip_params = hip_model.get_parameters()
    hip_predict = hip_model.predict(hip_model.get_parameters_abbr(), hip_model.x[:num_train+num_test])
    res = {
        "category":cate,
        "hipParams":hip_params.tolist(), 
        "predictViewcount":hip_predict.tolist(),
        "dailyViewcount":hip_model.y[:num_train+num_test],
    }
    ress[test_vid] = res
    
with open(output_path, "w") as outfile:
    json.dump(ress, outfile)
    
print('>>> Total time of {1} videos: {0}'.format(str(timedelta(seconds=time.time() - start_time)), size)[:-3])