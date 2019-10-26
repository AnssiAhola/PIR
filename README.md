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
PIR.py [-h] -i INPUT -o OUTPUT resolution [resolution ...] (--resize | --crop) [--verbose] [-y] [--organize] [--rotate] 
              
              
```



Options
```
-h, --help                    show this help message and exit

-i INPUT, --input INPUT       Input file or folder
-o OUTPUT, --output OUTPUT    Output folder
resolution                    output resolutions, <width>x<height> OR <width>

--rotate                      Rotate image(s) if neccesary

--resize                      resize images, maintains aspect ratio
--crop                        crop images, centered, NOTE: Skips images with width OR height smaller or equal to target
Either resize OR crop argument is required

-y, --yes                     Skip confirmation
--verbose                     Enable detailed logging
--organize                    Organize output resolutions in their own folders,
                              disables the resolution suffix
--rotate                      Rotate image(s) if neccesary
--resize                      resize images, maintains aspect ratio
--crop                        crop images, centered, NOTE: Skips images with width OR height smaller or equal to target
```

Crop images inside a folder to 1280 by 720 and 500 by 500 resolutions
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
Note, 1 file was skipped because its width or height was equal or smaller than target 


## License

This project is licensed under the MIT License - see the LICENSE.md file for details
