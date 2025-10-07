
"""Module for fitting microwave resonator data and extracting physical parameters.

This module provides the FittedResonator class which builds upon the PowerResonator
class, adding fitting capabilities and photon number calculations. It uses circle
fitting methods to extract quality factors, resonance frequencies, and other
parameters from complex S-parameter measurements.
"""

from typing import List, Dict, Union, Tuple, Optional, Any
import numpy as np
from .resonator import PowerResonator
from .circle_fitter import *  # TODO: Replace with explicit imports
import scipy.constants as const
from collections import defaultdict
import logging
import pandas as pd

class FittedResonator(PowerResonator):
    """Extends PowerResonator with fitting capabilities and photon properties.
    
    This class provides methods to fit resonator data using circle fitting algorithms,
    extract quality factors (Q), resonance frequencies, photon numbers, and other
    important parameters characterizing a superconducting microwave resonator.
    
    Attributes:
        beta: Coupling parameter.
        centers: Complex centers of the fitted circles.
        radii: Radii of the fitted circles.
        photon_number: Calculated photon numbers for each power.
        delay: Electrical delay in the measurement setup.
        A: Amplitude parameter from fitting.
        alpha: Phase parameter from fitting.
        phi: Impedance mismatch parameter.
        theta: Rotation angle parameter.
        Qc: Coupling quality factors.
        Qi: Internal quality factors.
        Ql: Loaded quality factors.
        fr: Resonance frequencies.
        ResonatorDF: DataFrame containing all fitted parameters.
        
    TODO:
        - Update to handle an array of resonator objects at different powers.
        - Implement properties to return either a list or single value based on power count.
    """

    def __init__(self, sij, frequency, power=[0.], delay=-50e-9, temp=26e-3, fit=False):
        """Initialize a FittedResonator object.
        
        Args:
            sij: Complex S-parameter data (transmission/reflection measurements).
            frequency: Frequency points corresponding to the S-parameter data.
            power: List of power levels used in the measurements (dBm). Default: [0.].
            delay: Electrical delay in the measurement setup (seconds). Default: -50e-9.
            temp: Temperature of the experiment (Kelvin). Default: 26e-3 (26 mK).
            fit: Flag to automatically fit the data during initialization. Default: False.
        """
        super().__init__(sij, frequency, power=power, temp=temp)

        # Coupling parameter
        self.beta = 0
        
        # Circle fitting results
        self.centers = []  # Centers of fitted circles in complex plane
        self.radii = []    # Radii of fitted circles
        
        # Initialize photon number (will be updated after fitting)
        self.photon_number = power
        
        # Internal state variables
        self._fit = fit    # Flag to track if fitting has been done
        self._fit_params = []  # List to store fit parameters
        self._plot = False  # Flag to control plotting during fitting
        
        # Measurement parameters
        self.delay = delay  # Electrical delay, fixed for all resonators
        
        # Initialize arrays for fit results (one entry per power level)
        self.A = np.zeros(self._powers)  # Amplitude parameter
        self.alpha = np.zeros(self._powers)  # Phase parameter 
        # TODO: Update alpha to be arg(A) and make A complex while fitting
        self.phi = np.zeros(self._powers)  # Impedance mismatch angle
        self.theta = np.zeros(self._powers)  # Rotation angle parameter
        
        # Quality factors and their uncertainties
        self.Qc = np.zeros(self._powers)  # Coupling quality factor
        self.Qc_err = np.zeros(self._powers)  # Error in Qc
        self.Qi = np.zeros(self._powers, dtype=float)  # Internal quality factor
        self.Qi_err = np.zeros(self._powers, dtype=float)  # Error in Qi
        self.Ql = np.zeros(self._powers, dtype=float)  # Loaded quality factor
        self.Ql_err = np.zeros(self._powers, dtype=float)  # Error in Ql
        
        # Resonance frequency and its uncertainty
        self.fr = np.zeros(self._powers, dtype=float)  # Resonance frequency
        self.fr_err = np.zeros(self._powers, dtype=float)  # Error in fr
        
        # Remaining delay after correction
        self.delay_remaining = np.zeros(self._powers, dtype=float)
        
        # Alternative internal quality factor calculation (without diamagnetic correction)
        self.Qi_absqc = np.zeros(self._powers, dtype=float)
        self.Qi_absqc_err = np.zeros(self._powers, dtype=float)


    def photon_from_P(self, P, fr, Ql, Qc):
        """Calculate the photon number inside the resonator from input power.
        
        Uses the relationship between input power and intra-resonator photon number
        based on quantum physics principles.
        
        Args:
            P: Input power in dBm.
            fr: Resonance frequency in Hz.
            Ql: Loaded quality factor (dimensionless).
            Qc: Coupling quality factor (dimensionless).
            
        Returns:
            float: The estimated number of photons in the resonator.
        """
        hbar = const.hbar  # Reduced Planck's constant
        
        # Convert from dBm to mW and apply scaling for chip-level power
        pw = (10**(P/10))/1e3  
        
        # Calculate photon number using the standard formula:
        # n = 2P_in/(hbar*omega^2) * (Ql^2/Qc)
        # where omega = 2π*fr is the angular frequency
        return 2*pw/(hbar*(2*const.pi*fr)**2)*(Ql**2)/(Qc)
    def fit(self, sij, f, power=None, delay=None, plot=None):
        """Fit resonator data using circle fitting algorithm.
        
        This method fits the provided complex S-parameter data to the resonator
        model using circle fitting techniques. It processes the data through
        the notch_port class and returns the fit results.
        
        Args:
            sij: Complex S-parameter data (transmission/reflection measurements).
            f: Frequency points corresponding to the S-parameter data.
            power: Power level at which the measurement was taken. Default: None.
            delay: Electrical delay in the measurement setup. Default: None.
            plot: Whether to generate plots during fitting. If None, uses the
                 default _plot attribute value.
                 
        Returns:
            dict: Dictionary containing all the fitted parameters.
        """
        if plot is None:
            plot = self._plot
            
        return notch_port(f, sij, delay=delay, power=power).fit_result(plot=plot, prefit=self.prefit)
    
    def fitter(self, sij, f, power=None, delay=None):
        """Return the raw notch_port object for debugging purposes.
        
        This method provides direct access to the notch_port object used for
        fitting, which is useful for debugging or advanced analysis.
        
        Args:
            sij: Complex S-parameter data (transmission/reflection measurements).
            f: Frequency points corresponding to the S-parameter data.
            power: Power level at which the measurement was taken. Default: None.
            delay: Electrical delay in the measurement setup. Default: None.
            
        Returns:
            notch_port: The notch_port object for the given data.
        """
        return notch_port(f, sij, delay=delay)
    
        
    def fit_all(self, index=-1):
        """Fit resonator data for all power levels and update object attributes.
        
        This is the main method that processes all power levels, performs fitting
        on each one, and updates the object's attributes with the fitted parameters.
        It handles both single-power and multi-power scenarios.
        
        Args:
            index: Optional index to select specific data. Default: -1.
            
        Returns:
            None: Updates the object's attributes in place.
        """
        # Handle multi-power case
        if self._powers > 1:  # sij is 2D in this case
            self.prefit = defaultdict()
            
            # Process each power level (starting from highest power)
            for i, power in reversed(list(enumerate(self._pow))):
                logging.info(f"Fitting for power {power} ------------>")
                
                # Perform the fitting
                result = self.fit(self.Rs[i].sij, self.Rs[i]._f, power, delay=self.delay)
                self._fit_params = result
                self._fit_params['power'] = power

                # Update parameters from fit results
                # Amplitude and phase parameters
                self.A[i] = result["a"]
                self.alpha[i] = result["alpha"]
                self.phi[i] = result["phi"]
                self.theta[i] = result["theta"]
                
                # Quality factors
                self.Qc[i] = result["Qc"]
                self.Qc_err[i] = result["absQc_err"]
                self.Qi[i] = result["Qi"]
                self.Qi_err[i] = result["Qi_err"]
                self.Ql[i] = result["Ql"]
                self.Ql_err[i] = result["Ql_err"]
                
                # Resonance frequency
                self.fr[i] = result["fr"]
                self.fr_err[i] = result["fr_err"]
                
                # Other parameters
                self.delay_remaining[i] = result["delay_remaining"]
                self.Qi_absqc[i] = result["Qi_no_dia_corr"]
                self.Qi_absqc_err[i] = result["Qi_no_dia_corr_err"]
                
                # Calculate photon number
                self.photon_number[i] = self.photon_from_P(power, self.fr[i], self.Ql[0], np.abs(self.Qc[0]))
                
                # Store circle fit results
                self.centers.append(result["c"])
                self.radii.append(result["r0"])
                
                # Store results for future fitting
                self.prefit.update(result)
                
                # Add to DataFrame for easy analysis
                self.ResonatorDF = self.ResonatorDF.append(pd.DataFrame([self._fit_params]))
        
        # Handle single-power case
        else:
            self.prefit = None
            
            # Perform the fitting
            result = self.fit(self.Rs[0].sij, self.Rs[0]._f, self._pow, delay=self.delay)
            self._fit_params = result
            self._fit_params['power'] = self._pow
            
            # Update parameters from fit results
            # Amplitude and phase parameters
            self.A[0] = result["a"]
            self.alpha[0] = result["alpha"]
            self.phi[0] = result["phi"]
            self.theta[0] = result["theta"]
            
            # Quality factors
            self.Qc[0] = result["Qc"]  # Setting will update the local variable
            self.Qc_err[0] = result["absQc_err"]
            self.Qi[0] = result["Qi"]
            self.Qi_err[0] = result["Qi_err"]
            self.Ql[0] = result["Ql"]
            self.Ql_err[0] = result["Ql_err"]
            
            # Resonance frequency
            self.fr[0] = result["fr"]
            self.fr_err[0] = result["fr_err"]
            
            # Other parameters
            self.delay_remaining[0] = result["delay_remaining"]
            self.Qi_absqc[0] = result["Qi_no_dia_corr"]
            self.Qi_absqc_err[0] = result["Qi_no_dia_corr_err"]
            
            # Calculate photon number
            self.photon_number = self.photon_from_P(self._pow, self.fr, self.Ql, np.abs(self.Qc))
            
            # Store circle fit results
            self.centers.append(result["c"])
            self.radii.append(result["r0"])
            
            # Create DataFrame for easy analysis
            self.ResonatorDF = pd.DataFrame([self._fit_params])

        # Set power as the index for the DataFrame
        self.ResonatorDF.set_index('power', inplace=True)
        
        # Mark that fitting has been done
        self._fit = True
        

#-------------------Test-------------------
# #Test the FittedResonator class
if __name__== "__main__":
    fr = FittedResonator([1+1j,2+2j,3+3j],5.0e9,power=[1.0,2.0])
    print(fr.__dict__)
    fr.plot()
# fr = FittedResonator([1+1j,2+2j,3+3j],5.0e9,1.0,300)