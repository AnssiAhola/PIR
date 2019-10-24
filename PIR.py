#!/usr/bin/python3
from PIL import Image, ImageOps, ExifTags
import os
import sys
import getopt
from io import BytesIO

HELP = [
    'Options:',
    '   -h,--help',
    '   -o : Output folder, Default: ./output',
    '   -r : Resolution(s),',
    '           <WidthxHeight> OR',
    '           <Width> (preserves aspect ratio)'
    '           For multiple resolutions separate by commas, i.e -r 900x450,650x325,450,200,100x100'
]

options = {
    'short':'ho:r:',
    'long': ['help', 'output=', 'resolution=']
}


def main(argv):
    try:
        opts, args = getopt.getopt(argv, options['short'], options['long'])
    except getopt.GetoptError as exception:
        print(exception)
        print(*HELP, sep='\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', '--help'] or not argv:
            print(*HELP, sep='\n')
            sys.exit()
        elif opt in ['-o', '--output']:
            print('Output:          ', arg)
        elif opt in ['-r', '--resolution']:
            print('Resolution(s):   ', arg)

def resize(width, height, filter=None, quality=90, dpi=[72,72]):
    return

def save(image, destination):
    return


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args) if args else print(*HELP, sep='\n')