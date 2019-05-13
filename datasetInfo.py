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


def get_ntuples_from_xml_files(top_directory):
    """Get iterator over ntuples in XML files in a directory.
    Looks recursively through directories for XML files.

    Parameters
    ----------
    top_directory : str

    Yields
    ------
    (str, iterator)
        Returns (relative path of XML file, ntuple filename iterator)
    """
    data = []
    for (dirpath, dirnames, filenames) in os.walk(top_directory):
        print("Looking in", dirpath)
        for filename in filenames:
            full_filename = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_filename, top_directory)
            ntuple_iter = get_ntuple_filenames_from_xml(full_filename)
            yield rel_path, ntuple_iter


def get_user_from_filename(ntuple_filename):
    """Get username from full filepath

    e.g. :
    get_user_from_filename("/nfs/dust/cms/user/robin/UHH2/20190215/Ntuple_RSGluonToTT_M-4000_2016v2.root")
    >> robin

    Parameters
    ----------
    ntuple_filename : str

    Returns
    -------
    str
        Username, or None if not found
    """
    if "/user/" not in ntuple_filename:
        return None
    parts = ntuple_filename.split("/")
    ind = parts.index("user")
    if ind == len(parts)-1:
        return None
    return parts[ind+1]


def get_year_from_dir(dirname):
    """Get dataset year from XML filepath.

    e.g.
    get_year_from_dir("../common/dataset/RunII_102X_v1/2017v2/MC_TTbar.xml")
    >> "2017v2"

    Parameters
    ----------
    dirname : str

    Returns
    -------
    str
        Year, or None if not found
    """
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

    with open("missing.txt", "w") as f_missing:  # save missing ones to file as well

        counter = 0
        for ind, (xml_rel_path, ntuple_iter) in enumerate(get_ntuples_from_xml_files(os.path.abspath(args.topDir))):
            for ntuple_filename in ntuple_iter:

                counter += 1

                if not os.path.isfile(ntuple_filename):
                    print(ntuple_filename, "does not exist, skipping")
                    f_missing.write(ntuple_filename)
                    f_missing.write("\n")
                    continue

                # size = np.random.random() * 100  # dummy data for testing
                user = get_user_from_filename(ntuple_filename)
                size = os.path.getsize(ntuple_filename) / (1024.0 * 1024.0)  # to MBytes
                year = get_year_from_dir(xml_rel_path)
                data.append({
                    "xmldir": os.path.dirname(xml_rel_path),
                    "ntuple": ntuple_filename,
                    "size": size,
                    "user": user,
                    "year": year,
                })

                # Sleep every so often to avoid too much stress on filesystem
                if counter % 5000 == 0:
                    print("Done", counter, ", sleeping for 5s...")
                    sleep(5)

            # if ind > 3:
            #     break

    df = pd.DataFrame(data)
    df['user'] = df['user'].astype('category')
    df['xmldir'] = df['xmldir'].astype('category')
    df['year'] = df['year'].astype('category')

    print(df.head())
    print(df.tail())
    print(df.dtypes)
    print(df.describe())
    print(df.memory_usage(deep=True))
    print(len(df.index))
    # print(data)

    df.to_csv(args.csv)
