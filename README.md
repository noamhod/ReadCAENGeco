# ReadCAENGeco
Script to read GECO log files from CAEN power supply modules.
The GECO software runs on windows only unfortunately.
In principle the script works out of the box on linux/mac.
If you copy the log files to these machines then you should only execute the script.
If you can only run on windows, the points below describe how to do this...

- Install VirtualBox
- Create a new image and install Ubuntu
- after installing Ubuntu
    - get ROOT from the main repository...
    - sudo apt-get install libc++
    - sudo apt install python2.7 python-pip
    - sudo apt-get install libtbb-dev
- Before trying to mount the shared folder: go to the virtual machine --> Devices -->Insert Guest Additions CD... --> Run

To prepare the files on the Windows host:
- make a new folder on your windows system and call it "shared" (can be anything else but below I use it)
- copy all files from this rep, including your data log file to: C:\path\to\your\shared\

To setup root on the Ubuntu guest:
- open the Ubuntu image in VirtualBox (start it if it is stopped)
- in Ubuntu open the Terminal application
- from the home directory, mount the shared folder:
    - To go to home:     cd
    - Make the work dir: mkdir -p Downloads/shared
    - To mount:          sudo mount -t vboxsf shared Downloads/shared
    - Move there:        cd Downloads/shared/
    - Setup ROOT:        source setup.sh

To run the script, just do for example:
- python readCAEN.py  -f  your-GECO-log-file-name.log  -c 4-7  -l  100
- python readCAEN.py  -f  your-GECO-log-file-name.log  -c 4-7

The parameters are:
- the -f parameter is your data log file name from GECO.
- the -c parameter is the channel range used in your power supply, e.g. 0-3, 4-7, etc.
- the -l parameter is controlling how many x-labels are printed in the plots.
- the -t parameter is a cut on the time window presented
- the -s parameter is a setting for the currents y-axis scale
