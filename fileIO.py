import subprocess
from datetime import datetime
import os
import glob


class iRodsGetter:
    """ A class to extract files on SR1 using the irods interface."""

    def __init__(self, workdir='/cunyZone/home/luis.ortiz/forecast/'):
        self.workdir = workdir

    def getFiles(self, date, dateobj=True, prefix='wrfout', dom='d03'):

        if dateobj is True:
            # If date is a datetime object, let's convert it to a string
            # representation following the WRF filename format. Each wrffile
            # is housed in a directory in the format YYYYMMDD/
            wrfdatefmt = '%Y-%m-%d_%H:%M:%S'
            dirfmt = '%Y%m%d/'

        # Build the WRF output filename
        timestamp = date.strftime(wrfdatefmt)
        datadir = date.strftime(dirfmt)
        filetoget = self.workdir + datadir + '_'.join([prefix,
                                                      dom,
                                                      timestamp])
        print filetoget
        # Call the iRods iget command to transfer the file to the cwd
        subprocess.call(['iget', '-Pv', filetoget])

        return None


class wrfFileGetter:
    """ A class to extract WRF output files from the forecast that live
        on the current machine.
    """

    def __init__(self,
                 workdir='/scratch/luis.ortiz/forecast/',
                 period='24hr'):

        self.workdir = workdir
        self.period = period

    def getFiles(self, date, dateobj=True, prefix='wrfout', dom='d03'):

        if dateobj is True:
            # If date is a datetime object, let's convert it to a string
            # representation following the WRF filename format. Each wrffile
            # is housed in a directory in the format YYYYMMDD/
            wrfdatefmt = '%Y-%m-%d_%H:%M:%S'
            dirfmt = '%Y%m%d/'

        # Build the WRF output filename
        timestamp = date.strftime(wrfdatefmt)
        datadir = date.strftime(dirfmt)
        filetoget = self.workdir + datadir + '_'.join([prefix,
                                                      dom,
                                                      timestamp])
        print filetoget

        subprocess.call(['ln', '-sf', filetoget])

    def getTodayFcst(self,
                     workdir='/scratch/luis.ortiz/fcsteval/',
                     dom='d03'):
        today = datetime.today().strftime('%Y%m%d')

        datadir = '/'.join(['/scratch', 'luis.ortiz', 'forecast', today])

        os.chdir(workdir)
        filelist = glob.glob(datadir + '/wrfout_' + dom + '*')
        for f in filelist:
            subprocess.call(['ln', '-sf', datadir + '/' + f])
