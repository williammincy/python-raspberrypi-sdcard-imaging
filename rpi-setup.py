import plistlib
import urllib2
import os
import sys
import click
import subprocess
import zipfile
import datetime, time

outputfilename = "rpi"
dir_path = os.getcwd()
raspbian = [{"url":"https://downloads.raspberrypi.org/raspbian_latest","descr":"(Full version of OS)"},{"url":"https://downloads.raspberrypi.org/raspbian_lite_latest","descr":"(Lite version of OS)"}]

def print_choose_disk():
    dc = 1
    disks = pl['AllDisksAndPartitions']
    actualdisks = []
    click.secho("Enter number of volume you want to use for Raspberry Pi installation:", fg='green')
    for disk in disks:
        if "Partitions" in disk:
            actualdisks.append(disk)
            partitions = disk["Partitions"]
            click.secho(" "+" "+str(dc)+": "+disk["DeviceIdentifier"]+" "+"("+partitions[0]["Content"]+")", fg='green')
            dc += 1
    rawresult = input()
    try:
        result = int(rawresult)
    except:
        result = 0

    if result < 1 or result > dc:
        sys.stdout.flush()
        click.secho("Sorry, "+str(rawresult)+" is not a valid choice", fg='red')
        return print_choose_disk()
    else:
        sys.stdout.flush()
        return actualdisks[result-1]

def print_choose_diskimage():
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

def install_rpi_image(diskpath, diskimage):
    click.secho("Unmounting disk", fg='green')
    subprocess.call(["diskutil","unmountDisk","/dev/"+diskpath])
    click.secho("Imaging SD card, this may take 15 to 20 minutes depeding on the size of your SD card", fg='green')
    subprocess.call(["sudo","dd","bs=1m","if="+diskimage,"of=/dev/"+diskpath])
    click.secho("Cleaning up", fg='green')
    subprocess.Popen("rm -Rf "+diskimage)
    click.secho("Complete", fg='green')

def dl_rpi_image(url, filename):
    data = None
    click.secho("Downloading Raspbian Image, this may take a few minutes", fg='green')
    req = urllib2.urlopen(url)
    fo = open(filename+".zip", "wb")
    fo.write(req.read())
    fo.close()
    click.secho("Unzipping archive", fg='green')
    with zipfile.ZipFile(filename+".zip", "r") as z:
        z.extractall(filename+".img")
    subprocess.call(["rm","-Rf",filename+".zip"])

if __name__ == "__main__":
    try:
        startTime = datetime.datetime.now()
        click.secho("Starting at "+startTime.strftime("%I:%M %p"), fg='blue')
        
        output = subprocess.check_output(["diskutil","list","-plist"])
        pl = plistlib.readPlistFromString(output)
        if len(pl['AllDisksAndPartitions']) > 0:
            disk = print_choose_disk()
            img = print_choose_diskimage()
            dl_rpi_image(img["url"], outputfilename)
            install_rpi_image(disk['DeviceIdentifier'], outputfilename+".img")
            endTime = datetime.datetime.now()
            difftime = endTime - startTime
            
            click.secho("Completed at "+endTime.strftime("%I:%M %p"), fg='blue')
            click.secho("Process took "+str(difftime), fg='blue')
        else:
            print "No disks or volumes found"
    except:
        sys.stdout.write('\r'+"Cancelling\n\n") 
        sys.exit(0)