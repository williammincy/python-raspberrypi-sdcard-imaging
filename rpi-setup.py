import plistlib
import urllib2
import os
import sys
from hurry.filesize import size
import click
import subprocess
import zipfile
import datetime, time

outputfilename = "rpi"
raspbian = [{"url":"https://downloads.raspberrypi.org/raspbian_latest","descr":"(Full version of OS)"},{"url":"https://downloads.raspberrypi.org/raspbian_lite_latest","descr":"(Lite version of OS)"}]

def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % 
       (bytes_so_far, total_size, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, chunk_size=8192, report_hook=None):
   total_size = response.info().getheader('Content-Length').strip()
   total_size = int(total_size)
   bytes_so_far = 0
   imagefile = ''

   while 1:
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      imagefile += chunk
      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size)
   
   return imagefile 

def print_choose_disk():
    try:
        dc = 1
        disks = pl['AllDisksAndPartitions']
        actualdisks = []
        click.secho("Enter number of volume you want to use for Raspberry Pi installation:", fg='green')
        for disk in disks:
            partitionInfo = " (???)"
            if "Partitions" in disk:
                partitionInfo = " ("+disk["Partitions"][-1]["VolumeName"]+")"
            actualdisks.append(disk)
            click.secho(" "+" "+str(dc)+": "+disk["DeviceIdentifier"]+" - "+size(disk["Size"])+partitionInfo, fg='green')
            dc += 1
        rawresult = raw_input()
        try:
            result = int(rawresult)
        except:
            result = 0

        if result < 1 or result > dc:
            click.secho("Sorry, "+str(rawresult)+" is not a valid choice", fg='red')
            return print_choose_disk()
        else:
            return actualdisks[result-1]
    except KeyboardInterrupt:
        sys.stdout.write('\r'+"")
        sys.exit(0)

def print_choose_diskimage():
    try:
        click.secho("Choose your version of Raspbian:", fg='green')
        rc = 1
        for img in raspbian:
            click.secho(" "+" "+str(rc)+": "+img["url"]+" "+img["descr"], fg='green')
            rc += 1
        rawresult = input()
        try:
            result = int(rawresult)
        except:
            result = 0
        
        if result < 1 or result > 2:
            sys.stdout.flush()
            click.secho("Sorry, "+str(rawresult)+" is not a valid choice", fg='red')
            return print_choose_diskimage()
        else:
            return raspbian[result-1]
    except KeyboardInterrupt:
        sys.stdout.write('\r'+"")
        sys.exit(0)

def print_format_disk():
    click.secho("Would you like to format the disk? y/n", fg='green')
    try:
        rawresult = raw_input()
        result = str(rawresult).lower()
        if result == "y":
            return 1
        elif result == "n":
            return 0
        else:
            sys.stdout.write("Invalid option ")
            print_format_disk()
    except KeyboardInterrupt:
        sys.stdout.write('\r'+"")
        sys.exit(0)
    except:
        sys.stdout.write("Invalid option ")
        print_format_disk()

def install_rpi_image(diskpath, shouldFormatDisk, diskimage):
    click.secho("Unmounting disk", fg='green')
    subprocess.call(["diskutil","unmountDisk","/dev/"+diskpath])
    if shouldFormatDisk == 1:
        click.secho("Formatting SD card, please wait a moment", fg='green')
        subprocess.call(["sudo","diskutil","partitionDisk","/dev/"+diskpath,"1 MBR","free","\"%noformat%\"","100%"])
    click.secho("Imaging SD card, this may take 15 minutes or more depeding on the size of your SD card", fg='green')
    subprocess.call(["sudo","dd","bs=1m","if="+diskimage,"of=/dev/"+diskpath])
    click.secho("Cleaning up", fg='green')
    subprocess.call(["rm","-Rf",diskimage])
    click.secho("Complete", fg='green')

def dl_rpi_image(url, filename):
    data = None
    click.secho("Downloading Raspbian Image, this may take a few minutes", fg='green')
    req = urllib2.urlopen(url)
    imagefile = chunk_read(req, report_hook=chunk_report)
    fo = open(filename+".zip", "wb")
    fo.write(imagefile)
    fo.close()
    click.secho("Unzipping archive, this may take a moment", fg='green')
    dimagename = ''
    with zipfile.ZipFile(filename+".zip", "r") as z:
        dimage = [item for item in z.infolist() if item.filename.endswith('.img')][-1]
        dimagename = dimage.filename
        z.extract(dimage)
    subprocess.call(["mv",dimagename,outputfilename+".img"])
    subprocess.call(["rm","-Rf",filename+".zip"])

if __name__ == "__main__":
    # try:
    startTime = datetime.datetime.now()
    click.secho("Starting at "+startTime.strftime("%I:%M %p"), fg='blue')
    
    output = subprocess.check_output(["diskutil","list","-plist"])
    pl = plistlib.readPlistFromString(output)
    if len(pl['AllDisksAndPartitions']) > 0:
        disk = print_choose_disk()
        shouldFormatDisk = print_format_disk()
        img = print_choose_diskimage()
        dl_rpi_image(img["url"], outputfilename)
        install_rpi_image(disk['DeviceIdentifier'], shouldFormatDisk, outputfilename+".img")
        endTime = datetime.datetime.now()
        difftime = endTime - startTime
        
        click.secho("Completed at "+endTime.strftime("%I:%M %p"), fg='blue')
        click.secho("Process took "+str(difftime), fg='blue')
    else:
        print "No disks or volumes found"
    # except:
    #     sys.stdout.write('\r'+"Cancelling\n\n") 
    #     sys.exit(0)