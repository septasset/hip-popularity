import os
import sys
import glob
import argparse
from joblib import Parallel, delayed
from readdata_uid import read_write_file

def main():
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--indir', type=str, required=True)
    args.add_argument('-o', '--outdir', type=str, required=True)
    ap = args.parse_args()

    res = []
    for infile in glob.glob(ap.indir + "/*.bz2"):
        outfile = os.path.join(ap.outdir, os.path.split(infile)[1] + ".pik")
        res.append((infile, outfile))
    
    Parallel(n_jobs=20)(delayed(read_write_file)(x[0], x[1]) for x in res)
    
    



if __name__ == "__main__":
    main()

