#Template_Prologix_GPIB_Instrument.py
#Generic template for creating new instrument drivers that connect via a Prologix Ethernet-to-GPIB bridge.
#This template demonstrates the use of PrologixGPIBInstrument and ModernInstrument's @QkitProperty and @QkitFunction decorators.
#Murat Baran Polat <2950172p@student.gla.ac.uk>

import logging
import numpy as np
from typing import List, Any #import Any for generic types

# Import the necessary base class and decorators
from qkit.core.instrument_basev2 import (
    PrologixGPIBInstrument,
    ModernInstrument, #ModernInstrument is included here for reference
    QkitProperty,
    QkitFunction,
    PropertyMetadata,
    CachePolicy,
    interval_check
)

class Template_Prologix_GPIB_Instrument(PrologixGPIBInstrument):
    '''
    Template driver class for a generic instrument connected via Prologix GPIB.

    To create a new driver:
    1.  Rename this file to match your instrument (e.g., MyNewDevice.py).
    2.  Rename the class 'Template_Prologix_GPIB_Instrument' to match your device (e.g., MyNewDevice).
    3.  Update the __init__ method for your device's specific needs.
    4.  Replace 'gpib_address_str="GPIB::XX::INSTR"' with your device's actual GPIB address.
    5.  Define properties using @QkitProperty and functions using @QkitFunction.
        -   For each property/function, add a clear docstring.
        -   Implement the actual SCPI commands (self.write, self.ask) for your device.

    Usage Example (after creating and renaming your driver file):
        my_device = qkit.instruments.create(
            "my_device_name",
            "MyNewDevice", # This must match your class name
            gpib_address_str="GPIB::XX::INSTR",
            ip="192.168.0.100"
        )
        my_device.some_property = 123
        my_device.some_function()
    '''
    def __init__(self, name: str, gpib_address_str: str, **kwargs) -> None:
        logging.info(__name__ + f' : Initializing {name} (Template Device)')

        # Call the parent PrologixGPIBInstrument's constructor.
        # This sets up the communication with the Prologix bridge.
        super().__init__(name, gpib_address_str=gpib_address_str, **kwargs)

        # --- ADD YOUR DEVICE-SPECIFIC INITIALIZATION HERE ---
        # e.g., self._my_device_specific_setting = kwargs.get("setting", "default")
        # --- END OF DEVICE-SPECIFIC INITIALIZATION ---

    # --- Example Properties (@QkitProperty) ---
    # Properties define parameters that can be read (get) or written (set)
    # by users as if they were Python attributes.

    @QkitProperty(
        type=float, units="V",
        arg_checker=interval_check(0.0, 10.0), # Example: Valid range from 0V to 10V
        tags=["voltage", "output"]
    )
    def voltage_output(self) -> float:
        """
        Gets the current output voltage of the device.
        (Example SCPI: ":SOUR:VOLT?")
        """
        # Implement the actual SCPI query for your device
        response = self.ask(":SOUR:VOLT?")
        return float(response)

    @voltage_output.setter
    def voltage_output(self, value: float):
        """
        Sets the output voltage of the device.
        (Example SCPI: ":SOUR:VOLT <value>")
        """
        # Implement the actual SCPI command for your device
        self.write(f":SOUR:VOLT {value}")

    @QkitProperty(type=bool, cache_policy=CachePolicy.ALWAYS_REFRESH)
    def device_status(self) -> bool:
        """
        Gets the operational status of the device (e.g., True if on, False if off).
        (Example SCPI: ":OUTP?")
        """
        response = self.ask(":OUTP?")
        return bool(int(response))

    # --- Example Functions (@QkitFunction) ---
    # Functions define specific actions or operations that the device can perform.

    @QkitFunction
    def device_reset(self):
        """
        Sends a reset command to the device.
        (Example SCPI: "*RST")
        """
        self.write("*RST")
        logging.info(f"{self._name}: Device reset performed.")

    @QkitFunction
    def perform_calibration(self, calibration_type: str = "full"):
        """
        Triggers a calibration routine on the device.
        (Example SCPI: ":CAL:PERF")

        Parameters:
            calibration_type (str): Type of calibration (e.g., "full", "quick").
        """
        logging.info(f"{self._name}: Starting {calibration_type} calibration...")
        self.write(f":CAL:PERF {calibration_type.upper()}")
        # You might add a delay or query for completion here
        logging.info(f"{self._name}: Calibration initiated.")

    # --- Internal Helper Methods (not exposed as QkitFunction) ---
    # These methods are used internally by the driver but are not intended
    # to be called directly by the user as part of the public API.

    def _get_device_id(self) -> str:
        """
        Internal helper to get the device's identification string.
        """
        return self.ask("*IDN?").strip()

    # You can add more device-specific properties and functions as needed.
    #---------------------------------------------------------------------
    #Please make sure to use this generic template to build new drivers.