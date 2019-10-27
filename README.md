# PIR
Python Image Resizer

Small script for editing images in bulk or one by one

Supports: 
* Resizing without altering the aspect ratio,
* Cropping, crops images to the specified size, cropped from the middle
* Rotating, tries to rotate images the right way around (JPG only)

Supported filetypes are JPG/JPEG, PNG

## Getting Started

### Dependencies

* pip
* python 3.7+
* pillow 5.2+   https://github.com/python-pillow/Pillow

### Usage
```
python PIR.py [-h] -i INPUT -o OUTPUT [-y] [-v] [-O] [-q [1-95]]
              [-AA | -BC | -BL | -N] [-R] (-r | -c)
              resolution [resolution ...]
```

#### Options
```
Required
  -i INPUT, --input INPUT       Input file or folder
  -o OUTPUT, --output OUTPUT    Output folder
  resolution                    output resolutions, <width>x<height> OR <width>
  -r, --resize                  resize images, maintains aspect ratio
  OR
  -c, --crop                    crop images, centered, 
                                NOTE: Skips images with width OR height smaller or equal to target

Optional
  -h, --help                    show this help message and exit
  -q [1-95], --quality [1-95]   Picture quality, Value between 1-95, Default is 75
  
  Pick one:
  -AA, --antialias              Uses Antialias/Lanczos as resampler, Slow (DEFAULT)
  -BC, --bicubic                Uses Bicubic as resampler, Fast
  -BL, --bilinear               Uses Bilinear as resampler, Faster)
  -N, --nearest                 Uses Nearest as resampler, Fastest
  
  -v, --verbose                 Enable detailed logging
  -y, --yes                     Skip confirmation
  -O, --organize                Organize output resolutions in their own folders,
                                disables the resolution suffix on files
  -R, --rotate                  Rotate image(s) if neccesary, 
                                Useful phone pictures taken with a phone
```

#### Example 1. Crop images to 1280 by 720 and 500 by 500 resolutions

```
> python PIR.py -i .\input\ -o .\output\  1280x720 500 --crop --verbose          
  Input:                C:\Users\<user>\input
  Output:               C:\Users\<user>\output
  Rotate:               False
  Resolution(s):        (1280, 720) (500, 500)

  File(s):

   img1.png
   img2.jpg
   img3.jpg
   img4.jpeg
  
   4 file(s)

  Press any key to continue, Ctrl+C to cancel...

  Cropping (1280x720)     [##############################] 4/4
           Done, time elapsed: 0.38 seconds
  Cropping (500x500)      [##############################] 4/4
           Done, time elapsed: 0.31 seconds

  Skipped 1 file(s)

  Finished in 0.70 seconds
```
#### Result

Target Resolution: 1280x720

|    File    | Original Resolution | Final Resolution |   Note
| :--------: | :-----------------: | :--------------: | :------:
|  img1.png  |       839x1280      |        -         |  Skipped, Original width is lower than target
|  img2.jpg  |       1350x940      |     1280x720     |
|  img3.jpg  |       3840x2160     |     1280x720     |
|  img4.jpeg |       5400x3600     |     1280x720     |


Target Resolution: 500x500

|    File    | Original Resolution | Final Resolution |   Note
| :--------: | :-----------------: | :--------------: | :------------:
|  img1.png  |       839x1280      |     500x500      |
|  img2.jpg  |       1350x940      |     500x500      |
|  img3.jpg  |       3840x2160     |     500x500      |
|  img4.jpeg |       5400x3600     |     500x500      |


#### Example 2. Resize images to 420 resolution (width or height)
```
> python PIR.py -i .\input\ -o .\output\  420 --resize --rotate --verbose -y       
  Input:                C:\Users\<user>\\input
  Output:               C:\Users\<user>\output
  Rotate:               True
  Resolution(s):        (420, 420)

  File(s):

   img1.png
   img2.jpg
   img3.jpg
   img4.jpeg

   4 file(s)

  Resizing (420x420)      [##############################] 4/4
           Done, time elapsed: 0.37 seconds

  Finished in 0.37 seconds
```
#### Result

Target Resolution: 420

|    File    | Original Resolution | Final Resolution |   Note
| :--------: | :-----------------: | :--------------: | :-----------:
|  img1.png  |       839x1280      |     275x420      |
|  img2.jpg  |       940x1350      |     420x292      | Original is oriented incorrectly
|  img3.jpg  |       3840x2160     |     420x236      |
|  img4.jpeg |       5400x3600     |     420x280      |


#### Example 3. Convert folder full of highres images (792) to 1000x1000, 500x500 and 100x100 thumbnails
```
> python PIR.py -i ./input  -o ./output  1000 500 100  -cN    
  Cropping (1000x1000)    [##############################] 792/792
           Done, time elapsed: 23.28 seconds
  Cropping (500x500)      [##############################] 792/792
           Done, time elapsed: 21.74 seconds
  Cropping (100x100)      [##############################] 792/792
           Done, time elapsed: 20.91 seconds

  Finished in 65.94 seconds
```
