# Python Raspberry Pi Disk Image Installer 

I created this project because I have provisioned more than a few SD cards for use in a Raspberry Pi, and wanted a simple and reliable script to do this whenever needed rather than having to look up the installation steps each time.

Please feel free to use this as you like, fork, or submit pull requests to make it better. 

## Requirements 

The requirements are very small to run this. You'll need: 

  - Python 2.7
  - pip package for click
  - SD card reader
  - SD card
  - 6GB free disk space

It's also worth mentioning that you should be able to `sudo` since some of the commands will require this to work properly.

### Instructions

Once you've cloned/downloaded the repository you'll need to also install the `pip` packages needed to run the script

```
   pip install click hurry.filesize
```

At this point you should prepare your SD card that you want to use by formatting it. Once done, you can initiate the script: 

```
   python rpi-setup.py
```

The script takes you through selecting the disk from those available and picking the RPi disk image to install. More information about the difference between the two can be found on the [Raspberry Pi website](https://www.raspberrypi.org/downloads/raspbian/). From there it will download the appropriate disk image, format the SD card if you enabled that option, and complete the installation.

After successfully installing the disk image onto the SD card the script will clean up after itself, removing the zip and disk image files from your computer.

At this point you are good to eject the SD card and begin using it in your Raspberry Pi.