import numpy as np
from datetime import datetime
# from qc import qualityControl

# A set of utilities to read data from NYC-MetNet stations while doing some
# quality control.


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
                           order='nearest', allvals=False):

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

            elif varname == 'winds':
                data = [float(st[12]) for st in stationlines if
                        st[3] == stationID]
                data = np.asarray(data)
                # data[data < -100] = np.nan

        # Check that the neirest neighbor is not too far.
        if allvals is False:
            if mindiff < 3000:
                return timeobj[minloc], data[minloc]
            else:
                return datatime, np.nan
        else:
            return timeobj, data


class validityCheck:
    """ Class to check that station data is within valid range."""

    def __init__(self, rawdata, varname):

        # Define range of acceptable values per variable.
        self.thresh = {'temperature': [-5, 45],
                       'winds': [0, 50]}
        self.rawdata = rawdata
        self.varname = varname

    def run(self):

        lowval, hival = self.thresh[self.varname]
        lvl1data = self.rawdata

        # Get the data's count of pre-existing NaNs
        # print lvl1data
        lvl1data = [data if (data >= lowval) and (data <= hival) else
                    np.nan for data in self.rawdata]

        nancount = self.rawdata.count(np.nan)
        newnancount = lvl1data.count(np.nan) - nancount
        print 'QC purged ' + str(newnancount) + ' data points!'

        return lvl1data
#
#
# class temporalCheck(qualityControl):
#     def __init__(self, rawdata, varname):
#         qualityControl.__init__(self, rawdata, varname)
#         self.rate = {'temperature': 19.4444,
#                      'winds': 10.2889}
#         self.datamean = np.nanmean(self.rawdata)
#
#     def run(self, maxdev=15):
#         datarate = self.rate[self.varname]
#         lvl2data = [t for t in self.rawdata]
#         hival = self.datamean + maxdev
#         lowval = self.datamean - maxdev
#
#         print lowval, hival
#in station.coords.keys():
#     fig, ax1 = plt.subplots(figsize=(7, 4))
#
#     # Use colored twin axes to denote the data.
#     ax2 = plt.twinx(ax=ax1)
#     ax1.plot_date(timestamps, t2lvl1[key],
#                   color='#f44336',
#                   linestyle='-',
#                   marker=None)
#     ax2.plot_date(timestamps, wmaglvl1[key],
#                   color='#009688',
#                   linestyle='-',
#                   marker=None)
#
#     ax1.set_ylabel(u'Temperature (\u2103)')
#     ax1.set_ylim(-5, 42)
#     ax1.yaxis.label.set_color('#f44336')
#     ax2.spines['left'].set_color('#f44336')
#     ax1.tick_params(axis='y', colors='#f44336')
#
#     ax2.set_ylabel('Wind Speed (m/s)')
#     ax2.set_ylim(0, 10)
#     ax2.yaxis.label.set_color('#009688')
#     ax2.spines['right'].set_color('#009688')
#     ax2.tick_params(axis='y', colors='#009688')
#
#     fig.autofmt_xdate()
#
#     fig.savefig(key + '.png', dpi=200, bbox_inches='tight')
#     fig.close()

#         for n in range(1, len(lvl2data)):
#
#             if np.isnan(lvl2data[n]):
#                 lvl2data[n] = np.nan
#
#             elif (np.isnan(lvl2data[n-1]) and lvl2data[n] > lowval and
#                   lvl2data[n] < hival):
#                 lvl2data[n] = lvl2data[n]
#
#             elif abs(lvl2data[n] - lvl2data[n-1]) < datarate:
#                 lvl2data[n] = lvl2data[n]
#
#             else:
#                 lvl2data[n] = np.nan
#
#         return lvl2data
