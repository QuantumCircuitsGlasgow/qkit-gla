# filename: Keithley_2450.py
# version 0.1 written by
# QKIT driver for a Keithley Multimeter 2450
# Updated by Chisha & Joao <j.barbosa.1@research.gla.ac.uk> 2023

import logging

import numpy

from qkit import visa
from qkit.core.instrument_base import Instrument


class Keithley_2450(Instrument):
    """
    This is the driver for the Keithley 2450 Source Meter
    Set ip address manually on instrument, e.g. TCPIP::10.22.197.50::5025::SOCKET
    Usage:
    Initialize with
    <name> = qkit.instruments.create('<name>', 'Keithley_2450', address='<IP address>', reset=<bool>)
    """

    def __init__(self, name, address, reset=False):
        """
        Initializes the Keithley, and communicates with the wrapper.

        Input:
            name (string)    : name of the instrument
            address (string) : IP address
            reset (bool)     : resets to default values, default=False
        """
        # Start VISA communication
        logging.info(__name__ + ": Initializing instrument Keithley 2450")
        Instrument.__init__(self, name, tags=["physical"])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._visainstrument.read_termination = "\n"
        self._visainstrument.timeout = (
            1000000  # big timeout required to wait for long sweeps
        )
        self.rvc_mode = False  # resistance via current
        self.four_wire = False
        self.meas_delay = 0.1  # delay between measurements in sweeps
        self.bufferElementTable = {  # table of the possible options for bufferElements when used (specified in manual)
            "DATE": "The date when the data point was measured",
            "FORM": "The measured value as it appears on the front panel",
            "FRAC": "The fractional seconds for the data point when the data point was measured",
            "READ": "The measurement reading based on the SENS:FUNC setting; if no buffer elements are defined, this option is used",
            "REL": "The relative time when the data point was measured",
            "SEC": "The seconds in UTC (Coordinated Universal Time) format when the data point was measured",
            "SOUR": "The source value; if readback is ON, then it is the readback value, otherwise it is the programmed source value",
            "SOURFORM": "The source value as it appears on the display",
            "SOURSTAT": "The status information associated with sourcing",
            "SOURUNIT": "The unit of value associated with the source value",
            "STAT": "The status information associated with the measurement The time for the data point",
            "TIME": "The timestamp for the data point",
            "UNIT": "The unit of measure associated with the measurement",
        }
        self.possibleModes = [
            "CURR",
            "VOLT",
            "RES",
        ]  # keithley can only be in these modes
        self.possibleBoundaries = ["MIN", "MAX", "DEF"]
        # self.setup(address) #used for GPIB connections

    def query(self, command):
        return self._visainstrument.query(command)

    def write(self, command):
        self._visainstrument.write(command)

    def reset(self):
        """
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        """
        logging.info(__name__ + " : resetting instrument")
        self._visainstrument.write("*RST")
        # self.get_all()

    def get_voltage(self):
        return self._visainstrument.query("SOUR:VOLT:LEV?")

    def get_current_dc(self):  # Return DC Current in auto-range
        value = self._visainstrument.query(":MEAS:CURR:DC?")
        try:
            return float(value)
        except Exception as m:
            print(m)
            return

    def get_voltage_dc(self):  # Return DC Current in auto-range
        value = self._visainstrument.query(":MEAS:VOLT:DC?")
        try:
            return float(value)
        except Exception as m:
            print(m)
            return

    def set_voltage_limit(self, limit):
        self._visainstrument.write(f"SOUR:CURR:VLIM {limit}")

    def set_current_limit(self, limit):
        self._visainstrument.write(f"SOUR:VOLT:ILIM {limit}")

    def get_resistance_2W(self):
        try:
            self._visainstrument.write(":OUTP ON")
            ret = self._visainstrument.query(":MEAS:RES?")
            self._visainstrument.write(":OUTP OFF")
            return float(ret)

        except ValueError as e:
            print(e)
            print(ret)
            return numpy.NaN

    def get_resistance_4W(self):
        try:
            self._visainstrument.write(":OUTP ON")
            ret = self._visainstrument.query(":MEAS:RES?")
            self._visainstrument.write(":OUTP OFF")
            return float(ret)
        except ValueError as e:
            print(e)
            print(ret)
            return numpy.NaN

    def set_4W(self, N=1):
        """Sets 2 or 4 wire measurement mode
        0 - 2-wire measurement, and 1 - 4-wire measurement"""
        if N:
            self.four_wire = True
        else:
            self.four_wire = False

        mode = self.get_sense_mode()
        if "VOLT" in mode:
            self._visainstrument.write(f"VOLT:RSEN {N}")
        elif "CURR" in mode:
            self._visainstrument.write(f"CURR:RSEN {N}")
        else:
            raise Exception("Non defined sensing mode (VOLT or CURR only)")
        return

    def set_output(self, state):
        self._visainstrument.write(f":OUTP {state}")

    def get_output(self):
        self._visainstrument.write(":OUTP?")

    def set_current_range(self, range_value):
        self._visainstrument.write(f":SENS:CURR:RANG {range_value}")

    def set_voltage_source(self, volt):
        # self._visainstrument.write("SENS:FUNC 'CURR'")
        self._visainstrument.write("SOUR:FUNC VOLT")
        self._visainstrument.write(f"SOUR:VOLT {volt}")

    def set_current_source(self, curr):
        # self._visainstrument.write("SENS:FUNC 'VOLT'")
        self._visainstrument.write("SOUR:FUNC CURR")
        self._visainstrument.write(f"SOUR:CURR {curr}")

    def set_voltage_range(self, range_value):
        self._visainstrument.write(f":SENS:VOLT:RANG {range_value}")

    def set_current_range_auto(self, auto):
        if auto:
            self._visainstrument.write(":SENS:CURR:RANG:AUTO ON")
        else:
            self._visainstrument.write(":SENS:CURR:RANG:AUTO OFF")

    def set_voltage_range_auto(self, auto):
        if auto:
            self._visainstrument.write(":SENS:VOLT:RANG:AUTO ON")
        else:
            self._visainstrument.write(":SENS:VOLT:RANG:AUTO OFF")

    def set_nplc(self, nplc):
        """
        Sets the number of power line cycles, aka, the time that the input signal is measured for

        Parameters
        -------
        nplc: number of cycles (time= nplc/60Hz in seconds)
        """
        mode = self.get_sense_mode()
        if "VOLT" in mode:
            self._visainstrument.write(f"VOLT:NPLC {nplc}")
        elif "CURR" in mode:
            self._visainstrument.write(f"CURR:NPLC {nplc}")
        else:
            raise Exception("Non defined sensing mode (VOLT or CURR only)")
        return

    def get_nplc(self):
        """
        Gets number of power line cycles
        """
        mode = self.get_sense_mode()
        if "VOLT" in mode:
            return self._visainstrument.query("VOLT:NPLC?")
        elif "CURR" in mode:
            return self._visainstrument.write("CURR:NPLC?")
        else:
            raise Exception("Non defined sensing mode (VOLT or CURR only)")

    def printBufferElementTable(self, includeDetails=False):
        """Print out the buffer element table, with an option to include the details of each element"""
        if includeDetails:
            print("Possible buffer elements, including descriptions:")
            for elmt, desc in self.bufferElementTable.items():
                print(
                    f"'{elmt}': {desc}"
                )
        else:
            print("Possible buffer elements:")
            print("\n".join(self.bufferElementTable.keys()))

    def _validateParameters(
        self,
        mode: str = None,
        readingElements: "tuple[str,...]" = None,
        boundary: str = None,
    ) -> "tuple[bool, str]":
        """
        For each scpi function, call this method and provide the relevant parameters to validate entries

        Returns a (bool,str) tuple, where 1st element (bool) indicates true/false for success/failure
         and 2nd element (str) indicates description of failure

        Leave the unwanted parameters = None if you dont want to validate them

        Supported parameters:
        - readingElements (refer to bufferElementsTable)
        - mode ('CURR', 'VOLT' 'RES')
        - boundary ('DEF', 'MIN', 'MAX')
        """
        logging.debug("Validating Parameters")
        if mode != None:
            mode = mode.upper()
            if mode not in self.possibleModes:
                return (False, "Invalid mode")

        if readingElements != None or len(readingElements) == 0:
            for i in readingElements:  # making sure each buffer element is correct
                if i.upper() not in self.bufferElementTable:
                    return (False, "Invalid Buffer Element")

        if (boundary != None) & (boundary.upper() not in self.possibleBoundaries):
            return (False, "Invalid boundary values")

        return (True, "")
        # then return true if all checks go fine

    def get_latest_reading(self, bufferName: str = "defbuffer1", *readingElements: str):
        """
        Returns the latest reading from a given/default reading buffer

        - 'bufferName': (optional) name of buffer where 'defbuffer1' is the default buffer

        - 'readingElements': (optional) variadic paramters (up to of 14) determining what aspects of the reading get returned
            E.g: 'DATE', 'UNIT'

        Note: if you want to add readingElements, you need to specify bufferName first

        If you're not sure what bufferName to use, use 'defbuffer1' (default)
        """
        logging.debug("Getting latest reading")
        # preventive error handling
        test = self._validateParameters(None, readingElements)
        if test[0] == False:
            print("Error:", test[1])
            return None
        if (
            len(readingElements) > 0
        ):  # for correct formatting of query, need to handle differently if no elements passed
            return self._visainstrument.query(
                ':FETCh "{bName}", {elements}'.format(
                    bName=bufferName, elements=", ".join(readingElements)
                )
            )
        else:
            return self._visainstrument.query(
                f':FETCh "{bufferName}"'
            )  # just get the plain reading as it is

    def make_measurement(
        self, mode: str, bufferName: str = "defbuffer1", *readingElements: str
    ):
        """
        Makes a measurement using the specified function mode, stores and returns the measurement in a reading buffer

        - 'mode': specify either 'CURR', 'RES', 'VOLT' to get a current, resistance or voltage measurement respectively

        - 'bufferName': (optional) name of buffer where 'defbuffer1' is the default buffer

        - 'readingElements': (optional) variadic paramters (up to 14) determining what aspects of the reading get returned (look up bufferElementTable)

        Note:

            - if you want to add readingElements, you need to specify bufferName first

            - If you're not sure what bufferName to use, use 'defbuffer1' (default)

            - the 'mode' parameter will change the measurement function to the specified one, and this change will persist
        """
        logging.debug("Making measurement")
        test = self._validateParameters(mode, readingElements)
        if test[0] == False:
            print("Error:", test[1])
            return None
        if len(readingElements) > 0:
            return self._visainstrument.query(
                ':MEAS:{mode}? "{bName}", {elements}'.format(
                    mode=mode, bName=bufferName, elements=", ".join(readingElements)
                )
            )
        else:
            return self._visainstrument.query(
                f':MEAS:{mode}? "{bufferName}"'
            )

    # Display (:DISPlay) function
    def set_display_digits(self, numDigits: int, mode: str = None):
        """
        Set the number of digits displayed on the front panel for a given measurement function (changes will persist)
         - 'mode': specify either 'CURR', 'RES', 'VOLT' to get current, resistance or voltage measurement functions respectively
                - if mode is set to None, then all 3 measurement functions will be changed
         - 'numDigits': the number of digits to set the display to. Use an integer value

        Note: this does NOT affect the accuracy or speed of measurements.
        """
        logging.debug("Setting display digits")
        test = self._validateParameters(mode)
        if test[0] == False:
            print("Error:", test[1])
            return None
        numDigits = str(numDigits)
        if mode == None:  # then all 3 measurement functions get changed
            self._visainstrument.write(f":DISP:DIG {numDigits}")
        else:
            self._visainstrument.write(
                f":DISP:{mode}:DIG: {numDigits}"
            )

    def get_display_digits(self, mode: str, boundary: str = None):
        """
        Get the number of digits dispayed for a given measurement function
        - 'mode': specify either 'CURR', 'RES', 'VOLT' to get current, resistance or voltage measurement functions respectively
        - 'boundary': (optional) specify the following string values to get the relevant data:
                - DEF to get to the default number of digits
                - MIN to get to the minimum number of digits allowed
                - MAX to get to the maximum number of digits allowed
        """
        logging.debug("getting number of digits displayed")
        test = self._validateParameters(mode, None, boundary)
        if test[0] == False:
            print("Error:", test[1])
            return None
        if boundary == None:
            return float(
                self._visainstrument.query(f":DISP:{mode}:DIG?")
            )
        else:
            return float(
                self._visainstrument.query(
                    f":DISP:{mode}:DIG? {boundary}"
                )
            )

    def get_bias_mode(self):
        """
        Gets bias mode <mode>.

        Returns
        -------
        mode: String
            Bias mode. "VOLT" for voltage, "CURR" for current
        """
        return self._visainstrument.query(":SOUR:FUNC?")

    def get_sense_mode(self):
        """
        Gets sense mode <mode>.

        Returns
        -------
        mode: String
            Bias mode. "VOLT" for voltage, "CURR" for current
        """
        return self._visainstrument.query(":SENS:FUNC?")

    def get_sweep_mode(self):  # find manual for setting the sweep "mode"
        """
        Either:
         * voltage is both applied and measured (VV-mode),
         * current is applied and voltage is measured (IV-mode),
         * voltage is applied and current is measured (VI-mode),
         * current is both applied and measured (II-mode).

        Parameters
        ----------
        None

        Returns
        -------
        mode: int
            Sweep mode denoting bias and sense modes. Meanings are 0 (VV-mode), 1 (IV-mode), 2 (VI-mode), or 3 (II-mode).
        """
        sourceMode = (
            self.get_bias_mode()
        )  # the independent variable that will be swept over
        senseMode = (
            self.get_sense_mode()
        )  # the dependant variable that will be measured
        # print(sourceMode,senseMode)
        if "VOLT" in sourceMode and "VOLT" in senseMode:
            return 0  # VV mode
        elif "CURR" in sourceMode and "VOLT" in senseMode:
            return 1  # IV mode
        elif "VOLT" in sourceMode and "CURR" in senseMode:
            return 2  # VI mode
        elif "CURR" in sourceMode and "CURR" in senseMode:
            return 3  # II mode
        else:
            raise ValueError("Unkown sweep mode")

    def set_sweep_mode(self, sourceMode, measureMode):
        """
         Parameters
        ----------
        - sourceMode: mode to sweep. Either 'VOLTage' or 'CURR'
        - measureMode: mode to measure sweep of. Either 'VOLT' or 'CURR'

        Either:
         * voltage is both applied and measured (VV-mode),
         * current is applied and voltage is measured (IV-mode),
         * voltage is applied and current is measured (VI-mode),
         * current is both applied and measured (II-mode).

        Returns
        -------
         None
        """
        # first validate the modes
        if sourceMode not in ["CURR", "VOLT", "CURRent", "VOLTage"]:
            print("Sorry, invalid source mode passed. Please use 'CURR' or 'VOLT")
            raise ValueError("Invalid sourceMode passed")
        elif measureMode not in ["CURR", "VOLT", "CURRent", "VOLTage"]:
            print("Sorry, invalid measure mode passed. Please use 'CURR' or 'VOLT")
            raise ValueError("Invalid measureMode passed")
        self._visainstrument.write("*CLS")
        self._visainstrument.write(
            f":SOUR:FUNC {sourceMode}"
        )
        self._visainstrument.write(
            f':SENS:FUNC "{measureMode}"'
        )

    def get_sweep_bias(self):
        """
        Calls get_bias_mode. This method is needed for qkit.measure.transport.transport.py in case of no virtual tunnel electronic.

        Parameters
        ----------
        None

        Returns
        -------
        mode: int
            Bias mode. Meanings are 0 (current) and 1 (voltage).
        """
        biasMode: str = self.get_bias_mode()
        if biasMode == "CURR":
            return 0
        elif biasMode == "VOLT":
            return 1
        else:
            raise ValueError("Unkown bias mode")

    def get_sweep_channels(self):  # always return 1
        """
        Due to the functionality of the Keithlet 2450, there is only 1 channel.

        So this function will only return 1 (though is still needed to be compatible with transport class)
        """
        return [1]

    def set_status(self, status: int, channel=[1]):  # should be able to do
        """
        This command enables or disables the source output

        Parameters
        ----------
        status: int
            Output status. Possible values are 0 (off) and 1 (on)
        """
        if status == True:
            status = 1
        if status == False:
            status = 0
        if status in [0, 1]:
            self._visainstrument.write(f":OUTP {status}")
        else:
            raise Exception("Wrong Status (must be 0 or 1)")

    def get_status(self):
        """
        This command simply checks if the source output is on or off
        """
        return self._visainstrument.query(":OUTP?")

    def take_IV(self, sweep):  # this one should do all 4 (IV, VV, VI, II)
        """
        Takes IV curve with sweep parameters <sweep> in the sweep mode predefined.

        Parameters
        ----------
        sweep: 5 element float list where :
            - sweep[0] is the start value
            - sweep[1] is the stop value
            - sweep[2] is the step width (MUST BE GREATER THAN 0)
            - sweep[3] is the delay between measuring points (in seconds)
            - sweep[4] is the number of times to perform the sweep (0 for infinite loop)

        Returns
        -------
        bias_values: numpy.array(float)
            Measured bias values.
        sense_values: numpy.array(float)
            Measured sense values.
        """
        self._visainstrument.write(":TRAC:CLE 'defbuffer1'")  # first clear the buffer
        logging.debug("CLEARING BUFFER----------->")
        try:
            start = sweep[0]
            stop = sweep[1]
            step = sweep[2]
            delay = self.meas_delay  # sweep[3]
            count = 1  # sweep[4]
        except:
            print("Invalid sweep parameter. Provide a 5 element array")
            return
        # setting up sweep parameters
        numSteps = (
            int(numpy.abs(stop - start) / step) + 1
        )  # needed for reading out data
        sweepMode = self.get_sweep_mode()
        bias = self.get_bias_mode()  # so that we correctly write the sweep command
        if sweepMode == 0:  # VV mode
            self._visainstrument.write(':SENS:FUNC "VOLT"')
            print("Sweeping voltage, measuring voltage")
        elif sweepMode == 1:  # IV mode
            self._visainstrument.write(':SENS:FUNC "VOLT"')
            print("Sweeping current, measuring voltage")
        elif sweepMode == 2:  # VI mode
            self._visainstrument.write(':SENS:FUNC "CURR"')
            print("Sweeping voltage, measuring current")
        elif sweepMode == 3:  # II mode
            self._visainstrument.write(':SENS:FUNC "CURR"')
            print("Sweeping current, measuring current")
        else:
            print("Invalid sweep mode passed in")
            return ValueError("Invalid sweep mode")
        self._visainstrument.write("TRACe:FILL:MODE CONT")  # fill mode
        self._visainstrument.write(
            ":SOUR:SWE:{bias}:LIN:STEP {start}, {stop}, {step}, {delay}, {count}, BEST, OFF,OFF".format(
                bias=bias, start=start, stop=stop, step=step, delay=delay, count=count
            )
        )
        self._visainstrument.write(":INIT")
        self._visainstrument.write(
            "*WAI"
        )  # waits until sweep is finished until executing next command

        # time.sleep(delay*numSteps*3)
        logging.debug(f"steps = {numSteps}")

        measuredArray = self._visainstrument.query(
            f":TRAC:DATA? 1, {numSteps}"
        )
        sourceArray = self._visainstrument.query(
            f":TRAC:DATA? 1, {numSteps}, 'defbuffer1', SOUR"
        )
        measuredArray = [float(i) for i in measuredArray.strip("\n").split(",")]
        sourceArray = [float(i) for i in sourceArray.strip("\n").split(",")]
        return sourceArray, measuredArray


if __name__ == "__main__":
    KEITH = Keithley_2450_gla(name="Keithley_2450_gla", address="10.22.197.8")
    print(f"DC current: {KEITH.get_current_dc():.4g}A")
