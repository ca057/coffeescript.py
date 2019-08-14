#!/usr/bin/env python3.7
"""
# todo
"""

__author__ = "Christian Ost"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse


def main(args):
    """ Main entry point of the app """
    print(args.input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a collage out of a collection of images.")
    parser.add_argument('-i', '--input', default="input", help="the folder with the input images")
    parser.add_argument('-o', '--output', default="output", help="the folder for storing the output images")
    parser.add_argument('-f', '--file', default="compilation", help="filename for the compilation")
    parser.add_argument('--thumb', action="store_true", help="save thumbnails used for the compilation in output folder")
    parser.add_argument('-c', '--columns', help="number of columns used for layout, defaults to square layout")
    parser.add_argument('-s', '--size', default=500, help="width/height for each image in compilation")
    parser.add_argument('-m', '--margin', default=0, help="margin between two images in compilation")
    parser.add_argument('-v', '--verbose', action="store_true", help="show verbose output")

    main(parser.parse_args())
