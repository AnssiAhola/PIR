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


def main():
    skipped = 0

    input_dir, filelist = get_realinput_and_filelist(args.input)
    options = {
        'input': input_dir,
        'output': path.realpath(args.output),
        'resolutions': parse_resolutions(args.resolution),
        'quality': args.quality,
        'filelist': filelist,
        'filecount': len(filelist),
        'rotate': args.rotate,
        'organize': args.organize,
        'resample': resampler,
        'skip': args.yes,
        'action': 'Resizing' if args.resize else 'Cropping',
    }

    if options['filecount'] == 0:
        raise OSError(0, 'Input filetype is not supported')

    try:

        if args.verbose:
            print('Input:               ', options['input'])
            print('Output:              ', options['output'])
            print('Rotate:              ', options['rotate'])
            print('Resampler:           ', SAMPLERS[options['resample']])
            print('Quality:             ', options['quality'])
            print('Resolution(s):       ', *options['resolutions'], '\n')
            print('File(s):\n', *options['filelist'], sep='\n ')
            print(f"\n {options['filecount']} file(s)\n")
            if not options['skip']:
                input('Press enter to continue, Ctrl+C to cancel...\n')

        start = perf_counter()

        # Process image files, return list of skipped files
        skipped = process_files(options)
        if len(skipped) > 0:
            print(f'\nSkipped {len(skipped)} file(s)')
            print(*skipped, sep='\n')

        end = perf_counter()
        print(f'\nFinished in {(end-start):.2f} seconds\n')

    except KeyboardInterrupt:
        print('\nProcess cancelled\n')
    except OSError as err:
        print(err)


def process_files(opts):
    skipped = []
    for res in opts['resolutions']:
        res_start = perf_counter()

        with ProgressBar(opts['filecount'], '%s (%dx%d)\t' % (opts['action'], *res), 30) as bar:
            # Determine where to save images ./output/ or ./output/resolution
            save_to = path.join(opts['output'], '%sx%s' %
                                res) if opts['organize'] else opts['output']
            makedirs(save_to, exist_ok=True)

            with ThreadPoolExecutor(max_workers=6) as executor:
                # Helper to pass rest of the arguments needed
                def _helper(file):
                    return process_img(file, save_to, res, opts)
                # Process images concurrently
                for file, success in zip(opts['filelist'], executor.map(_helper, opts['filelist'])):
                    if not success:
                        skipped.append(file)
                    bar.next()

        res_end = perf_counter()
        print(f'\t Done, time elapsed: {(res_end-res_start):.2f} seconds')
    return skipped


def get_realinput_and_filelist(input_directory):
    real_input = path.realpath(input_directory)
    if path.isdir(real_input):
        filelist = listdir(real_input)
    else:
        filelist = [real_input.split('\\')[-1]]
        # Single file as input so get the directory
        real_input = path.dirname(input_directory)

    # Filter out unsupported files
    filelist = [file for file in filelist if any(
        ext in file for ext in supported)]
    return (real_input, filelist)


# Convert resolutions to tuple of ints, 1920x1080 -> (1920,1080) and 100 -> (100,100)
def parse_resolutions(arrRes):
    for i, res in enumerate(arrRes):
        arrRes[i] = tuple(map(lambda r: int(r), res.split('x')))
        if len(arrRes[i]) == 1:
            arrRes[i] = (arrRes[i][0], arrRes[i][0])
    return arrRes


# Progress bar, modified for concurrency from https://stackoverflow.com/a/34482761
class ProgressBar:
    def __init__(self, count, prefix="", size=60):
        self.count = count
        self.completed = 0
        self.prefix = prefix
        self.size = size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def next(self):
        stdout.flush()
        self.completed += 1
        x = int(self.size*self.completed/self.count)
        progress = f"{'#'*x}{'.'*(self.size-x)}"
        stdout.write(
            f"{self.prefix}[{progress}] {self.completed}/{self.count}\r")
        if self.completed == self.count:
            stdout.write("\n")


def process_img(file, output_dir, res, opts):
    try:
        image = Image.open(path.join(opts['input'], file))
        target_w, target_h = res
        width, height = image.size
        name, ext = path.splitext(file)

        if image.format == 'GIF':
            process_gif(image, file, res, output_dir, name, ext)
            return True

        # When cropping skip images with resolution smaller or equal to target resolution
        if args.crop and (target_w >= width or target_h >= height):
            return False

        if opts['rotate']:
            image = rotate(image)
        if opts['action'] == 'Resizing':
            image = resize(image, res)
        else:
            image = ImageOps.fit(image, res, opts['resample'], 0, (0.5, 0.5))

        # Add file suffix (resolution)
        if not opts['organize']:
            file = name + (' - %dx%d' % image.size) + ext

        image.save(
            path.join(output_dir, file), image.format,
            quality=opts['quality'], optimize=True)
        return True     # Success

    except IOError as err:
        print('IOError:', err, 'Skipped')
        return False    # Skipped


# https://gist.github.com/skywodd/8b68bd9c7af048afcedcea3fb1807966
# Results in larger filesizes relative to original
def process_gif(image, filename, res, output, name, ext):
    frames = ImageSequence.Iterator(image)

    def thumbnails(frames_):
        for frame in frames_:
            thumbnail = frame.copy()
            thumbnail.thumbnail(res, resampler)
            yield thumbnail

    frames = thumbnails(frames)
    image_out = next(frames)  # get the first frame
    image_out.info = image.info  # copy image info
    if not args.organize:
        filename = name + (' - %dx%d' % image_out.size) + ext
    image_out.save(  # save GIF and append rest of the frames to it
        path.join(output, filename), save_all=True, append_images=list(frames), optimize=True)


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
        return reduce(type(image).transpose, seq, image)
    except:
        return image


if __name__ == "__main__":
    main()
