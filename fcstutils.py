import numpy as np
import scipy.io.netcdf as nc
from datetime import datetime, timedelta

import cdo


def rmse(predictions, targets):
    mask = np.where(~np.isnan(targets))[0]
    return np.sqrt(np.nanmean((np.array(predictions)[mask] -
                               np.array(targets)[mask]) ** 2))


def flatlist(list2flat):
    return [item for sublist in list2flat for item in sublist]


class pointFind:
    """ A class to find the closest point in a grid given an input using
        geospatial coordinates.
        INPUT:
        longrid: n-dimensional longitude coordinate
        latgrid: n-dimensional latitude coordinate
    """

    def __init__(self, longrid, latgrid):

        # Check that the lon and lat grids have the same shape. Raise
        # an assertion error otherwise.
        gridErrMsg = 'The coordinate grids do not match!'
        assert longrid.shape == latgrid.shape, gridErrMsg

        # Make sure that longs go from -180 to 180
        if (np.max(longrid) > 180) and (np.min(longrid) >= 0):
            self.longrid = ((longrid + 180) % 360) - 180
        else:
            self.lon = longrid

        self.lat = latgrid
        luloc = '/home/luis/Documents/CCNY/Research/pymodules/lu.nc'
        lufile = nc.netcdf_file(luloc)
        self.lu = lufile.variables['LU_INDEX'][:].squeeze()

    def nearest(self, xin, yin, data=None):
        """ Perform nearest neighbor interpolation at location (xin,yin)
            and returns value of data at that point if a data array is given.
        """

        if data is not None:
            assert isinstance(data, np.ndarray), 'Not a valid data array!'

        # Calculate the distance of all points to the (xin,yin) coordinate
        # and get the point in which the distance is minimum.
        distance = np.sqrt((xin - self.lon)**2 + (yin - self.lat)**2)
        # distance[np.where(self.lu == 17.0)] = np.nan
        locIndex = np.where(distance == np.nanmin(distance))

        if data is None:
            return locIndex[0][0], locIndex[1][0]
        else:
            return locIndex[0][0], locIndex[1][0], data[locIndex[0][0],
                                                        locIndex[1][0]]


def timerange(start, end, delta, freq='hourly'):
    """ Create a range of datetime objects at delta intervals.
        start:    datetime object for the start time of the range
        end  :    datetime object for the end time of the range
        delta:    timeunits of separation between elements in the range
        freq :    unit for the delta value. Can be hourly, daily, monthly

        ----------------------------------------------------------------------
        Returns a list of datetime objects at delta intervals.
    """
    newtime = start
    runningtime = []
    while newtime <= end:
        runningtime.append(newtime)
        if freq is 'hourly':
            newtime = newtime + timedelta(hours=delta)
        elif freq is 'daily':
            newtime = newtime + timedelta(days=delta)
        elif freq is 'monthly':
            newtime = newtime + timedelta(months=delta)
        else:
            print 'freq must be either hourly, daily, or monthly!'
            break

    return runningtime


def interp2height(data, heightcoord, newheight):
    # Get the height values between which newheight lies
    diff = heightcoord - newheight
    z0 = np.max(heightcoord[diff < 0])
    z1 = np.min(heightcoord[diff > 0])

    z0Index = np.where(heightcoord == z0)[-1][0]
    z1Index = np.where(heightcoord == z1)[-1][0]

    if len(data.shape) == 4:
        data0 = data[:, z0Index, :, :]
        data1 = data[:, z1Index, :, :]
    elif len(data.shape) == 2:
        data0 = data[:, z0Index]
        data1 = data[:, z1Index]
    else:
        raise ValueError

    data_interp = data0 + (data1 - data0)*(newheight - z0)/(z1 - z0)
    return data_interp


# To unstagger the WRF wind variables, we use the following equations
#    U_THETA(i,j,k) = 0.5*(U(i,j,k) + U(i+1,j,k))
#    V_THETA(i,j,k) = 0.5*(V(i,j,k) + V(i,j+1,k))
#    W_THETA(i,j,k) = 0.5*(W(i,j,k) + W(i,j,k+1))
def unstagger(data, dimension):
    # data must be 4D wind variable in staggered coordinates

    stagdim = 0
    if dimension is 'U':
        stagdim = -1

    elif dimension is 'V':
        stagdim = -2

    else:
        stagdim = -3

    datashape = data.shape
    datashape_unstaggered = np.copy(datashape)
    datashape_unstaggered[stagdim] = datashape[stagdim] - 1

    data_unstaggered = np.zeros(datashape_unstaggered)

    if dimension == 'U':
        for n in range(datashape_unstaggered[stagdim]):
            data_unstaggered[:, :, :, n] = .5*(data[:, :, :, n] +
                                               data[:, :, :, n+1])
    elif dimension == 'V':
        for n in range(datashape_unstaggered[stagdim]):
            data_unstaggered[:, :, n, :] = .5*(data[:, :, n, :] +
                                               data[:, :, n+1, :])

    else:
        for n in range(datashape_unstaggered[stagdim]):
            data_unstaggered[:, n, :, :] = .5*(data[:, n, :, :] +
                                               data[:, n+1, :, :])

    return data_unstaggered


def extractDates(filename, out='str'):
    c = cdo.Cdo()
    dates = c.showtimestamp(input=filename)
    dates = dates[0].split()

    if out == 'str':
        return dates
    else:
        date_obj = [datetime.strptime(a, '%Y-%m-%dT%H:%M:%S') for a in dates]
        return date_obj
