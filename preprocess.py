#!/usr/bin/python3 -u
import numpy as np
import pandas as pd
from scipy import optimize
import argparse
import os.path as op
import sys
from multiprocessing import Pool
import math
import matplotlib.pylab as plt
import matplotlib.cm
import matplotlib.colors


def _validate_csv_file(csv_path):
    """
    Validate an input csv file. Raise an exception or print warning if necessary.
    :param csv_path: input csv path
    """
    err_msg = ''

    # check if file exists and ends with 'csv':
    if not op.isfile(csv_path):
        err_msg = 'no such file:\n%s' % csv_path
    elif not (csv_path.endswith('csv') or csv_path.endswith('csv.gz') or csv_path.endswith('tsv')):
        err_msg = 'file must end with ".csv[.gz]":\n%s' % csv_path

    # take a peek and validate the file format
    else:
        if (csv_path.endswith('csv')):
            input_head = pd.read_csv(csv_path, nrows=4)
        else:
            input_head = pd.read_table(csv_path, nrows=4)
        
        # at least two columns:
        if input_head.shape[1] < 2:
            err_msg = 'file must contain at least 2 columns (accessions and a values). '

        # first column must be Illumina IDs column
        elif not str(input_head.iloc[0, 0]).startswith('cg'): 
                err_msg = 'invalid Illumina ID column'

        # print a warning if the second column in the csv file has a numeric header
        # (this probably means there is no header)
        if input_head.columns[1].replace('.', '', 1).isdigit():
            print('Warning: input files should have headers', file=sys.stderr)

    if err_msg:
        err_msg = op.basename(csv_path) + ': ' + err_msg
        raise ValueError(err_msg)


def preprocessing(atlas_path):
        """
        Read the atlas csv file, save data in self.atlas
        :param atlas_path: Path to the atlas csv file
        """
        # validate path:
        _validate_csv_file(atlas_path)
        # Read atlas, sort it and drop duplicates
        df = pd.read_csv(str(atlas_path))
        df.rename(columns={list(df)[0]: 'acc'}, inplace=True)
        df = df.sort_values(by='acc').drop_duplicates(subset='acc').reset_index(drop=True)
        return df, "reference_atlas.csv"

def get_bname(samp_path):
    """
    Compose output files path:
    join the out_dir path with the basename of the samples file
    remove csv and gz extensions.
    """
    base_fname = op.basename(samp_path)

    if base_fname.endswith('.gz'):
        base_fname = op.splitext(base_fname)[0]
    base_fname = op.splitext(base_fname)[0]
    return op.join(base_fname)


def load_sample(samp_path, atlas):
        """
        Read samples csv file. Reduce it to the atlas sites, and save data in self.samples
        Note: samples file must contain a header line.
        """

        # validate path:
        _validate_csv_file(samp_path)

        samples = pd.read_csv(samp_path)
        samples.rename(columns={list(samples)[0]: 'acc'}, inplace=True)
        samples = samples.sort_values(by='acc').drop_duplicates(subset='acc').reset_index(drop=True)
        samples = samples.merge(atlas['acc'].to_frame(), how='inner', on='acc')
        return samples, samp_path