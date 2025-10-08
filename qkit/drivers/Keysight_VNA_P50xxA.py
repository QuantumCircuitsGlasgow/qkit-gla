# Keysight P50xxA/P5004A Streamline Series USB VNA
# Joao Barbosa <j.barbosa.1@research.gla.ac.uk>, 2021

import logging
from time import sleep

import numpy as np

from qkit import visa
from qkit.core.instrument_base import Instrument


class Keysight_VNA_P50xxA(Instrument):
    """
    Driver class for Keysight P50xxA/P5004A Streamline Series USB VNA
    Usage:
        vna=
        qkit.instruments.create("vna", "Keysight_VNA_P50xxA", address=<TCPIP address>)
        vna.gets_()
        vna.sets_()
        vna.some_function()
        ...
    Address for this instrument is only available after initializing the instrument through the "Network Analyzer" software. Currently it is not possible to communicate with it without this proxy software.
    """

    def __init__(self, name, address, channel_id=1, cw_mode=False) -> None:
        logging.info(__name__ + " : Initializing instrument")
        super().__init__(name, tags=["physical"])

        self._address = address
        self._visainstrument = visa.instrument(self._address)

        self._ci = int(channel_id)
        self.cw_mode = cw_mode
        self._edel = 0
        # self._freqpoints=None
        # self._nop=None
        # self._startfreq=None
        # self._stopfreq=None

        self.add_parameter(
            "averages", flag=Instrument.FLAG_GETSET, type=int, units="", minval=1
        )
        self.add_parameter("Average", type=bool)
        self.add_parameter(
            "bandwidth",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=1,
            maxval=15e6,
        )
        self.add_parameter(
            "centerfreq",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=9e3,
            maxval=20e9,
        )
        self.add_parameter("cw", type=bool)
        self.add_parameter(
            "cwfreq",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=10e6,
            maxval=20e9,
        )
        self.add_parameter(
            "edel",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="s",
            minval=-10,
            maxval=10,
        )
        self.add_parameter(
            "nop",
            flag=Instrument.FLAG_GETSET,
            type=int,
            units="",
            minval=1,
            maxval=1e5,
            tags=["sweep"],
        )
        self.add_parameter(
            "power",
            flag=Instrument.FLAG_GETSET,
            type=float,
            minval=-100,
            maxval=+20,
            units="dBm",
        )
        self.add_parameter(
            "rf_output", flag=Instrument.FLAG_GETSET, type=bool, units=""
        )
        self.add_parameter("s_parameter", flag=Instrument.FLAG_GETSET, type=str)
        self.add_parameter(
            "span",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=70,
            maxval=20e9,
        )
        self.add_parameter(
            "startfreq",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=9e3,
            maxval=20e9,
        )
        self.add_parameter(
            "stopfreq",
            flag=Instrument.FLAG_GETSET,
            type=float,
            units="Hz",
            minval=9e3,
            maxval=20e9,
        )
        self.add_parameter("sweepmode", flag=Instrument.FLAG_GETSET, type=str)
        self.add_parameter(
            "sweeptime",
            flag=Instrument.FLAG_GET,
            type=float,
            units="s",
            minval=0,
            maxval=1e3,
        )
        self.add_parameter(
            "sweeptime_averages",
            flag=Instrument.FLAG_GET,
            type=float,
            units="s",
            minval=0,
            maxval=1e3,
        )

        self.add_function("reset")
        self.add_function("hold")
        self.add_function("avg_clear")
        self.add_function("data_format")
        self.add_function("set_sweeptime_auto")
        self.add_function("get_tracedata")
        self.add_function("get_freqpoints")
        self.add_function("ready")
        self.add_function("start_measurement")
        self.add_function("pre_measurement")
        self.add_function("post_measurement")
        self.add_function("get_span")

        self.get_all()

    def get_all(self):
        self.get_averages()
        self.get_nop()
        self.get_power()
        self.get_startfreq()
        self.get_stopfreq()
        self.get_centerfreq()
        self.get_sweeptime()
        self.get_sweepmode()
        self.get_rf_output()

    ###
    ###

    def reset(self):
        self.write("*RST")
        return

    def ready(self):
        """
        This is a proxy function, returning True when the VNA has finished the required number of averages.
        Averaging must be on (even if it is just one average)
        Trace1 -> 0b10
        Trace2 -> 0b100
        ...
        Trace14 ->0b100 0000 0000 0000
        """
        if self.get_averages() == 1:
            if self.get_sweepmode() == "HOLD\n":
                return True
            else:
                return False

        return int(self.ask("STAT:OPER:AVER1:COND?")) & 0b10

    def hold(self, value):
        if value:
            self.write(f"SENS{self._ci}:SWE:MODE HOLD")
        else:
            self.write(f"SENS{self._ci}:SWE:MODE CONT")

    def avg_clear(self):
        self.write(f"SENS{self._ci}:AVER:CLE")

    def data_format(self, value="ASC"):
        if value == "ASC":
            self.write("FORM ASC")
        elif value == "REAL32":
            self.write("FORM REAL,32")
        elif value == "REAL64":
            self.write("FORM REAL,64")
        else:
            raise ValueError("Incorrect data format. Use: ['ASC','REAL32','REAL64']")

    def set_sweeptime_auto(self):
        self.write(f"SENS{self._ci}:SWE:TIME:AUTO ON")

    def get_tracedata(self, format="AmpPha"):
        self.write("FORM REAL,32")  # for now use Real 32 bit data format
        self.write("FORM:BORD SWAPPED")  # byte order for GPIB data transfer

        data = self.ask_for_values(f"CALC{self._ci}:MEAS:DATA:SDATA?")
        dataRe = np.array(data[::2])
        dataIm = np.array(data[1::2])

        if format == "AmpPha":
            if self.cw_mode:
                datacomplex = [np.mean(dataRe + 1j * dataIm)]
                dataAmp = np.abs(datacomplex)
                dataPha = np.angle(datacomplex)
            else:
                dataAmp = np.sqrt(dataRe**2 + dataIm**2)
                dataPha = np.arctan2(dataIm, dataRe)

            return dataAmp, dataPha
        elif format == "RealImag":
            if self.cw_mode:
                dataRe = np.mean(dataRe)
                dataIm = np.mean(dataIm)

            return dataRe, dataIm
        else:
            raise ValueError("get_tracedata(): Format must be AmpPha or RealImag")

    def get_freqpoints(self):
        self.write("FORM REAL,64")
        self.write("FORM:BORD SWAPPED")

        if self.cw_mode:
            return self.get_cwfreq()
        else:
            return self.ask_for_values(
                f"CALC{self._ci}:MEAS:DATA:X?", format=visa.double
            )

    ### GETs / SETs ###
    def do_get_Average(self):
        return self.ask(f"SENS{self._ci}:AVER?")

    def do_set_Average(self, value):
        value = 1 if value else 0
        self.write(f"SENS{self._ci}:AVER {value}")
        return

    def do_get_averages(self):
        return self.ask(f"SENS{self._ci}:AVER:COUN?")

    def do_set_averages(self, value):
        self.write(f"SENS{self._ci}:AVER:COUN {value}")

    def do_get_bandwidth(self):
        return self.ask(f"SENS{self._ci}:BWID?")

    def do_set_bandwidth(self, value):
        self.write(f"SENS{self._ci}:BWID {value}")
        return

    def do_get_centerfreq(self):
        return self.ask(f"SENS{self._ci}:FREQ:CENT?")

    def do_set_centerfreq(self, value):
        self.write(f"SENS{self._ci}:FREQ:CENT {value}")

    def do_get_cw(self):
        return self.cw_mode

    def do_set_cw(self, status=1):
        if status:
            self.write(f"SENS{self._ci}:SWEEP:TYPE CW")
            self.cw_mode = True
        else:
            self.write(f"SENS{self._ci}:SWEEP:TYPE LIN")
            self.cw_mode = False
        return

    def do_get_cwfreq(self):
        return self.ask(f"SENS{self._ci}:FREQ:CW?")

    def do_set_cwfreq(self, value):
        if self.cw_mode:
            self.write(f"SENS{self._ci}:FREQ:CW {value}")
        else:
            raise ValueError("VNA not in CW mode.")
        return

    def do_get_edel(self):
        # needs to first select the active measurement with CALC{}:PAR:SEL. All meas available through CALC{}:PAR:CAT?
        ch_sel = self.ask(f"CALC{self._ci}:PAR:SEL?").strip("\n")
        if ch_sel == '""':
            ch_ = self.ask(
                f"CALC{self._ci}:PAR:CAT?"
            )  # for now we select the first measurement chnl
            self.write(
                "CALC{}:PAR:SEL {}".format(self._ci, ch_.strip('"').split(",")[0])
            )
        self._edel = self.ask(f"CALC{self._ci}:CORR:EDEL:TIME?")
        return self._edel

    def do_set_edel(self, value):
        ch_sel = self.ask(f"CALC{self._ci}:PAR:SEL?").strip("\n")
        if ch_sel == '""':
            ch_ = self.ask(f"CALC{self._ci}:PAR:CAT?")
            self.write(
                "CALC{}:PAR:SEL {}".format(self._ci, ch_.strip('"').split(",")[0])
            )
        self.write(f"CALC{self._ci}:CORR:EDEL:TIME {value}")
        self._edel = value
        return

    def do_get_nop(self):
        return self.ask(f"SENS{self._ci}:SWE:POIN?")

    def do_set_nop(self, value):
        return self.write(f"SENS{self._ci}:SWE:POIN {value}")

    def do_get_rf_output(self):
        return self.ask("OUTP?")

    def do_set_rf_output(self, state=True):
        return self.write(f"OUTP {state}")

    def do_get_power(self, port=1):
        return self.ask(f"SOUR{self._ci}:POW{port}?")

    def do_set_power(self, value, port=1):
        return self.write(f"SOUR{self._ci}:POW{port} {value}")

    def do_get_s_parameter(self):
        return self.ask("CALC:MEAS:PAR?")

    def do_set_s_parameter(self, value):
        self.write("CALC:MEAS:PAR " + value)
        return

    def do_get_span(self):
        return self.ask(f"SENS{self._ci}:FREQ:SPAN?")

    def do_set_span(self, value):
        self.write(f"SENS{self._ci}:FREQ:SPAN {value}")
        return

    def do_get_startfreq(self):
        return self.ask(f"SENS{self._ci}:FREQ:START?")

    def do_set_startfreq(self, value):
        self.write(f"SENS{self._ci}:FREQ:START {value}")

    def do_get_stopfreq(self):
        return self.ask(f"SENS{self._ci}:FREQ:STOP?")

    def do_set_stopfreq(self, value):
        self.write(f"SENS{self._ci}:FREQ:STOP {value}")

    def do_get_sweepmode(self):
        return self.ask(f"SENS{self._ci}:SWE:MODE?")

    def do_set_sweepmode(self, value):
        if value in ["CONT", "HOLD", "SING", "GRO"]:
            return self.write(f"SENS{self._ci}:SWE:MODE {value}")
        else:
            raise ValueError('Sweep mode unknown. Use: ["CONT","HOLD","SING","GRO"]')
        return

    def do_get_sweeptime(self):
        return self.ask(f"SENS{self._ci}:SWE:TIME?")

    def do_get_sweeptime_averages(self):
        return self.get_sweeptime() * self.get_averages()

    ### COMM ###
    def write(self, msg):
        return self._visainstrument.write(msg)

    if visa.qkit_visa_version == 1:

        def ask(self, msg):
            return self._visainstrument.ask(msg)

        def ask_for_values(self, msg, **kwargs):
            return self._visainstrument.ask_for_values(kwargs)

    else:

        def ask(self, msg):
            return self._visainstrument.query(msg)

        def ask_for_values(self, msg, format=None, fmt=None):
            dtype = (
                format
                if format is not None
                else fmt
                if fmt is not None
                else visa.single
            )
            dtype = visa.dtypes[dtype]
            return self._visainstrument.query_binary_values(
                msg, datatype=dtype, container=np.array
            )

    def pre_measurement(self):
        self.write("TRIG:SOUR MAN")
        self.set_sweepmode("CONT")
        self.write(f"SENS{self._ci}:AVER ON")

    def start_measurement(self):
        if self.get_averages() == 1:
            self.set_sweepmode("HOLD")
            sleep(0.05)
            self.write("INIT:IMM")
        else:
            self.avg_clear()
            for i in range(self.get_averages()):
                while True:
                    if int(self.ask("TRIG:STAT:READ? MAN")):
                        break
                    sleep(0.05)
                self.write("INIT:IMM")
                sleep(0.1)

    def post_measurement(self):
        self.write("TRIG:SOUR IMM")
        self.write(f"SENS{self._ci}:AVER OFF")
        self.hold(False)
