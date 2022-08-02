import bz2
import csv
import json
import pickle
import argparse
import re
import sys
import numpy as np

def bz2_csv_rows(fp):
    with bz2.open(fp, mode='rt') as bzfp:
        #for row in csv.reader(bzfp): # NOTE: csv.reader is too slow
        #    yield row
        for line in bzfp:
            sp = line.split(',')
            yield sp

def read_write_file(infile, outfile):
    all_dates = []
    all_hashtags = []
    all_vids = []
    all_uids = []
    url_find = re.compile("https\://t\.co/[a-zA-Z0-9]{10}")
    UTF_CHARS = u"a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff"
    TAG_EXP = u'(?:^|[^0-9A-Z&/]+)(?:#|\uff03)([0-9A-Z_]*[A-Z_]+[%s]*)' % UTF_CHARS
    TAG_REGEX = re.compile(TAG_EXP, re.UNICODE | re.IGNORECASE)
    v = 0
    for row in bz2_csv_rows(infile):
        # ignore rate message rows
        if len(row) < 10:
            continue
        
        # ignore non-english tweets
        lang = row[4]
        if lang != 'en':
            continue

        # ignore retweets
        if row[5] != 'N':
            continue

        # get the date
        date = int(row[2])

        # get hashtags
        hashtags = row[13]

        text = row[-3]

        ht_all = set(TAG_REGEX.findall(text))
        if hashtags != 'N':
            ht_all.update(hashtags.split(';'))
        

        # ignore empty hashtags
        if not ht_all:
            continue

        hashtags = ';'.join(ht_all)

        original_vids = row[7].strip()
        if original_vids == 'N':
            original_vids = ""
        quoted_vids = row[9].strip()
        if quoted_vids == 'N':
            quoted_vids = ""
        if original_vids and quoted_vids:
            vids = original_vids + ';' + quoted_vids
        else:
            vids = original_vids + quoted_vids
        
        urls = url_find.findall(text)

        if vids and urls:
            vids = vids + ';' + ';'.join(urls)
        else:
            vids = vids + ';'.join(urls)

        uid = row[3]

        all_dates.append(date)
        all_hashtags.append(hashtags)
        all_vids.append(vids)
        all_uids.append(uid)

    pickle.dump((all_dates, all_hashtags, all_vids, all_uids), open(outfile, "wb")) 

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--infile', type=str, required=True)
    args.add_argument('-o', '--outfile', type=str, required=True)

    ap = args.parse_args()

    read_write_file(ap.infile, ap.outfile)

