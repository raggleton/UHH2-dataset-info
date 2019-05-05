#!/usr/bin/env python


"""Loop over XML files, get filenames, look for their info, print stats"""


from __future__ import print_function

import os
import sys
import argparse
import pandas as pd
import numpy as np
from time import sleep


def get_ntuple_filenames_from_xml(full_filename):
    """Yield ntuple filenames from XML file

    Parameters
    ----------
    full_filename : str
        XML file to get ntuples from

    Yields
    ------
    generator
        To iterate over filenames
    """
    with open(full_filename) as f:
        is_comment = False
        for line in f:
            if line.startswith("<!--"):
                is_comment = True
            if line.endswith("-->"):
                is_comment = False
            if is_comment:
                continue
            if line.startswith("<In FileName="):
                this_line = line.strip()
                this_line = this_line.replace('<In FileName="', '')
                this_line = this_line.replace('" Lumi="0.0"/>', '')
                yield this_line


def get_of_xml_files(top_directory):
    """Summary

    Parameters
    ----------
    top_directory : str
        Description

    Yields
    ------
    TYPE
        Description
    """
    data = []
    for (dirpath, dirnames, filenames) in os.walk(top_directory):
        print(dirpath)
        for filename in filenames:
            full_filename = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_filename, top_directory)
            ntuple_iter = get_ntuple_filenames_from_xml(full_filename)
            yield rel_path, ntuple_iter


def get_user_from_filename(ntuple_filename):
    if "/user/" not in ntuple_filename:
        return None
    parts = ntuple_filename.split("/")
    ind = parts.index("user")
    if ind == len(parts)-1:
        return None
    return parts[ind+1]


def get_year_from_dir(dirname):
    parts = dirname.split("/")
    branch = "RunII_102X_v1"
    if branch in dirname:
        ind = parts.index(branch)
        if ind == len(parts)-1:
            return None
        return parts[ind+1]
    else:
        return parts[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topDir",
                        help="Top directory to look for XML files. "
                        "All subdirectories will be included, recursively.")
    parser.add_argument("--csv",
                        default="datasetinfo.csv",
                        help="Input/output CSV file. If already exists, "
                        "will use info from it and only update with new entries.")
    args = parser.parse_args()

    if not os.path.isdir(args.topDir):
        raise IOError("%s does not exist" % args.topDir)

    data = []

    counter = 0
    for ind, (xml_rel_path, ntuple_iter) in enumerate(get_of_xml_files(os.path.abspath(args.topDir))):
        for ntuple_filename in ntuple_iter:
            counter += 1
            user = get_user_from_filename(ntuple_filename)
            # size = np.random.random() * 100  # dummy data for testing
            size = os.path.getsize(ntuple_filename) / (1024.0 * 1024.0)  # to MBytes
            year = get_year_from_dir(xml_rel_path)
            data.append({
                "xmldir": os.path.dirname(xml_rel_path),
                "ntuple": ntuple_filename,
                "size": size,
                "user": user,
                "year": year,
            })

            # sleep every so often to avoid hammering the system
            if counter % 1000 == 0:
                print("Processed", counter, "files, sleeping for 5s...")
                sleep(5)

    df = pd.DataFrame(data)
    df['user'] = df['user'].astype('category')
    df['xmldir'] = df['xmldir'].astype('category')
    df['year'] = df['year'].astype('category')

    print(df.head())
    print(df.dtypes)
    print(df.describe())
    print(len(df.index))
    print("Total size: %.3f TB" % (df['size'].sum() / (1024*1024.)))

    df.to_csv(args.csv)
