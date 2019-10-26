# PIR
Python Image Resizer

Small script for editing images in bulk or one by one

Supports: 
* Resizing without altering the aspect ratio,
* Cropping, crops images to the specified size, cropped from the middle
* Rotating, rotates images so they are oriented correctly

Supported filetypes are JPG/JPEG, PNG

## Getting Started

### Dependencies

* pip
* python 3.7+
* pillow 6.2+   https://github.com/python-pillow/Pillow
* progress 1.5+ https://github.com/verigak/progress/

### Usage
```
python PIR.py -i INPUT -o OUTPUT [resolution ...] (--resize | --crop) --verbose -y --organize --rotate
```

#### Options
```
Required
  -i INPUT, --input INPUT       Input file or folder
  -o OUTPUT, --output OUTPUT    Output folder
  resolution                    output resolutions, <width>x<height> OR <width>
  --resize                      resize images, maintains aspect ratio
  OR
  --crop                        crop images, centered, 
                                NOTE: Skips images with width OR height smaller or equal to target

Optional
  -h, --help                    show this help message and exit
  --verbose                     Enable detailed logging
  -y, --yes                     Skip confirmation
  --organize                    Organize output resolutions in their own folders,
                                disables the resolution suffix on files
  --rotate                      Rotate image(s) if neccesary
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
  
  Press anything to continue, Ctrl+C to cancel...
  
  Cropping (1280x720) |################################| 4/4
  Cropping (500x500) |################################| 4/4

  Skipped 1 file(s)

  Finished in 0.72 seconds
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
  Input:                C:\Users\Anssi\Documents\Repos\PIR\input
  Output:               C:\Users\Anssi\Documents\Repos\PIR\output
  Rotate:               True
  Resolution(s):        (420, 420)

  File(s):

   img1.png
   img2.jpg
   img3.jpg
   img4.jpeg

  Cropping (420x420) |################################| 4/4

  Finished in 0.32 seconds
```
#### Result

Target Resolution: 420

|    File    | Original Resolution | Final Resolution |   Note
| :--------: | :-----------------: | :--------------: | :-----------:
|  img1.png  |       839x1280      |     275x420      |
|  img2.jpg  |       940x1350      |     420x292      | Original is oriented incorrectly
|  img3.jpg  |       3840x2160     |     420x236      |
|  img4.jpeg |       5400x3600     |     420x280      |


