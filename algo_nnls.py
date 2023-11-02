#C


#!/usr/bin/python3 -u
import numpy as np
import pandas as pd
from scipy import optimize
import argparse
import os.path as op
import sys
from multiprocessing import Pool
import math
# import matplotlib.pylab as plt
# import matplotlib.cm
# import matplotlib.colors

ATLAS_FILE = './atlas.tsv'
OUT_PATH = '.'


####################################
#     Deconvolve class             #
####################################


class Deconvolve:
    def __init__(self, atlas, samples, samp_name, out_dir, resid, slim=False, algo="nnls", plot=False):
        self.out_dir = out_dir                      # Output dir to save mixture results and plot
        self.slim = slim                            # Write results table w\o indexes and header (bool)
        self.plot = plot                            # Plot results (bool)
        self.resid = resid                          # Output residuals as well
        self.algo = algo
        self.samples = samples
        self.out_bname = samp_name  # output files path w/o extension

        self.atlas = atlas
        # self.out_bname = self.get_bname(samp_path)  # output files path w/o extension

        # Load input files:
        # self.atlas = self.load_atlas(atlas_path)    # Atlas
        # self.samples = self.load_sample(samp_path)  # Samples to deconvolve

    # def get_bname(self, samp_path):
    #     """
    #     Compose output files path:
    #     join the out_dir path with the basename of the samples file
    #     remove csv and gz extensions.
    #     """
    #     base_fname = op.basename(samp_path)

    #     if base_fname.endswith('.gz'):
    #         base_fname = op.splitext(base_fname)[0]
    #     base_fname = op.splitext(base_fname)[0]
    #     return op.join(self.out_dir, base_fname)
    




    @staticmethod
    def algo_nnls(samp, atlas):
        """
        Deconvolve a single sample, using NNLS, to get the mixture coefficients.
        :param samp: a vector of a single sample
        :param atlas: the atlas DadtaFrame
        :return: the mixture coefficients (of size 25)
        """

        name = samp.columns[1]

        # remove missing sites from both sample and atlas:
        data = samp.merge(atlas, on='acc', how='inner').copy().dropna(axis=0)
        if data.empty:
            print('Warning: skipping an empty sample {}'.format(name), file=sys.stderr)
            # print('Dropped {} missing sites'.format(self.atlas.shape[0] - red_atlas.shape[0]))
            return np.nan
        print('{}: {} sites'.format(name, data.shape[0]), file=sys.stderr)
        del data['acc']

        samp = data.iloc[:, 0]
        red_atlas = data.iloc[:, 1:]

        # get the mixture coefficients by deconvolution (non-negative least squares)
        mixture, residual = optimize.nnls(red_atlas, samp)
        mixture /= np.sum(mixture)
        return mixture, residual
    def algo_dnn(samp, atlas):
        pass

    def algo_nnmf(samp, atlas):
        pass

    def run_deconv(self):

        # run deconvolution on all samples in parallel
        processes = []
        with Pool() as p:
            if self.algo == "nnls":

                for i, smp_name in enumerate(list(self.samples)[1:]):
                    params = (self.samples[['acc', smp_name]], self.atlas)
                    processes.append(p.apply_async(Deconvolve.algo_nnls, params))
            elif self.algo == "dnn":
                for i, smp_name in enumerate(list(self.samples)[1:]):
                    params = (self.samples[['acc', smp_name]], self.atlas)
                    processes.append(p.apply_async(Deconvolve.algo_dnn, params))
            else: 
                for i, smp_name in enumerate(list(self.samples)[1:]):
                    params = (self.samples[['acc', smp_name]], self.atlas)
                    processes.append(p.apply_async(Deconvolve.algo_nnmf, params))


            p.close()
            p.join()

        self.samples = self.samples.iloc[:, 1:]

        # collect the results to 'res_table':
        arr = [pr.get() for pr in processes]
        res_table = np.empty((self.atlas.shape[1] - 1, self.samples.shape[1]))
        resids_table = np.empty((self.samples.shape[1], 1))
        for i in range(len(arr)):
            res_table[:, i], resids_table[i] = arr[i]
        df = pd.DataFrame(res_table, columns=self.samples.columns, index=list(self.atlas.columns)[1:])

        # Dump results
        # print(df)
        out_path = self.out_bname + '_deconv_output.csv'
        if self.slim:   # without indexes and header line
            df.to_csv(out_path, index=None, header=None, float_format='%.3f')
        else:
            df.to_csv(out_path, float_format='%.3f')

        if self.resid:
            rf = pd.DataFrame(resids_table, columns=['Residuals'], index=self.samples.columns)
            rf.to_csv(self.out_bname + '_residuals.csv', float_format='%.3f')
        
        return df