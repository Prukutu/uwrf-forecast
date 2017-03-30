import numpy as np

# A set of functions to calculate derived fields from raw WRF data


def relhum(temp, pres, qvapor):
    """ Calculate relative humidity given the temperature, pressure,
        and water vapor mixing ratio.

        INPUT:
        ------
        temp: ndarray of temperature in Kelvin
        pres: ndarray of pressure in Pa
        qvapor: ndarray of water vapor mixing ratio in kg/kg

        OUTPUT:
        -------
        rh: Relative Humidity in (%)

    """

    # Make sure the INPUT variables are the same shape
    assert temp.shape == pres.shape == qvapor.shape, 'Input size mismatch!'

    # Get Clausius-Claperyon constants
    e_0 = 611.73  # Pa
    t_0 = 273.16  # K
    Rv = 461.50  # J K-1 Kg-1
    Lv_0 = 2.501 * 10**6

    # For making the calculations easier
    K1 = Lv_0/Rv
    K2 = 1/t_0
    K3 = 1/temp

    # Finally, Clausius-Claperyon
    e_s = e_0*np.exp(K1*(K2 - K3))
    w_s = (.622*e_s)/(pres - e_s)

    rh = (qvapor/w_s)*100

    return rh


def windmag(u, v):
    # Calculation of total wind speed
    return np.sqrt(u**2 + v**2)


def winddir(u, v):
    # Calculate wind direction
    return 180 + np.arctan2(u, v)*180/np.pi


def tdew(P, Q):
    """ Calculate the dew point temperature from pressure and water vapor
        mixing ratio. Uses the power law from the Handbook.

            INPUT:
                P: Atmospheric pressure in kPa
                Q: Water vapor mixing ratio in kg_wv/kg_da

            OUTPUT:
              Tdew: Dew point temperature in degC
    """
    # Calculate the water vapor partial pressure
    pw = (Q/.622)/(1 + (Q/.622))*P
    a = np.log(pw)
    Tdew = 6.54 + 14.25*a + .7389*a**2 + .0948*a**3 + .4569*pw**.1984

    return Tdew


def K2F(tk):
    """ Convert a temperature from Kelvin to Farenheit. Convenience function.
    """
    return (tk - 273.15)*1.8 + 32


def hi(t_c, rh, units='C'):
    """ Calculate the heat index (degF) as per the instruction by the NWS:
        http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        Inputs:

        t_c: Temperature. Function defaults to Celcius, but Kelvin or
             Farenheit can be specified via the units kwarg.

        rh: Relative Humidity in % units.

        units: units of the given temperature. All temperature values are
               converted to Farenheit.
    """

    if units is 'C':
        t = 1.8*np.array(t_c) + 32
    elif units is 'K':
        t = 1.8*np.array(t_c - 273.15) + 32
    else:
        t = t_c

    # print 'Temperature is ' + str(t) + ' degF'
    # The first attempt is calculated.
    initial = .5*(t + 61.0 + ((t - 68.0)*1.2) + rh*.094)

    # If average between actual temperature and this HI is >= 80, the full
    # equation is used.
    if (initial + t)/2.0 >= 80.0:

        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -.22475541
        c5 = -6.83783e-3
        c6 = -5.481717e-2
        c7 = 1.22873e-3
        c8 = 8.5282e-4
        c9 = -1.99e-6

        if (rh < 13) and (t > 80) and (t < 112):
            # print 'Adjustment 1 is used!'
            adj = -((13 - rh)/4)*np.sqrt((17 - np.abs(t - 95))/17.0)

        elif (rh > 85) and (t > 80) and (t < 87):
            # print 'Adjustment 2 is used!'
            adj = ((rh - 85)/10)*((87 - t)/5.0)
        else:
            # print 'Adjustment is 0!'
            adj = 0

        hival = (c1 + c2*t + c3*rh + c4*t*rh + c5*t**2 + c6*rh**2 +
                 c7*rh*t**2 + c8*t*rh**2 + c9*(t**2)*(rh**2) + adj)
    else:
        # print 'Initial estimate is used!'
        hival = initial

    return hival


def pressure(P, PB):
    # WRF devides the pressure field into a "Base State Pressure" (PB) and a
    # "Perturbation Pressure" (P). Return the pressure (Pa).
    return P + PB


# Calculate WRF temperature in Celcius given the perturbation pressure P,
# base state perturbation pressure PB, and perturbation potential temperature
# T.
def temp_c(P, PB, T):
    # Calculate the Temperature from perturbation potential temperature and
    # actual pressure. Used to convert WRF output to actual temperature
    ptot = (P + PB)*.01
    p0 = 1000  # base pressure in hPa
    kappa = .2854
    theta = T + 300
    return theta*(ptot/p0)**kappa - 273.15


def geopotential_height(PH, PHB):
    return (PH + PHB)/9.81
