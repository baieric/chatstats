'''
main Chat Stats script
'''

import sys

import util
from fb_parser import make_csvs
from plot_graphs import plot_graphs


def main(argv):
    if len(argv) != 2:
        print("Usage: {} <conversation_file>".format(argv[0]))
        sys.exit(2)

    output_folder = make_csvs(argv[1])
    csvs = util.get_csvs(output_folder)

    plot_graphs(csvs, output_folder)

    print("Results saved in {}".format(output_folder))

if __name__ == "__main__":
    main(sys.argv)
