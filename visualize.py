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

ATLAS_FILE = './atlas.tsv'
OUT_PATH = '.'

# Plotting parameters:
NR_CHRS_XTICKS = 30         # number of characters to be printed of the xticks
FIG_SIZE = (15, 7)          # figure size
COLOR_MAP = 'tab10'         # color map. See https://matplotlib.org/users/colormaps.html
#COLOR_MAP = 'Vega10'
# tissues with less than OTHERS_THRESH contribution will be clustered to 'other' (black):
OTHERS_THRESH = 0.01
TITLE = ""

####################################
#       Plotting methods           #
####################################

def hide_small_tissues(df):
    """
    tissues with very small contribution are grouped to the 'other' category.
    :return: The DataFrame with the new category ('other'),
             where the low-contribution tissues are set to 0.
    """
    others = df[df < OTHERS_THRESH].sum()
    df[df < OTHERS_THRESH] = 0.0
    df = df.append(others.rename('other'))
    return df


def gen_bars_colors_hatches(nr_tissues):
    """
    Generate combinations of colors and hatches for the tissues bars
    Every tissue will get a tuple of (color, hatch)
    the last tuple is for the 'other' category, and is always black with no hatch.
    :return: a list of tuples, with length == nr_tissues
    """
    matplotlib.rcParams['hatch.linewidth'] = 0.3
    hatches = [None, 'xxx', '...', 'O', '++'][:nr_tissues // 7]

    nr_colors = int(math.ceil(nr_tissues / len(hatches)) + 1)

    # generate bars colors:
    cmap = matplotlib.cm.get_cmap(COLOR_MAP)
    norm = matplotlib.colors.Normalize(vmin=0.0, vmax=float(nr_colors))
    colors = [cmap(norm(k)) for k in range(nr_colors)]

    def get_i_bar_tuple(i):
        color_ind = i % nr_colors
        hatch_ind = int(i // math.ceil(nr_tissues / len(hatches)))
        return colors[color_ind], hatches[hatch_ind]

    colors_hatches_list = [get_i_bar_tuple(i) for i in range(nr_tissues - 1)]
    # return 0
    return colors_hatches_list + [((0, 0, 0, 1), None)]


def plot_res(df, name, show=False):

    df = hide_small_tissues(df)
    nr_tissues, nr_samples = df.shape
    TITLE = name

    # generate bars colors and hatches:
    colors_hatches = gen_bars_colors_hatches(nr_tissues)

    plt.figure(figsize=FIG_SIZE)
    r = [i for i in range(nr_samples)]
    bottom = np.zeros(nr_samples)
    for i in range(nr_tissues):
        plt.bar(r, list(df.iloc[i, :]),
                edgecolor='white',
                width=0.85,
                label=df.index[i],
                bottom=bottom,
                color=colors_hatches[i][0],
                hatch=colors_hatches[i][1])
        bottom += np.array(df.iloc[i, :])

    # Custom x axis
    plt.xticks(r, [w[:NR_CHRS_XTICKS] for w in df.columns], rotation='vertical', fontsize=9)
    plt.xlabel("sample")
    plt.xlim(-.6, nr_samples - .4)

    # Add a legend and a title
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    plt.title('Deconvolution Results\n' + op.basename(TITLE))

    # adjust layout, save and show
    plt.tight_layout(rect=[0, 0, .83, 1])
    plt.savefig(TITLE + '_deconv_plot.png')
    if show:
        plt.show()

