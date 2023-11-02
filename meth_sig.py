
# call Deconvoluve in deconvolve.py import 

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
from visualize import plot_res
from preprocess import preprocessing, load_sample
import algo_nnls
import getopt
import sys
from algo_nnls import Deconvolve  # Import your Deconvolve class from the appropriate module


ATLAS_FILE = './atlas.tsv'
OUT_PATH = '.'



def main():    

    parser = argparse.ArgumentParser()
    parser.add_argument('--signature', '-s', default=ATLAS_FILE,
                        help='Path to Atlas csv file.\nThe first column must be'
                             ' Illumina IDs (e.g cg00000029)')
    
    parser.add_argument('--outdir', '-od', default=OUT_PATH, help='Output directory')

    
    parser.add_argument('-outfile', '-of', default="out.png",
                        help='name of image file')
    
    parser.add_argument('--inputfile',
                help='Path to samples csv file. It must have a header line.\n'
                        'The first column must be Illumina IDs (e.g cg00000029)')


    parser.add_argument('--slim', action='store_true',
                        help='Write the results table *without indexes and header line*')
    
    parser.add_argument('--algo',
                    help='Write type of algorithm you want to use*')


    parser.add_argument('--residuals', '-r', action='store_true',
                        


                        help='Output residuals to a separate file')

    parser.add_argument('--plot', action='store_true',
                        help='Plot stacked bars of the results')


    args = parser.parse_args()
    # preprocess input file saved in output file (args.inputfile)
    input_tsv, atlas_path = preprocessing(args.signature) #convert to tsv
    samples, samp_name = load_sample(args.inputfile, input_tsv)
    # #include other algorithm files later on w/ if statement related to args


    decomposed_tsv = Deconvolve(input_tsv, samples, samp_name,
               out_dir=args.outdir,
               resid=args.residuals,
               slim=args.slim).run_deconv()
    plot_res(decomposed_tsv, samp_name)
            #returns deconvoluted results 
            #goes into visuali
            # put in output file from preprocessing function 
if __name__ == "__main__":
    main()
