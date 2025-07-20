# Keysight P50xxA/P5004A Streamline Series USB VNA
# Joao Barbosa <j.barbosa.1@research.gla.ac.uk>, 2021
# Refactored for ModernInstrument and PrologixGPIBInstrument base classes
# Murat Baran Polat <2950172p@student.gla.ac.uk>

import logging
import numpy as np
import time
from typing import List

# Import the new base class and necessary decorators/metadata from instrument_basev2
from qkit.core.instrument_basev2 import (
    PrologixGPIBInstrument,
    ModernInstrument,
    QkitProperty,
    QkitFunction,
    PropertyMetadata,
    CachePolicy,
    interval_check
)

# You can remove 'from qkit import visa' if it was present, as it's not used directly anymore.
# from qkit.core.instrument_base import Instrument # This is no longer needed

class Keysight_VNA_P50xxA(PrologixGPIBInstrument):
    '''
    Driver class for Keysight P50xxA/P5004A Streamline Series USB VNA.
    Now inheriting from ModernInstrument framework and using QkitProperty/QkitFunction.

    Usage:
        vna = qkit.instruments.create("vna", "Keysight_VNA_P50xxA", gpib_address_str="GPIB::1::INSTR", ip="192.168.0.100")
        vna.averages = 10
        print(vna.bandwidth)
        vna.set_segment(...)
    '''
    def __init__(self, name: str, gpib_address_str: str, channel_id: int = 1, cw_mode: bool = False, **kwargs) -> None:
        logging.info(__name__ + f' : Initializing instrument {name}')
        
        # Call the parent PrologixGPIBInstrument's constructor
        # It handles setting up self._prologix_instrument and calling discover_capabilities
        super().__init__(name, gpib_address_str=gpib_address_str, **kwargs)

        self._ci = int(channel_id) # Channel ID for SCPI commands
        self.cw_mode = cw_mode     # Continuous wave mode flag
        self._edel = 0             # Electronic Delay value

        # Note: The original add_parameter and add_function calls are REMOVED.
        # Properties and functions are now defined using decorators below.
        # self.get_all() is now called implicitly if discover_capabilities processes the properties.
        # However, a manual get_all can still be useful for initial state capture.
        self._initial_get_all_parameters()

    # --- Properties (formerly add_parameter) ---

    @QkitProperty(
        type=int, units="",
        arg_checker=interval_check(1, None) # minval=1
    )
    def averages(self) -> int:
        """Sets or gets the number of averages for the sweep."""
        return int(self.ask(f"SENS{self._ci}:AVER:COUN?"))
    @averages.setter
    def averages(self, value: int):
        self.write(f"SENS{self._ci}:AVER:COUN {value}")

    @QkitProperty(type=bool)
    def Average(self) -> bool: # Note: Capital 'A' as in original
        """Enables or disables averaging."""
        return bool(int(self.ask(f"SENS{self._ci}:AVER?")))
    @Average.setter
    def Average(self, value: bool):
        self.write(f"SENS{self._ci}:AVER {1 if value else 0}")

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(1.0, 15e6) # minval=1, maxval=15e6
    )
    def bandwidth(self) -> float:
        """Sets or gets the Intermediate Frequency (IF) bandwidth."""
        return float(self.ask(f"SENS{self._ci}:BWID?"))
    @bandwidth.setter
    def bandwidth(self, value: float):
        self.write(f"SENS{self._ci}:BWID {value}")

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(9e3, 20e9) # minval=9e3, maxval=20e9
    )
    def centerfreq(self) -> float:
        """Sets or gets the center frequency of the sweep."""
        return float(self.ask(f"SENS{self._ci}:FREQ:CENT?"))
    @centerfreq.setter
    def centerfreq(self, value: float):
        self.write(f"SENS{self._ci}:FREQ:CENT {value}")

    @QkitProperty(type=bool)
    def cw(self) -> bool:
        """Enables or disables Continuous Wave (CW) mode."""
        return self.cw_mode # This was a locally stored flag in original
    @cw.setter
    def cw(self, status: bool):
        if status:
            self.write(f"SENS{self._ci}:SWEEP:TYPE CW")
            self.cw_mode = True
        else:
            self.write(f"SENS{self._ci}:SWEEP:TYPE LIN")
            self.cw_mode = False

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(10e6, 20e9) # minval=10e6, maxval=20e9
    )
    def cwfreq(self) -> float:
        """Sets or gets the Continuous Wave (CW) frequency."""
        return float(self.ask(f"SENS{self._ci}:FREQ:CW?"))
    @cwfreq.setter
    def cwfreq(self, value: float):
        if self.cw_mode:
            self.write(f"SENS{self._ci}:FREQ:CW {value}")
        else:
            raise ValueError("VNA not in CW mode. Set .cw = True first.")

    @QkitProperty(
        type=float, units="s",
        arg_checker=interval_check(-10.0, 10.0) # minval=-10, maxval=10
    )
    def edel(self) -> float:
        """Sets or gets the electronic delay."""
        # Original logic was complex here, selecting active measurement if none.
        # This implementation simplifies to assume an active measurement or handles default.
        ch_sel = self.ask(f"CALC{self._ci}:PAR:SEL?").strip("\n")
        if ch_sel == '""':
            ch_ = self.ask(f"CALC{self._ci}:PAR:CAT?")
            strip_char = '"' # Variable to hold the double quote character
            self.write(f"CALC{self._ci}:PAR:SEL {ch_.strip(strip_char).split(',')[0]}")
        self._edel = float(self.ask(f"CALC{self._ci}:CORR:EDEL:TIME?"))
        return self._edel
    @edel.setter
    def edel(self, value: float):
        """Sets or gets the electronic delay."""
        ch_sel = self.ask(f"CALC{self._ci}:PAR:SEL?").strip("\n")
        if ch_sel == '""':
            ch_ = self.ask(f"CALC{self._ci}:PAR:CAT?")
            strip_char = '"' # Variable to hold the double quote character
            self.write(f"CALC{self._ci}:PAR:SEL {ch_.strip(strip_char).split(',')[0]}")
        self.write(f"CALC{self._ci}:CORR:EDEL:TIME {value}")
        self._edel = value # Update local cache


    @QkitProperty(
        type=int, units="",
        arg_checker=interval_check(1, 1e5), # minval=1, maxval=1e5
        tags=["sweep"]
    )
    def nop(self) -> int:
        """Sets or gets the number of points in the sweep."""
        return int(self.ask(f"SENS{self._ci}:SWE:POIN?"))
    @nop.setter
    def nop(self, value: int):
        self.write(f"SENS{self._ci}:SWE:POIN {value}")

    @QkitProperty(type=float, units="dBm")
    def power(self) -> float:
        """Sets or gets the output power."""
        # Original accepted a 'port' argument in getter/setter, here it's fixed to port 1
        return float(self.ask(f"SOUR{self._ci}:POW1?"))
    @power.setter
    def power(self, value: float):
        """Sets or gets the output power."""
        self.write(f"SOUR{self._ci}:POW1 {value}")

    @QkitProperty(type=bool)
    def rf_output(self) -> bool:
        """Enables or disables RF output."""
        return bool(int(self.ask("OUTP?")))
    @rf_output.setter
    def rf_output(self, state: bool):
        """Enables or disables RF output."""
        self.write(f"OUTP {1 if state else 0}")

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(70.0, 20e9) # minval=70, maxval=20e9
    )
    def span(self) -> float:
        """Sets or gets the frequency span of the sweep."""
        return float(self.ask(f"SENS{self._ci}:FREQ:SPAN?"))
    @span.setter
    def span(self, value: float):
        """Sets or gets the frequency span of the sweep."""
        self.write(f"SENS{self._ci}:FREQ:SPAN {value}")

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(9e3, 20e9) # minval=9e3, maxval=20e9
    )
    def startfreq(self) -> float:
        """Sets or gets the start frequency of the sweep."""
        return float(self.ask(f"SENS{self._ci}:FREQ:START?"))
    @startfreq.setter
    def startfreq(self, value: float):
        """Sets or gets the start frequency of the sweep."""
        self.write(f"SENS{self._ci}:FREQ:START {value}")

    @QkitProperty(
        type=float, units="Hz",
        arg_checker=interval_check(9e3, 20e9) # minval=9e3, maxval=20e9
    )
    def stopfreq(self) -> float:
        """Sets or gets the stop frequency of the sweep."""
        return float(self.ask(f"SENS{self._ci}:FREQ:STOP?"))
    @stopfreq.setter
    def stopfreq(self, value: float):
        """Sets or gets the stop frequency of the sweep."""
        self.write(f"SENS{self._ci}:FREQ:STOP {value}")

    @QkitProperty(type=str)
    def sweepmode(self) -> str:
        """Sets or gets the sweep mode."""
        return self.ask(f"SENS{self._ci}:SWE:MODE?").strip()
    @sweepmode.setter
    def sweepmode(self, value: str):
        """Sets or gets the sweep mode."""
        if value.upper() in ["CONT", "HOLD", "SING", "GRO"]:
            self.write(f"SENS{self._ci}:SWE:MODE {value.upper()}")
        else:
            raise ValueError(f"Sweep mode unknown. Use: ['CONT','HOLD','SING','GRO']. Got '{value}'")

    @QkitProperty(type=float, units="s")#, cache_policy=CachePolicy.ALWAYS_REFRESH)
    def sweeptime(self) -> float:
        """Gets the sweep time."""
        return float(self.ask(f"SENS{self._ci}:SWE:TIME?"))

    @QkitProperty(type=float, units="s")#, cache_policy=CachePolicy.ALWAYS_REFRESH)
    def sweeptime_averages(self) -> float:
        """Gets the total sweep time including averages."""
        # Calls the getter for sweeptime and averages properties
        return self.sweeptime * self.averages # Accessing properties directly


    # --- Functions (formerly add_function) ---

    @QkitFunction
    def reset(self):
        """Resets the VNA to its default state."""
        self.write("*RST")

    @QkitFunction
    def hold(self, value: bool):
        """Puts the VNA sweep into hold (True) or continuous (False) mode."""
        if value:
            self.write(f"SENS{self._ci}:SWE:MODE HOLD")
        else:
            self.write(f"SENS{self._ci}:SWE:MODE CONT")

    @QkitFunction
    def avg_clear(self):
        """Clears the averaging buffer."""
        self.write(f"SENS{self._ci}:AVER:CLE")

    @QkitFunction
    def data_format(self, value: str = "ASC"):
        """Sets the data format for trace data retrieval."""
        if value.upper() == "ASC":
            self.write("FORM ASC")
        elif value.upper() == "REAL32":
            self.write("FORM REAL,32")
        elif value.upper() == "REAL64":
            self.write("FORM REAL,64")
        else:
            raise ValueError("Incorrect data format. Use: ['ASC','REAL32','REAL64']")

    @QkitFunction
    def set_sweeptime_auto(self):
        """Sets the sweep time to auto mode."""
        self.write(f"SENS{self._ci}:SWE:TIME:AUTO ON")

    @QkitFunction
    def get_tracedata(self, format: str = "AmpPha"):
        """
        Retrieves trace data from the VNA.
        Returns: Tuple[np.ndarray, np.ndarray] for (Amplitude, Phase) or (Real, Imaginary).
        """
        self.write("FORM REAL,32") # For now use Real 32 bit data format
        self.write('FORM:BORD SWAPPED') # Byte order for GPIB data transfer

        # Use ask_for_values which is now implemented in PrologixGPIBInstrument
        data = self.ask_for_values(f"CALC{self._ci}:MEAS:DATA:SDATA?")
        
        # Ensure data is a NumPy array for further processing
        if not isinstance(data, np.ndarray):
            logging.error(f"get_tracedata received non-array data: {data}")
            raise TypeError("Expected numerical data from ask_for_values for trace data.")

        dataRe = data[::2]
        dataIm = data[1::2]

        if format.upper() == "AMPPHA":
            if self.cw_mode:
                datacomplex = np.mean(dataRe + 1j * dataIm)
                dataAmp = np.abs(datacomplex)
                dataPha = np.angle(datacomplex)
                return dataAmp, dataPha
            else:
                dataAmp = np.sqrt(dataRe**2 + dataIm**2)
                dataPha = np.arctan2(dataIm, dataRe)
                return dataAmp, dataPha
        elif format.upper() == "REALIMAG":
            if self.cw_mode:
                dataRe = np.mean(dataRe)
                dataIm = np.mean(dataIm)
                return dataRe, dataIm
            else:
                return dataRe, dataIm
        else:
            raise ValueError('get_tracedata(): Format must be AmpPha or RealImag')

    @QkitFunction
    def get_freqpoints(self):
        """Retrieves frequency points of the current sweep."""
        self.write("FORM REAL,32")
        self.write('FORM:BORD SWAPPED')

        if self.cw_mode:
            return self.cwfreq # Accessing property directly
        else:
            return self.ask_for_values(f"CALC{self._ci}:MEAS:DATA:X?")

    @QkitFunction
    def ready(self) -> bool:
        '''
        This is a proxy function, returning True when the VNA has finished the required number of averages.
        Averaging must be on (even if it is just one average)
        '''
        return bool(int(self.ask("STAT:OPER:AVER1:COND?")) & 0b10)

    @QkitFunction
    def pre_measurement(self):
        """Configures VNA for manual trigger and enables averaging before measurement."""
        self.write("TRIG:SOUR MAN")
        self.write(f"SENS{self._ci}:AVER ON")

    @QkitFunction
    def start_measurement(self):
        """Initiates a measurement sequence, waiting for triggers and averaging."""
        self.avg_clear()
        for i in range(self.averages): # Accessing property directly
            while(True):
                if(int(self.ask("TRIG:STAT:READ? MAN"))) : break
                time.sleep(0.05)
            self.write("INIT:IMM")
            time.sleep(0.1)

    @QkitFunction
    def post_measurement(self):
        """Resets VNA to immediate trigger and disables averaging after measurement."""
        self.write("TRIG:SOUR IMM")
        self.write(f"SENS{self._ci}:AVER OFF")
        self.hold(False)

    @QkitFunction
    def set_segment(self, start_freqs: List[float], stop_freqs: List[float], powers: List[float], bandwidths: List[float]):
        """
        Configures segmented sweep using start/stop frequency ranges.

        Parameters:
            start_freqs (List[float]): Start frequency of each segment (Hz).
            stop_freqs (List[float]): Stop frequency of each segment (Hz).
            powers (List[float]): Power level for each segment (dBm).
            bandwidths (List[float]): IF bandwidth for each segment (Hz).
        """
        if not (len(start_freqs) == len(powers) == len(bandwidths)):
            raise ValueError("All input lists must be the same length.")

        n_segments = len(start_freqs)

        self.write(f"SENS{self._ci}:SEGM:DEL:ALL")

        for i, (f_start, f_stop, p, bw) in enumerate(zip(start_freqs, stop_freqs, powers, bandwidths), start=1):
            self.write(f"SENS{self._ci}:SEGM{i}:FREQ:STAR {f_start}")
            self.write(f"SENS{self._ci}:SEGM{i}:FREQ:STOP {f_stop}")
            self.write(f"SENS{self._ci}:SEGM{i}:POW {p}")
            self.write(f"SENS{self._ci}:SEGM{i}:BWID {bw}")

        self.write(f"SENS{self._ci}:SEGM:STAT ON")


    # --- Internal helper for initial get_all, adapting to new property access ---
    def _initial_get_all_parameters(self):
        """
        Initializes properties by querying them once.
        This adapts the old get_all() logic to the new QkitProperty system.
        """
        logging.info(f"{self._name}: Performing initial property refresh.")
        # Accessing the properties via their getters to populate internal caches
        # For properties that query the instrument, this will perform an 'ask'.
        _ = self.averages
        _ = self.nop
        _ = self.power
        _ = self.startfreq
        _ = self.stopfreq
        _ = self.centerfreq
        _ = self.sweeptime
        _ = self.sweepmode
        _ = self.rf_output
        _ = self.edel # This one has complex logic, ensure it works.
        _ = self.Average # Boolean property
        _ = self.bandwidth
        _ = self.cw # Boolean property
        _ = self.cwfreq # Depends on cw_mode


    # --- REMOVED METHODS ---
    # The following methods have been REMOVED as their functionality is now handled
    # by the PrologixGPIBInstrument base class or by the new @QkitProperty/Function system.
    # def write(self,msg): ...
    # def ask(self, msg): ...
    # def ask_for_values(self, msg, **kwargs): ...
    # def do_get_Average(self): ...
    # def do_set_Average(self, value): ...
    # ... and all other do_get_X / do_set_X methods