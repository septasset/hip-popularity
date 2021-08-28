from __future__ import print_function, division
import os, bz2, json, time, argparse
from datetime import timedelta

import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

dataset_path = "../data/active-dataset.json.bz2"

with bz2.BZ2File(dataset_path) as f:
    dataset = json.loads(f.readline())
    
active_videos = {"videoIds":[]}
for video in dataset:
    active_videos["videoIds"].append(video["YoutubeID"])

with open("../data/active-dataset-vids-order.json", "w") as outfile:
    json.dump(active_videos, outfile)