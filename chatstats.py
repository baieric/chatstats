'''
main Chat Stats script
'''

import sys

from make_chat_csv import make_csv
from make_graphs import plot_graphs

def main(argv):
    if len(argv) != 1:
        print 'Usage: {} <outputfolder>'.format(sys.argv[0])
        sys.exit(2)
    outputfolder = "generated/{}".format(argv[0])

    chatfile = make_csv(outputfolder)

    graph_dir = "{}/graphs".format(outputfolder)
    plot_graphs(chatfile, graph_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
