#!/usr/bin/python3
from os import path, listdir, mkdir
from re import match
from sys import argv
from math import floor
from time import perf_counter
from argparse import ArgumentParser, ArgumentTypeError
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from progress.bar import Bar
from PIL import Image, ImageOps, ExifTags, ImageFile

# Fixes "IOError: broken data stream when reading image file" when loading files concurrently
ImageFile.LOAD_TRUNCATED_IMAGES = True

supported = ['.jpg', '.jpeg', '.png']


# Check if input folder/file exists
def exists(s):
    if not path.exists(s):
        raise ArgumentTypeError('path does not exist')
    else:
        return s


# Validate resolution (WidthxHeight OR Width)
def resolution(res):
    if match(r'^[0-9]+x*[0-9]+$', res):
        return res
    else:
        raise ArgumentTypeError('&d' % res)


parser = ArgumentParser(
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
    help='Organize output resolutions in their own folders, disables the resolution suffix on files',
    action='store_true')

# Image processing arguments
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument(
    '--rotate', help='Rotate image(s) if neccesary', action='store_true')
group.add_argument(
    '--resize', help='resize images, maintains aspect ratio', action='store_true')
group.add_argument(
    '--crop',
    help='crop images, centered, NOTE: Skips images with width OR height smaller or equal to target',
    action='store_true')

args = parser.parse_args()


def main(argv):
    skipped = 0
    try:
        input_dir = path.realpath(args.input)
        output_dir = path.realpath(args.output)
        resolutions = args.resolution
        for i, res in enumerate(resolutions):
            resolutions[i] = tuple(map(lambda r: int(r), res.split('x')))
            if len(resolutions[i]) is 1:
                resolutions[i] = (resolutions[i][0], resolutions[i][0])

        # Filter out unsupported files
        if any(ext in input_dir for ext in supported):
            files = [input_dir.split('\\')[-1]]
            input_dir = path.dirname(path.realpath(args.input))
        elif path.isdir(input_dir):
            files = [file for file in listdir(input_dir) if any(
                ext in file for ext in supported)]
        else:
            raise OSError(0, 'Input filetype is not supported')

        if args.verbose:
            print('Input:               ', input_dir)
            print('Output:              ', output_dir)
            print('Rotate:              ', args.rotate)
            print('Resolution(s):       ', *resolutions, '\n')
            print('File(s):\n', *files, sep='\n ')
            print()
            if not args.yes:
                input('Press any key to continue, Ctrl+C to cancel...')

        start = perf_counter()

        # Process imagefiles
        action = 'Resizing' if args.resize else 'Cropping'
        for res in resolutions:
            with Bar('%s (%dx%d)' % (action, *res), max=len(files)) as bar:
                if args.organize:
                    output_dir = path.join(output_dir, '%sx%s' % res)
                else:
                    output_dir = output_dir
                if not path.exists(output_dir):
                    mkdir(output_dir)
                with ThreadPoolExecutor(max_workers=6) as executor:
                    def _helper(file):
                        return process_img(file, input_dir, output_dir, res)
                    for file, success in zip(files, executor.map(_helper, files)):
                        # Count how many images skipped
                        if not success:
                            skipped += 1
                        bar.next()
        if skipped > 0:
            print(f'\nSkipped {skipped} file(s)')

        end = perf_counter()

        print(f'\nFinished in {(end-start):.2f} seconds')

    except KeyboardInterrupt:
        print('\nProcess cancelled\n')
    except OSError as err:
        print(err)


def process_img(file, input_dir, output_dir, res, quality=95):
    try:
        image = Image.open(path.join(input_dir, file))
        target_W, target_h = res
        width, height = image.size
        name, ext = path.splitext(file)

        # When cropping skip images with resolution smaller or equal to target resolution
        if args.crop and (target_W >= width or target_h >= height):
            return False

        if args.resize:
            image = resize(image, res)
        elif args.crop:
            image = ImageOps.fit(image, res, Image.ANTIALIAS, 0, (0.5, 0.5))
        if args.rotate:
            image = rotate(image)

        # Add file suffix (resolution)
        if not args.organize:
            file = name + (' - %dx%d' % image.size) + ext

        image.save(path.join(output_dir, file), image.format, quality=quality)
        return True     # Success

    except IOError as err:
        print('IOError:', err, 'Skipped')
        return False    # Skipped


def resize(image, res):
    max_width, max_height = res
    width, height = image.size
    resize_ratio = min(max_width/width, max_height/height)
    new_size = (floor(resize_ratio * width), floor(resize_ratio * height))
    return image.resize(new_size, Image.ANTIALIAS)


def rotate(image):
    try:
        # https://stackoverflow.com/a/6218425
        # key = orientation value from images exif tags
        # value = degrees to to rotate the image for correct orientation
        degrees = {3: 180, 6: 270, 8: 90}
        # https://github.com/python-pillow/Pillow/blob/master/src/PIL/ExifTags.py
        # Constant for exif tag for Orientation
        ORIENTATION = 0x0112

        exif_data = dict(image._getexif().items())
        deg_to_rotate = degrees[exif_data[ORIENTATION]]

        image = image.rotate(deg_to_rotate, expand=True)
    finally:
        return image


if __name__ == "__main__":
    main(argv[1:])
