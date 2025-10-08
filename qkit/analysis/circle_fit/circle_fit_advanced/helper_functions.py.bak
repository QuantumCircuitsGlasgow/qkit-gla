
import numpy as np
from scipy.ndimage import gaussian_filter1d as scpg


'''
Additional functions to support the circle fitting


author = Wridhdhisom Karar
University of Glasgow, 2024

'''
def Watt2dBm(x):
	'''
	converts from units of watts to dBm
	'''
	return 10.*np.log10(x*1000.)
	
def dBm2Watt(x):
	'''
	converts from units of watts to dBm
	'''
	return 10**(x/10.) /1000.	

def soft_averager(z_data_raw:np.ndarray,averages:int=20)->np.ndarray:
    '''
    A iterative soft averager to remove the noise from the data
    and smoothen out noisy data for low power resonator data
    to improve fitting at low photon numbers.

    It samples the raw data ,spaced evenly/unevenly and accumulates averaging it over the number of averages
    and then returns the averaged data
    '''
    z_data=z_data_raw.copy()
    for i in range(averages):
        z_data+=np.roll(z_data,i)
    return z_data/averages

data_smoother = lambda x,sigma: scpg(x, sigma=sigma, mode='nearest',order=0)