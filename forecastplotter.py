import scipy.io.netcdf as nc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def data_extract(wrffiles, varname):

    # Extract a single variable from a set of wrf files.
    # Data is converted to a numpy array for ease of use.

    fobjs = [nc.netcdf_file(f, 'r', mmap=False) for f in wrffiles]
    data = np.asarray([f.variables[varname][0, :, :] for f in fobjs])

    return data


def createMap(ax,
              ll_lat=40.5349739075,
              ll_lon=-74.3852612305,
              ur_lat=40.911207428,
              ur_lon=-73.6359838867,
              truelat1=30,
              truelat2=60,
              cenlon=-98,
              cenlat=40.703476,
              proj='lcc',
              resolution='c',
              fix_aspect=False):

    """Create a basemap instance for the forecast. Just a wrapper to
       the Basemap class using our forecast defaults for ease of use.
    """

    mp = Basemap(llcrnrlat=ll_lat,
                 llcrnrlon=ll_lon,
                 urcrnrlat=ur_lat,
                 urcrnrlon=ur_lon,
                 lat_0=cenlat,
                 lon_0=cenlon,
                 projection=proj,
                 resolution=resolution,
                 #    ax=ax,
                 fix_aspect=False)

    return mp


def figsetup(xpix=451,
             ypix=550,
             dpi=96.0):

    """ Create a figure for the forecast output. Defaults are
       based on the uWRF forecast page requirements. Returns matplotlib figure
       and ax objects.
    """

    fig = plt.figure(figsize=(xpix/dpi, ypix/dpi),
                     dpi=dpi,
                     frameon=False)
    ax = plt.Axes(fig, [0., 0., 1.0, 1.0])

    fig.add_axes(ax)

    return fig, ax


def plotcbar(im, labelx, labely, labeltxt,
             xpix=451,
             ypix=75,
             dpi=96.0):

    """ Utility function to draw a plot colorbar given an matplotlib object
        and label parameters. The figure is saved as cbar.png.
        Returns a matplotlib colorbar object.
    """

    fig, ax = plt.subplots(nrows=1,
                           ncols=1,
                           frameon=False,
                           figsize=(xpix/dpi, ypix/dpi))

    cbar = fig.colorbar(im, orientation='horizontal', cax=ax, drawedges=True)
    cbar.ax.text(labelx, labely, labeltxt)
    fig.tight_layout()
    fig.savefig('cbar.png', facecolor=fig.get_facecolor(), dpi=dpi)

    return cbar
