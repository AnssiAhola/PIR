#!/usr/bin/python3
from os import path, listdir, makedirs
from re import match
from sys import argv, stdout
from math import floor
from time import perf_counter
from argparse import ArgumentParser, ArgumentTypeError
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image, ImageOps, ExifTags, ImageFile, ImageSequence
from functools import reduce

# Fixes "IOError: broken data stream when reading image file" when loading files concurrently
ImageFile.LOAD_TRUNCATED_IMAGES = True

supported = ['.jpg', '.jpeg', '.png', '.gif']


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
    '-v', '--verbose', help='Enable detailed logging', action='store_true')
parser.add_argument(
    '-O', '--organize',
    help='Organize output resolutions in their own folders, disables the resolution suffix on files',
    action='store_true')

# Image processing arguments
parser.add_argument(
    '-q', '--quality',
    required=False,
    type=int,
    choices=range(1, 96),
    metavar='[1-95]',
    default=75,
    help='Picture quality, Value between 1-95, Default is 75')
quality = parser.add_mutually_exclusive_group()
quality.add_argument(
    '-AA', '--antialias', help='Uses Antialias/Lanczos as resampler, Slow (DEFAULT)', action='store_true')
quality.add_argument(
    '-BC', '--bicubic', help='Uses Bicubic as resampler, Fast', action='store_true')
quality.add_argument(
    '-BL', '--bilinear', help='Uses Bilinear as resampler, Faster)', action='store_true')
quality.add_argument(
    '-N', '--nearest', help='Uses Nearest as resampler, Fastest', action='store_true')
parser.add_argument(
    '-R', '--rotate', help='Rotate image(s) if neccesary, Useful for pictures taken with a phone', action='store_true')
actions = parser.add_mutually_exclusive_group(required=True)
actions.add_argument(
    '-r', '--resize', help='Resize images, maintains aspect ratio', action='store_true')
actions.add_argument(
    '-c', '--crop',
    help='crop images, centered, NOTE: Skips images with width OR height smaller or equal to target',
    action='store_true')

args = parser.parse_args()

SAMPLERS = {0: 'Nearest', 1: 'Antialias/Lanczos', 2: 'Bilinear', 3: 'Bicubic'}

if args.bicubic:
    resampler = Image.BICUBIC
elif args.bilinear:
    resampler = Image.BILINEAR
elif args.nearest:
    resampler = Image.NEAREST
else:
    resampler = Image.ANTIALIAS


def main(argv):
    skipped = 0
    try:
        input_dir = path.realpath(args.input)
        output_dir = path.realpath(args.output)
        resolutions = args.resolution

        # Convert resolutions to tuple of ints, 1920x1080 -> (1920,1080) and 100 -> (100,100)
        for i, res in enumerate(resolutions):
            resolutions[i] = tuple(map(lambda r: int(r), res.split('x')))
            if len(resolutions[i]) == 1:
                resolutions[i] = (resolutions[i][0], resolutions[i][0])

        # Get list of Files
        if path.isdir(input_dir):
            files = listdir(input_dir)
        else:
            files = [input_dir.split('\\')[-1]]
            # Single file as input so get the directory
            input_dir = path.dirname(args.input)

        # Filter out unsupported files
        files = [file for file in files if any(
            ext in file for ext in supported)]

        file_count = len(files)
        if file_count == 0:
            raise OSError(0, 'Input filetype is not supported')

        if args.verbose:
            print('Input:               ', input_dir)
            print('Output:              ', output_dir)
            print('Rotate:              ', args.rotate)
            print('Resampler:           ', SAMPLERS[resampler])
            print('Quality:             ', args.quality)
            print('Resolution(s):       ', *resolutions, '\n')
            print('File(s):\n', *files, sep='\n ')
            print(f'\n {file_count} file(s)\n')
            if not args.yes:
                input('Press enter to continue, Ctrl+C to cancel...\n')

        start = perf_counter()

        # Process image files
        print()
        action = 'Resizing' if args.resize else 'Cropping'
        for res in resolutions:
            res_start = perf_counter()

            with ProgressBar(file_count, '%s (%dx%d)\t' % (action, *res), 30) as bar:
                # Determine where to save images ./output/ or ./output/resolution
                save_to = path.join(output_dir,
                                    '%sx%s' % res) if args.organize else output_dir
                makedirs(save_to, exist_ok=True)

                with ThreadPoolExecutor(max_workers=6) as executor:
                    # Helper to pass rest of the arguments needed
                    def _helper(file):
                        return process_img(file, input_dir, save_to, res)
                    # Process images concurrently
                    for file, success in zip(files, executor.map(_helper, files)):
                        if not success:
                            skipped += 1
                        bar.next()

            res_end = perf_counter()
            print(f'\t Done, time elapsed: {(res_end-res_start):.2f} seconds')

        if skipped > 0:
            print(f'\nSkipped {skipped} file(s)')

        end = perf_counter()
        print(f'\nFinished in {(end-start):.2f} seconds\n')

    except KeyboardInterrupt:
        print('\nProcess cancelled\n')
    except OSError as err:
        print(err)


# Progress bar, modified for concurrency from https://stackoverflow.com/a/34482761
class ProgressBar():
    def __init__(self, count, prefix="", size=60):
        self.count = count
        self.completed = 0
        self.prefix = prefix
        self.size = size
        self.file = stdout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def next(self):
        self.file.flush()
        self.completed += 1
        self.x = int(self.size*self.completed/self.count)
        self.file.write("%s[%s%s] %i/%i\r" %
                        (self.prefix, "#"*self.x, "."*(self.size-self.x), self.completed, self.count))
        if self.completed == self.count:
            self.file.write("\n")


def process_img(file, input_dir, output_dir, res, quality=args.quality):
    try:
        image = Image.open(path.join(input_dir, file))
        target_W, target_h = res
        width, height = image.size
        name, ext = path.splitext(file)

        # Process GIFs seperately
        if image.format == 'GIF':
            frames = process_gif(image, res)  # returns iterator
            output = next(frames)  # get the first frame
            output.info = image.info  # copy image info
            if not args.organize:
                file = name + (' - %dx%d' % output.size) + ext
            output.save(  # save GIF and append rest of the frames to it
                path.join(output_dir, file), save_all=True, append_images=list(frames), optimize=True)
            return True

        # When cropping skip images with resolution smaller or equal to target resolution
        if args.crop and (target_W >= width or target_h >= height):
            return False

        if args.rotate:
            image = rotate(image)
        if args.resize:
            image = resize(image, res)
        elif args.crop:
            image = ImageOps.fit(image, res, resampler, 0, (0.5, 0.5))

        # Add file suffix (resolution)
        if not args.organize:
            file = name + (' - %dx%d' % image.size) + ext

        image.save(
            path.join(output_dir, file), image.format,
            quality=quality, optimize=True)
        return True     # Success

    except IOError as err:
        print('IOError:', err, 'Skipped')
        return False    # Skipped


# https://gist.github.com/skywodd/8b68bd9c7af048afcedcea3fb1807966
# Results in larger filesizes relative to original
def process_gif(image, res):
    frames = ImageSequence.Iterator(image)

    def thumbnails(frames):
        for frame in frames:
            thumbnail = frame.copy()
            thumbnail.thumbnail(res, resampler)
            yield thumbnail
    frames = thumbnails(frames)
    return frames


def resize(image, res):
    max_width, max_height = res
    width, height = image.size
    resize_ratio = min(max_width/width, max_height/height)
    new_size = (floor(resize_ratio * width), floor(resize_ratio * height))
    return image.resize(new_size, resampler)


# Supports JPG/JPEG only
def rotate(image):
    # Source:               https://stackoverflow.com/a/30462851
    # Orientation Tag From: https://github.com/python-pillow/Pillow/blob/master/src/PIL/ExifTags.py
    exif_orientation_tag = 0x0112
    exif_transpose_sequences = [                    # Val 0th row  0th col
        [],                                         # 0     (reserved)
        [],                                         # 1   top      left
        [Image.FLIP_LEFT_RIGHT],                    # 2   top      right
        [Image.ROTATE_180],                         # 3   bottom   right
        [Image.FLIP_TOP_BOTTOM],                    # 4   bottom   left
        [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],   # 5   left     top
        [Image.ROTATE_270],                         # 6   right    top
        [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],   # 7   right    bottom
        [Image.ROTATE_90]                           # 8   left     bottom
    ]

    try:
        seq = exif_transpose_sequences[image._getexif()[exif_orientation_tag]]
    except Exception as err:
        return image
    else:
        return reduce(type(image).transpose, seq, image)


if __name__ == "__main__":
    main(argv[1:])
