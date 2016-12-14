from datetime import datetime, timedelta
from subprocess import call


class downloader:

    def __init__(self, start, end, delta):

        # Check that the input parameters are of the correct type
        assert isinstance(start, datetime), 'start must be a datetime object!'
        assert isinstance(end, datetime), 'end must be a datetime object!'

        # Start must come before End
        assert (end - start).total_seconds() > 0, \
               'start must be a datetime object BEFORE end'

        self.start = start
        self.end = end
        self.delta = delta

    def timerange(self, freq='hourly'):

        """ Create a range of datetime objects at delta intervals.
            start:    datetime object for the start time of the range
            end  :    datetime object for the end time of the range
            delta:    timeunits of separation between elements in the range
            freq :    unit for the delta value. Can be hourly, daily, monthly

            ----------------------------------------------------------------------
            Returns a list of datetime objects at delta intervals.
        """
        newtime = self.start
        runningtime = []
        while newtime <= self.end:
            runningtime.append(newtime)
            if freq is 'hourly':
                newtime = newtime + timedelta(hours=self.delta)
            elif freq is 'daily':
                newtime = newtime + timedelta(days=self.delta)
            elif freq is 'monthly':
                newtime = newtime + timedelta(months=self.delta)
            else:
                print 'freq must be either hourly, daily, or monthly!'
                break

        return runningtime

    def downloadNARR(self):
        dataloc = 'ftp://nomads.ncdc.noaa.gov/NARR/'
        preamble = 'narr-a_221_'
        postamble = '00_000.grb'

        dateobjs = self.timerange()

        cmd = 'wget'

        for dt in dateobjs:
            year = str(dt.year)
            month = str(dt.month)
            day = str(dt.day)
            hour = str(dt.hour)

            if len(day) == 1:
                day = '0' + day
            if len(hour) == 1:
                hour = '0' + hour
            if len(month) == 1:
                month = '0' + month

            address = dataloc + year + month + '/' + year + month + day + '/'

            datafile = address + preamble + year + month + day + '_' + hour + \
                       postamble

            call([cmd, datafile])

        return None
