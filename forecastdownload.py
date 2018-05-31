import urllib
from datetime import datetime
import time

try:
    # Check that tqdm exists
    from tqdm import tqdm
except ImportError:
    'tqdm not found. Re-install using conda or pip'

class GRIBDownloader:
    """ A class to set up downloads from the NCEP NOMADS server. Specifically,
        to download GRIB files to initialize WRF forecast runs at the
        NYC-MetNet

        KWARGS:
        -------
        model: Model source for the grib files. Default is NAM
        date: either the string 'today' or a datetime object. When 'today'
              is used, it fetches the current year-month-day from the server.
    """

    def __init__(self, model='NAM', date='today'):

        self.model = model
        source_list = ('NAM', 'GFS')

        # Some preliminary error checking
        assert model in source_list, model + ' not supported!'
        assert (date is 'today') or isinstance(date, datetime), ('Bad date!')

        # The source URL for our data
        source_root = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/'
        source = {'NAM': source_root + 'nam/prod/nam.',
                  'GFS': source_root + 'gfs/prod/gfs.'}

        # Extract the time information to build the correct URL and filenames.
        if date is 'today':
            dtobj = datetime.today()
            self.day = dtobj.strftime('%d')
            self.month = dtobj.strftime('%m')
            self.year = dtobj.strftime('%Y')
        else:
            self.day = date.strftime('%d')
            self.month = date.strftime('%m')
            self.year = date.strftime('%Y')

        self.url = source[model] + self.year + self.month + self.day + '/'

    def getFiles(self, inittime='00', maxtries=5, sleep=10):

        """ This method fetches the actual files from the NOMADS server.
            It will retrieve 3-hourly files at the forecast initialization
            time provided.

            KWARGS:
            -------
            inittime: zero-padded string indicating initialization time of the
            forecast
        """

        fcast = ['0' + str(n) if len(str(n)) == 1 else str(n)
                 for n in range(0, 85, 3)]

        # We use urllib to download the files. Create an instance of the URL
        # opener
        getter = urllib.URLopener()

        if self.model is 'NAM':

            # Build the file names.
            self.fname = ['.'.join([self.model.lower(),
                                    't' + inittime + 'z',
                                    'awphys' + n,
                                    'tm00',
                                    'grib2'])
                          for n in fcast]

        if self.model is 'GFS':
            self.url = self.url[:-1] + inittime + '/'
            self.fname = ['.'.join([self.model.lower(),
                                    't' + inittime + 'z',
                                    'pgrb2',
                                    '0p50',
                                    'f0' + n])
                          for n in fcast]
        tries = 0

        # Download the files. It will try for a few times,  then time out.
        for f in tqdm(self.fname):

            try:
                getter.retrieve(self.url + f, f)

            except IOError:
                while tries < maxtries:
                    tries = tries + 1
                    print 'File not found, trying again in ' + str(sleep)
                    time.sleep(sleep*60)  # arg for time.sleep in seconds

                    getter.retrieve(self.url + f, f)

                    if tries == maxtries:
                        print 'Max tries exceeded, check logs!'
                        with open('download.log', 'w') as log:
                            log.write('Could not find '
                                      + self.model + ' files\n')
                        break
