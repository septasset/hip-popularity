import subprocess

import bz2, os, sys, glob
import json, datetime
import pickle
from joblib import Parallel, delayed

def engage_dataset(test_category, eval_days = [90, 135, 180, 225, 270]):
    # read days info in engage16
    with open(os.path.join(engage_dataset_base, test_category+".json"), "r") as f:
        dataset_json = f.readlines()

    # dict-like dataset
    dataset = {}
    # remove duplication
    vids_set = set()

    for line in dataset_json:
        record = json.loads(line)
        try:        
            day = [int(x) for x in record['insights']['days'].split(",")]
            day_zero = record['insights']['startDate']
            views = [x for x in record['insights']['dailyView'].split(",")]

            """!!!"""
            if len(day) < eval_days[-1]: continue
        except:
            continue
        dataset[record['id']] = (day_zero, day, views)

        if record['id'] in vids_set:
            continue
        vids_set.add(record['id'])
        
    return dataset

def write_segfit_result(views_str, length_str, index, res):
    # if sequential: 6 seconds/video
    cp = subprocess.run([segfit_path,"-s", views_str, "-l", length_str], 
                        universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    phases = [line.split("\t") for line in cp.stdout.strip("\n").split("\n")]
    
    res['res_segfit'][index] = cp.stdout    
    res['end_first_phase'][index] = int(phases[0][1])
    res['num_phases'][index] = len(phases)

def get_segfit_input(dataset, vids):
    sequences = []
    ls = []    
    for vid in vids:
        values = dataset[vid]
        views_list = values[2]
        views_str = ",".join(views_list)
        length = len(views_list)
        sequences.append(views_str)
        ls.append(str(length))
        
    return sequences, ls    
    
if __name__ == "__main__":
    segfit_path = "./segfit"
    engage_dataset_base = "/localdata/u6314203/dataset_engage16/tweeted_videos"
    output_base = "/localdata/u6314203/segfit_res_engage16"

    categories_eligible = ["autos", "comedy","education","entertainment", \
                           "film","gaming","howto","music",\
                           "news","people","science","sports",\
                           "travel"]
    njobs = 20

    for category in categories_eligible[:2]:
        dataset_partial = engage_dataset(category)

        vids = list(dataset_partial.keys())
        sequences, ls = get_segfit_input(dataset_partial, vids)

        res = {
            'vid': vids,
            'end_first_phase': [None]*len(vids),
            'num_phases': [None]*len(vids), 
            'res_segfit': [None]*len(vids),
        }

        t1 = datetime.datetime.now()
        Parallel(n_jobs=njobs, backend="threading")(delayed(write_segfit_result)(sequences[x], ls[x], x, res) for x in range(len(vids)))
        t2 = datetime.datetime.now()
        print("Total time({}):{} seconds".format(category, (t2-t1).total_seconds()))    

        outfile = os.path.join(output_base, "{}.json".format(category))
        with open(outfile, "w") as f:
            json.dump(res, f)    