# UHH2 Ntuple dataset info

Script & notebook to gather & analyse data about the UHH2 ntuples.

Should work in both python2 & 3.

## Prerequisites

- Local copy of UHH2 code (currently only for RunII_102X_v1 branch)
- `numpy`, `matplotlib`, `pandas`, `jupyter` python libraries. Easily installable with the included `requirements.txt`: `pip install -r requirements.txt`

## Running

1) Run `datasetInfo.py` on NFS machine:

```
./datasetInfo.py <location of UHH2/common/datasets/RunII_102X_v1> --csv datasetinfo_DD_MON_YY.csv
```

This will take a while, since it pauses every 5K files to ease up on the filesystem. (TODO: just run with `nice` instead?)
This script makes a (large) CSV file that can then be used for later processing.
It also produces a file `datasetinfo_DD_MON_YY_missing.txt`, with a list of all ntuples in an XMl file but not found on disk.

2) Run the jupyter notebook:

```
jupyter notebook UHH2_Ntuple_Info.ipynb
```

Update the CSV filename to be read in before running all cells.
This notebook will load the CSV file, and make some plots & print stats.

3) Make it into a webpage

```
jupyter nbconvert --to=html UHH2_Ntuple_Info.ipynb
```

This currently looks a bit messy - TODO: find how to hide code boxes

Alternatively make into slides by using `--to=slides`. Configure slides using `View - Cell Toolbar - Slideshow`.
