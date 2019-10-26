#!/usr/bin/python3
import os
import re
import sys
import math
import time
import argparse
import concurrent.futures
from io import BytesIO
from progress.bar import Bar
from PIL import Image, ImageOps, ExifTags, ImageFile

# Fixes "IOError: broken data stream when reading image file" when loading files concurrently
ImageFile.LOAD_TRUNCATED_IMAGES = True

valid_ext = ['.jpg', '.jpeg', '.png']

# Check if input folder/file exists


def exists(s):
    if not os.path.exists(s):
        raise argparse.ArgumentTypeError('path does not exist')
    else:
        return s

# Validate resolution (WidthxHeight OR Width)


def resolution(res):
    if re.match(r'^[0-9]+x*[0-9]+$', res):
        return res
    else:
        raise argparse.ArgumentTypeError('&d' % res)


parser = argparse.ArgumentParser(
    description='Example. PIR.py -i ./inputfolder -o ./outputfolder 2560x1440 1920 100x100 --resize')
parser.add_argument(
    '-i', '--input', type=exists, help='Input file or folder', required=True)
parser.add_argument(
    '-o', '--output', help='Output folder', required=True)
parser.add_argument(
    'resolution', type=resolution, nargs='+', help='output resolutions, <width>x<height> OR <width>')

# Logging arguments
parser.add_argument(
    '-y', '--yes', help='Skip confirmation', action='store_true')
parser.add_argument(
    '--verbose', help='Enable detailed logging', action='store_true')
parser.add_argument(
    '--organize',
    help='Organize output resolutions in their own folders, disables the resolution suffix',
    action='store_true')

# Image processing arguments
parser.add_argument(
    '--rotate', help='Rotate image(s) if neccesary', action='store_true')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    '--resize', help='resize images, maintains aspect ratio', action='store_true')
group.add_argument(
    '--crop',
    help='crop images, centered, NOTE: Skips images with width OR height greater or equal to target',
    action='store_true')

args = parser.parse_args()


def main(argv):
    skipped = 0
    try:
        input_dir = os.path.realpath(args.input)
        output_dir = os.path.realpath(args.output)
        resolutions = args.resolution
        for i, res in enumerate(resolutions):
            resolutions[i] = tuple(map(lambda r: int(r), res.split('x')))
            if len(resolutions[i]) is 1:
                resolutions[i] = (resolutions[i][0], resolutions[i][0])

        if any(ext in input_dir for ext in valid_ext):
            files = [input_dir.split('\\')[-1]]
            input_dir = os.path.dirname(os.path.realpath(args.input))
        else:
            files = [file for file in os.listdir(input_dir)]

        if args.verbose:
            print('Input:               ', input_dir)
            print('Output:              ', output_dir)
            print('Rotate:              ', args.rotate)
            print('Resolution(s):       ', *resolutions, '\n')
            print(*files, sep='\n')
            if not args.yes:
                input('\nPress anything to continue, Ctrl+C to cancel...')

        start = time.perf_counter()

        # Process imagefiles
        action = 'Resizing' if args.resize else 'Cropping'
        for res in resolutions:
            with Bar('%s (%dx%d)' % (action, *res), max=len(files)) as bar:
                if args.organize:
                    save_to = os.path.join(output_dir, '%sx%s' % res)
                else:
                    save_to = output_dir
                if not os.path.exists(save_to):
                    os.mkdir(save_to)
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    def _helper(file):
                        return process_img(file, input_dir, save_to, res)
                    for file, success in zip(files, executor.map(_helper, files)):
                        # Count how many images skipped
                        if not success:
                            skipped += 1
                        bar.next()
        if skipped > 0:
            print(f'\nSkipped {skipped} file(s)')

        end = time.perf_counter()

        print(f'\nFinished in {(end-start):.2f} seconds')

    except KeyboardInterrupt:
        print('\nProcess cancelled\n')


def process_img(file, input_dir, save_to, res, quality=95):
    try:
        image = Image.open(os.path.join(input_dir, file))
        target_W, target_h = res
        width, height = image.size
        name, ext = os.path.splitext(file)

        # Skip images with resolution greater or equal to target resolution
        if args.crop and (target_W >= width or target_h >= height):
            return False

        image = resize(image, res) if args.resize else crop(image, res)

        # Add file suffix (resolution)
        if not args.organize:
            file = name + (f' - {target_W}x{target_h}') + ext

        image.save(os.path.join(save_to, file), image.format, quality=quality)
        return True     # Success

    except IOError as err:
        print('IOError:', err, 'Skipped')
        return False    # Skipped


def resize(image, res):
    max_width, max_height = res
    width, height = image.size
    resize_ratio = min(max_width/width, max_height/height)
    new_size = (math.floor(resize_ratio * width),
                math.floor(resize_ratio * height))
    return image.resize(new_size, Image.ANTIALIAS)


def crop(image, res):
    return ImageOps.fit(image, res, Image.ANTIALIAS, 0, (0.5, 0.5))


def rotate(image):

    return image


if __name__ == "__main__":
    main(sys.argv[1:])
