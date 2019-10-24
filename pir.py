from PIL import Image, ImageOps, ExifTags
import os
import sys
import getopt
from io import BytesIO

HELP = [
    'Options:',
    '   -h,--help',
    '   -o : Output folder, Default: ./output',
    '   -r : Resolution(s), <WidthxHeight>, for multiple resolutions separate by comma, i.e -r 100x100,200x200'
]

options = {
    '-h': HELP,
}


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ho:", ['help', 'output='])
    except getopt.GetoptError as exception:
        print(exception)
        print(*HELP, sep='\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', '--help'] or not argv:
            print(*HELP, sep='\n')
            sys.exit()
        elif opt in ['-o', '--output']:
            print('Output is', arg)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args) if args else print(*HELP, sep='\n')
