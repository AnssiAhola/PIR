#!/usr/bin/python3
import os
import sys
import argparse
import re
import math
from PIL import Image, ImageOps, ExifTags
from io import BytesIO
from progress.bar import Bar


valid_ext = ['.jpg', '.jpeg', '.png']


def exists(s):
    if not os.path.exists(s):
        raise argparse.ArgumentTypeError('path does not exist')
    else:
        return s

# Trying to get to work


def validresolution(arr):
    for res in arr:
       # res = res.split('x')
        res = map(lambda x: int(x), res)
    return arr


parser = argparse.ArgumentParser(
    description='Example. PIR.py ./inputfolder ./outputfolder 2560x1440 1920x1080')
parser.add_argument('input', type=exists, help='input file or folder')
parser.add_argument('output', help='output folder')
parser.add_argument(
    'res', type=validresolution, nargs='+', help='output resolutions, <width>x<height> OR <width>')
parser.add_argument(
    '--rotate', help='Rotate image(s) if neccesary', action='store_true')
parser.add_argument('-y', help='Skip confirmation', action='store_true')
parser.add_argument(
    '--verbose', help='Enable detailed logging', action='store_true')
parser.add_argument(
    '--organize', help='Organize output resolutions in their own folders, disables the resolution suffix', action='store_false')
args = parser.parse_args()


def main(argv):
    try:
        input_dir = os.path.realpath(args.input)
        rotate = True if args.rotate else False
        output_dir = os.path.realpath(args.output)
        print(args.res)
        # Determine if input is a file or a folder
        # If a file, store the filename and remove it from input_dir
        if any(ext in input_dir for ext in valid_ext):
            filenames = [input_dir.split('\\')[-1]]
            input_dir = os.path.dirname(os.path.realpath(args.input))
        else:
            filenames = [file for file in os.listdir(input_dir)]

        if args.verbose:
            print('Inputfolder:         ', input_dir)
            print('Outputfolder:        ', output_dir)
            print('Rotate:              ', rotate)
            print('Resolution(s):       ', args.res)
            print(*filenames, sep='\n')
            print()
            if not args.y:
                input('Press anything to continue, Ctrl+C to cancel...')

        #resize(input_dir, filenames, output_dir, args.res)

    except KeyboardInterrupt:
        print('\nProcess cancelled')


def resize(input_dir, filenames, output_dir, resolutions, quality=95):
    # skipped = 0
    try:
        for res in resolutions:
            with Bar('Resizing (%d)' % res, max=len(filenames)) as bar:
                for filename in filenames:
                    image = Image.open(os.path.join(input_dir, filename))

                    ratio = math.min(width/image.size[0], height/image.size[1])

                    # if res >= image.size[0 and 1]:
                    #     skipped += 1
                    #     continue
                    name, ext = os.path.splitext(filename)

                    image.thumbnail([res, res], Image.ANTIALIAS)

                    # Determine where files will be saved and with or without resolution suffix
                    if (args.organize):
                        save_to = os.path.join(output_dir, str(res))
                    else:
                        save_to = output_dir
                        filename = name + (' - %dx%d' % image.size) + ext
                    # Check if save location exists
                    if not os.path.exists(save_to):
                        os.mkdir(save_to)

                    image.save(
                        os.path.join(save_to, filename),
                        image.format,
                        quality=quality)
                    bar.next()
        # print('Skipped %d files due to target resolution being larger or equal to original resolution' % skipped)

    except IOError as err:
        print(err)
    except KeyboardInterrupt:
        print('\nProcess aborted')


if __name__ == "__main__":
    main(sys.argv[1:])
