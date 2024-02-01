# Methylation Atlas Deconvolution

This is built upon the Nature article [Comprehensive human cell-type methylation atlas reveals origins of circulating cell-free DNA in health and disease](https://www.nature.com/articles/s41467-018-07466-6). 

This program an input **reference atlas** file to deconvolve a given **sample**, or multiple samples with three algorithms: non-negative least squares (NNLS), Deep Neural Network (DNN), and non-negative matrix factorization (NNMF). 
It outputs a csv file and plots a stacked bars figure. 

### atlas
A reference atlas file. 
- csv file
- Contains a header (columns names).
- The first column must be Illumina IDs.

The reference atlas used on the paper is supplied in this repository - *reference_atlas.csv*.
The full reference atlas, with ~390K sites (before the feature selection process) is also supplied - *full_reference_atlas.csv.gz*. For better deconvolurions results, it's recommended not to use the full atlas, but the smaller one.

### samples
A file containing one or more samples, with similar requirements as the atlas file (csv, header, index column).
The CpG (Illumina ID) column may contain different CpG sites than the ones in the atlas files, as long as they share some sites.

An example dummy file is supplied, *examples.csv*.

---

### Usage

```
usage: meth_sig.py [-h] [--signature ATLAS_PATH] [--inputfile] 
                     [--outfile OUT_NAME]
                     samples_path

positional arguments:
  samples_path          Path to samples csv file. It must have a header line.
                        The first column must be Illumina IDs (e.g cg00000029)

optional arguments:
  -h, --help            show this help message and exit
  --signature, -s
                        Path to signature file
  --outfile
                        Out-file name of picture
  --inputfile
                        samples file path 
```

---
### Example
```
meth_sig.py --signature reference_atlas.csv -outfile out.png --inputfile  examples.csv
```
will deconvolve all samples given as columns in *examples.csv*, dump the resulting coefficients to a csv file named *examples_deconv_output.csv*, plot them, and dump the figure to *examples_deconv_plot.png*.
![Image of bar plot](https://github.com/anaisha-d/meth_atlas/blob/main/Meth%20Atlas.png?raw=true)
