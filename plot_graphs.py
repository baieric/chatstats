import os
import sys
import pandas as pd

import util
from grapher import graphers_to_plot

def plot_graphs(csvs, output_folder):
    for grapher in graphers_to_plot:
        grapher.graph(csvs, output_folder)

def main(argv):
    if len(argv) != 2:
        print('Usage: {} <outputfolder>'.format(sys.argv[0]))
        sys.exit(2)
    output_folder =  argv[1]

    csvs = util.get_csvs(output_folder)

    plot_graphs(csvs, output_folder)

if __name__ == "__main__":
    main(sys.argv)
