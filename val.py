import numpy as np
from datetime import datetime

""" Data key:
    ['DataKey',
 ' utm_date',
 ' network',
 ' station_id',
 ' obs_date',
 ' obs_time',
 ' org_date',
 ' org_time',
 ' dew_point',
 ' rel_hum',
 ' temp',
 ' wind_dir',
 ' wind_speed',
 ' wind_gust',
 ' visibility',
 ' pressure',
 ' rain_rate1h',
 ' rain_rate24h',
 ' rain_rate']
"""


class metnetCSV:
    """ Defines a station data file from NYC-MetNet. """

    def __init__(self, timestamp):
        """ The station data file is initialized with a timestamp in the form
            YYYYMMDD. There should be a correctly timestamped file for each
            day
        """

        self.filename = '.'.join([timestamp, 'metnetSALKdata', 'csv'])
        lines = [l.split(',') for l in open(self.filename)][2:]

# Get the list of stations available in the data
        self.coords = {}
        for l in lines:
            ID = l[3]
            if ID not in self.coords:
                self.coords[ID] = (float(l[-3]), float(l[-4]))

    def extractStationData(self, stationID, varname, datatime,
                           order='nearest', all=False):

        """ Extract a variable given by varname from the NYCMetNet CSV file
            object. The data is interpolated using method specified in order.

            INPUT:
            stationID: ID corresponding to the station needed.
            varname: Name of variable of interest. Could be any of these:
                     temperature
                     windspeed
                     winddir
                     rainfaill
            datatime: datetime object of the requested time for data
            order: At the moment, only one option available:
                   'nearest'.
            TODO: Incorporate linear interpolation method.

            OUTPUT:
            data: single value of varname at stationID.
        """

        # Get the actual file lines. Data starts on the 3rd line.
        stationlines = [l.split(',') for l in open(self.filename)][2:]

        # Get the timestamps from the file lines
        timestamps = [l[6] + '_' + l[7] for l in stationlines
                      if l[3] == stationID]

        # Convert to datetime objects.
        timeobj = [datetime.strptime(tm, '%m/%d/%Y_%H:%M') for
                   tm in timestamps]

        if order is 'nearest':
            # Find the closest timeobj to datatime
            diff = [abs((datatime - t).total_seconds()) for t in timeobj]
            mindiff = min(diff)
            minloc = diff.index(min(diff))

            if varname == 'temperature':

                data = [float(st[10]) for st in stationlines if
                        st[3] == stationID]
                data = np.asarray(data)
                data[data < -100] = np.nan

            elif varname == 'winds':
                data = [float(st[12]) for st in stationlines if
                        st[3] == stationID]
                data = np.asarray(data)
                data[data < -100] = np.nan

        if all is False:
            if mindiff < 3600:
                return timeobj[minloc], data[minloc]
            else:
                return np.nan, np.nan
        else:
            return timeobj, data


def main():
    import matplotlib.pyplot as plt
    station = metnetCSV('20160405')
    tm = datetime(2016, 4, 4, 15, 0)
    timestamps, data = station.extractStationData('KNYC ',
                                                  'temperature',
                                                  tm)

    fig, ax = plt.subplots()
    ax.plot(timestamps, data)
    fig.autofmt_xdate()
    fig.savefig('test.png')

if __name__ == '__main__':
    main()
