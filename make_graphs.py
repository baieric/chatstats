import os
import sys
import pandas as pd

from grapher import graphers_to_plot
from message import Message

def plot_graphs(chatfile, graph_dir):
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    for grapher in graphers_to_plot:
        grapher.graph(chatfile, graph_dir)

def main(argv):
    if len(argv) != 1:
        print 'Usage: {} <outputfolder>'.format(sys.argv[0])
        sys.exit(2)
    outputfolder = "generated/{}".format(argv[0])
    chatfile = '{}/chat.csv'.format(outputfolder)
    if not os.path.exists(chatfile):
        print 'chat.csv not found. Generate chat.csv with make_chat_csv.py'.format(sys.argv[0])
        sys.exit(2)

    graph_dir = "{}/graphs".format(outputfolder)
    plot_graphs(chatfile, graph_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
