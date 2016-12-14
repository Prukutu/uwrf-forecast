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
        mixing ratio. Uses the power paw                                     

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



