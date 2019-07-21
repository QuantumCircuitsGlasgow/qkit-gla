"""Module to provide a high-level possibility to arange pulses for an experiment."""

from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from inspect import getargspec as getargspec
from inspect import getsourcelines as getsourcelines
from typing import Dict, Set
import logging


class Shape(np.vectorize):
    """
    A vectorized function describing a possible shape
    defined on the standardized interval [0,1).
    """

    def __init__(self, name, func, *args, **kwargs):
        self.name = name
        super(Shape, self).__init__(func, *args, **kwargs)

    def __mul__(self, other):
        return Shape(self.name, lambda x: self.pyfunc(x) * other.pyfunc(x))


class ShapeLib(object):
    """
    Object containing pre-defined pulse shapes.
    Currently implemented: rect, gauss
    """

    def __init__(self):
        self.zero = Shape("", lambda x: 0)
        self.rect = Shape("rect", lambda x: np.where(x >= 0 and x < 1, 1, 0))
        self.gauss = Shape("gauss", lambda x: np.exp(-0.5 *
                                                     np.power((x - 0.5) / 0.166, 2.0))) * self.rect


# Make ShapeLib a singleton:
ShapeLib = ShapeLib()


class PulseType(Enum):
    """Type of Pulse object"""
    Pulse = 1
    Wait = 2
    Readout = 3


class Pulse(object):
    """
    Class to describe a single pulse.
    """

    def __init__(self, length, shape=ShapeLib.rect, name=None, amplitude=1, phase=0, iq_frequency=0, iq_dc_offset=0, iq_angle=90, ptype=PulseType.Pulse):
        """
        Inits a pulse with:
            length:       length of the pulse. This can also be a (lambda) function for variable pulse lengths.
            shape:        pulse shape (i.e. rect, gauss, ...)
            name:         name you want to give your pulse (i.e. pi-pulse, ...)
            amplitude:    relative amplitude of your pulse
            phase:        phase of the pulse in deg. (i.e. 90 for pulse around y-axis of the bloch sphere)
            iq_frequency: IQ-frequency of your pulse for heterodyne mixing (if 0 homodyne mixing is employed)
            iq_dc_offset: complex dc offset for calibrating the IQ-mixer (real part for dc offset of I, imaginary part is dc offset of Q)
            iq_angle:     angle between I and Q in the complex plane (default is 90 deg)
            type:         The type of the created pulse (from enum PulseType: can be Pulse, Wait or Readout)
        """
        if isinstance(length, float) or callable(length):
            self.length = length  # type: float or lambda
        else:
            raise ValueError(
                "Pulse length is not understood. Only floats and functions returning floats are allowed.")

        self.shape = shape
        self.name = name  # type: string
        self.amplitude = amplitude  # type: float
        self.phase = phase  # type: float
        self.iq_frequency = iq_frequency  # type: float
        self.iq_dc_offset = iq_dc_offset
        self.iq_angle = iq_angle
        self.type = ptype  # type: PulseType

    def __call__(self, time_fractions):
        """
        Returns the envelope of the pulse as array for a given array of timesteps.

        Args:
            time_fractions: normalized time for the shape of the pulse

        Returns:
            envelope of the pulse as numpy array.
        """
        # Pulse class can be called like a vectorized function!
        return self.amplitude * self.shape(time_fractions)

    def get_envelope(self, samplerate):
        """
        Returns the envelope of the pulse as array with given time steps.

        Args:
            samplerate: samplerate for calculating the envelope

        Returns:
            envelope of the pulse as numpy array
        """
        timestep = 1. / samplerate
        if callable(self.length):
            print("This pulse has a variable length.")
            return 0
        time_fractions = np.arange(0, self.length, timestep) / self.length
        return self(time_fractions)

    def get_complex_envelope(self, samplerate):
        """
        Returns the envelope of the pulse as array with given time steps.

        Args:
            samplerate: samplerate for calculating the envelope

        Returns:
            envelope of the pulse as numpy array
        """
        timestep = 1. / samplerate
        envelope = self.get_envelope(samplerate)
        if self.iq_frequency is 0:
            # for homodyne mixing the envelope is real
            return envelope
        time = np.arange(0, self.length, timestep)
        envelope_complex = envelope * \
            np.exp(1.j * (2*np.pi * self.iq_frequency *
                          time - np.pi/180 * self.phase))
        # adjust angle between I and Q by rotating Q:
        I = np.real(envelope_complex)
        Q = np.imag(envelope_complex * np.exp(1.j *
                                              np.pi / 180 * (90 - self.iq_angle)))
        envelope_complex = I + 1.j * Q + self.iq_dc_offset
        return envelope_complex


class PulseSequence(object):
    """
    Class for aranging pulses for a time-domain experiment.
    Sequence objects are callable, returning the sequence envelope for a given time step.
    Add wait as variable times in the experiment.
    Add readout to synchornize different channels in more sophisticated experiments.

    Attributes:
        add:         adds a given pulse to the experiment
        add_wait:    adds a wait time
        add_readout: adds the readout to the experiment
        plot:        plots schematic of the sequence
        get_pulses:  returns list of currently added pulses and their properties.
    """

    def __init__(self, sample=None, samplerate=None, dc_corr=0):
        """
        Inits PulseSequence with sample and samplerate:
            sample:     Sample object
            samplerate: Samplerate of your device
                        This should already be specified in your sample object as sample.clock
            dc_corr:    DC Voltage bias of the AWG for idling times (Real p)complex dc offset for calibrating the IQ-mixer during idling times.
                        The real part encodes the dc offset of I, the imaginary part is the dc offset of Q.
                        This correction is added to the dc offset during the pulse (i.e. of the pulse object).
        """
        self._sequence = []  # type: List[List[Pulse]]
        self._next_pulse_is_parallel = False
        self._pulses = {}  # type: Dict[str, Pulse]
        self._variables = set()  # type: Set[str]
        self._sample = sample
        self.dc_corr = dc_corr
        try:
            self.samplerate = self._sample.clock
        except AttributeError:
            self.samplerate = samplerate

        self._color_palette = ["C0", "C1", "C2", "C3", "C4", "C5",
                      "C6", "C8", "C9", "r", "g", "b", "y", "k", "m"]
        self._pulse_cols = {PulseType.Readout: "C7", PulseType.Wait: "w"}

    def __call__(self, IQ_mixing=False, **kwargs):
        """
        Returns the envelope of the whole pulse sequence for the input time.
        Also returns the index where the readout pulse starts.
        If no readout tone is found it is assumed to be at the end of the sequence.

        Args:
            IQ_mixing:   returns complex valued sequence if IQ_mixing is True (real part encodes I, imaginary part encodes Q)
            **kwargs:    function arguments for time dependent pulse lengths/wait times. Parameter names need to match time function parameters.


        Returns:
            waveform:      numpy array of the squence envelope, if IQ_mixing is True real part is I, imaginary part is Q
            readout_index: index of the readout tone
        """

        if self._variables != set(kwargs.keys()):
            logging.error("Given function arguments do not match with required ones. " +
                          "The following keyword arguments are required: {}.".format(", ".join(self._variables)))
            return

        if not self.samplerate:
            logging.error("Sequence call requires samplerate.")
            return

        # build the waveform of this sequence
        full_waveform = np.zeros(0)
        timestep = 1.0 / self.samplerate  # minimum time step
        readout_index = 0  # index of the readout in the waveform of the whole sequence
        position_of_next_slice = 0 # index where the next time slice will start
        for time_slice in self._sequence:
            wfm_slice = np.zeros(0)
            last_wfm_length = 0
            for pulse in time_slice:
                # Determine length of the pulse
                if callable(pulse.length):
                    required_arguments = {
                        k: v for k, v in kwargs.items()
                        if k in getargspec(pulse.length).args
                    }
                    length = pulse.length(**required_arguments)
                else:
                    length = pulse.length
                
                #if (pulse_dict["pulse"].type == PulseType.Readout) and (i == len(self._sequence) - 1):
                #    # if readout is last, omit the wfm (apart from a single digit)
                #    length = timestep

                # Warning if pulse is shorter than smallest possible step
                if (length < 0.5*timestep) and (length != 0):
                    logging.warning("{:}-pulse is shorter than {:.2f} nanoseconds and thus is omitted.".format(
                        pulse.name, 0.5*timestep*1e9))

                # create waveform array of the current pulse
                if pulse.type == PulseType.Pulse:
                    if length > 0.5*timestep:
                        wfm = pulse(np.arange(0, length, timestep) / length)
                    else:
                        wfm = np.zeros(0)
                else:
                    # Wait or Readout
                    # TODO Unify as these are normal pulses now
                    wfm = np.zeros(int(round(length * self.samplerate)))

                # Store index if this pulse is a readout pulse (will have the last one at the end)
                if pulse.type == PulseType.Readout:
                    readout_index = position_of_next_slice
                
                # Encode I and Q in real/imaginary part of the sequence
                iq_freq = pulse.iq_frequency
                # homodyne pulses are not mixed (iq_freq = 0)
                if IQ_mixing and iq_freq != 0:
                    # calculate I and Q
                    # adjust global phase relative to the beginning of the sequence
                    time = np.arange(position_of_next_slice, len(wfm)) * timestep
                    iq_phase = np.exp(
                        1.j * (2 * np.pi * iq_freq * time - np.pi/180 * pulse.phase))
                    wfm *= iq_phase
                    # account for mixer calibration i.e. dc offset and phase != 90deg between I and Q
                    if pulse.iq_angle != 90:
                        wfm_i = np.real(wfm)
                        wfm_q = np.imag(wfm * np.exp(1.j * np.pi / 180 * (90 - pulse.iq_angle)))
                        wfm = wfm_i + 1.j * wfm_q
                    wfm[wfm != 0] += pulse.iq_dc_offset

                # Add pulse to waveform of current time slice
                if len(wfm_slice) < len(wfm):
                    wfm_slice.resize(len(wfm))
                last_wfm_length = len(wfm)
                wfm.resize(len(wfm_slice))
                wfm_slice += wfm

            # Add current time slice to global waveform
            new_waveform_length = max(len(full_waveform), position_of_next_slice + len(wfm_slice))
            full_waveform.resize(new_waveform_length)
            wfm_slice_filled = np.zeros_like(full_waveform)
            wfm_slice_filled[position_of_next_slice:(position_of_next_slice + len(wfm_slice))] = wfm_slice
            full_waveform += wfm_slice_filled

            # Update position for next slice (the last waveform has no skip and thus decides the time)
            position_of_next_slice += last_wfm_length

        full_waveform += self.dc_corr
        # make sure first and last point of the waveform go to 0
        full_waveform = np.append(0, full_waveform)
        full_waveform = np.append(full_waveform, 0)
        return full_waveform, readout_index + 1 # +1 due to leading 0

    def add(self, pulse, skip=False):
        """
        Append a pulse to the sequence.

        Args:
            pulse: pulse object
            skip:  if True the next pulse in the sequence will not wait until this pulse is finished (i.e. they happen at the same time)
        """
        # Check if pulse name is valid and unique
        if pulse.name is None or not isinstance(pulse.name, str):
            logging.error(
                "The pulse name has to be a string and must not be None.")
            return self
        elif self._pulses.has_key(pulse.name) and not self._pulses[pulse.name] is pulse:
            logging.error("Another pulse with the same name ({name}) is already present in the sequence!".format(
                name=pulse.name))
            return self

        # Add the pulse to the pulse dictionary if it is not yet present
        if not self._pulses.has_key(pulse.name):
            self._pulses[pulse.name] = pulse

        if callable(pulse.length):
            # Keep track of all variable names: Add them to a set of unique variable names
            self._variables.update(getargspec(pulse.length).args)

        if not self._next_pulse_is_parallel:
            # Add empty list for next pulse
            self._sequence.append([])
        # Add pulse to last sequence slice
        self._sequence[-1].append(pulse)

        # If skip is true the next pulse will be scheduled at the same time
        self._next_pulse_is_parallel = skip

        return self

    def add_wait(self, time, name=None):
        """
        Add a wait time to the sequence.
        Use a (lambda) function for variable wait times.

        Args:
            time: float or function
            name: A special name can be passed for this wait block (by default, wait[#] will be used)
        """
        def compose_name(index):
            return "wait[{}]".format(index)

        if name is None:
            # Find a unused name for the next wait "pulse"
            wait_index = 0
            while self._pulses.has_key(compose_name(wait_index)):
                wait_index += 1
            name = compose_name(wait_index)

        wait_pulse = Pulse(time, shape=ShapeLib.zero,
                           name=name, ptype=PulseType.Wait)
        return self.add(wait_pulse)

    def add_readout(self, skip=False, pulse=None):
        """
        Add a readout pulse to the sequence.

        Args:
            skip: If True the next pulse will follow at the same time as the readout.
            pulse: A user-defined readout pulse can be specified if necessary.
        """
        def compose_name(index):
            return "readout[{}]".format(index)

        if pulse is None:
            # Find a unused name for the next readout pulse
            readout_index = 0
            while self._pulses.has_key(compose_name(readout_index)):
                readout_index += 1
            name = compose_name(readout_index)

            # Try to determine useful readout tone length
            try:
                readout_length = self._sample.readout_tone_length
            except AttributeError:
                readout_length = 0.

            # Create the readout pulse (just a symbolic placeholder)
            readout_pulse = Pulse(
                readout_length, shape=ShapeLib.zero, name=name, ptype=PulseType.Readout)
        else:
            # If a special pulse is needed, user can add it
            readout_pulse = pulse  # type: Pulse

            if readout_pulse.type != PulseType.Readout:
                readout_pulse.type = PulseType.Readout
                logging.warning(
                    "The type of the added pulse has to be Readout and was changed accordingly.")

        return self.add(readout_pulse)

    @property
    def variable_names(self):
        """A list with the names of all variables present in this sequence."""
        return self._variables

    def get_pulses(self):
        """
        Returns a list of all pulses and their properties. 
        The properties of each pulse are stored in a dictionary with keys: name, shape, length, skip value
        """
        dict_list = []
        for time_slice in self._sequence:
            for i, pulse in enumerate(time_slice):
                # This is more for legacy reasons
                dict_list.append({
                    "name": pulse.name,
                    "shape": pulse.shape.name,
                    "length": pulse.length,
                    "iq_frequency": pulse.iq_frequency,
                    "phase": pulse.phase,
                    "skip": i != len(time_slice) - 1
                })
        return dict_list

    def plot(self):
        """
        Plot a schematic of the stored pulses.
        """
        fig, ax = plt.subplots()
        amp = 1
        ampmax = 1
        remaining_colors = self._color_palette[:]
        pulse_colors = {}  # type: Dict[str, str]

        for i, time_slice in enumerate(self._sequence):
            for amp, pulse in enumerate(time_slice):
                ampmax = max(ampmax, amp + 1)
            
                # Generate displayed text
                text = "{name}\n{shape}\n{time}".format(
                    name=pulse.name,
                    shape=pulse.shape.name,
                    time=(
                        self._pulselength_as_str(pulse.length)
                        if pulse.type != PulseType.Readout else ""
                    )
                )

                if pulse.iq_frequency not in [0, None]:
                    text += "\n\n f_iq = {:.0f} MHz".format(
                        pulse.iq_frequency / 1e6)
                    if pulse.phase != 0:
                        text += "\n phase = {:.0f} deg".format(
                            pulse.phase)

                # Make sure pulse colors are unique
                if not remaining_colors:
                    remaining_colors = self._color_palette[:]
                    print("All colors already in use...\n Resetting color palette.")
                if pulse.type in self._pulse_cols.keys():
                    # Pulse type is special and has predefined color
                    col = self._pulse_cols[pulse.type]
                elif pulse.name in pulse_colors.keys():
                    # Pulse was in sequence before, take same color again
                    col = pulse_colors[pulse.name]
                else:
                    col = remaining_colors[0]
                    pulse_colors[pulse.name] = col
                    remaining_colors = remaining_colors[1:]
                    

                ax.fill(
                    [i, i, i + 1, i + 1, i],
                    [amp, amp + 1, amp + 1, amp, amp],
                    color=col, alpha=0.3)
                ax.text(i + 0.5, amp + 0.5, text,
                        horizontalalignment="center", verticalalignment="center")

        # make sure plot looks nice and fits on the screen (max number of pulses before scaling down is 9)
        size = 2.*min(1., 9./(i + 1))
        fig.set_figheight(size * ampmax)
        fig.set_figwidth(size * i + 2.)
        ax.set_xlabel("pulse number")
        ax.set_xticks(np.arange(i + 1))
        plt.xlim(-0.05, )
        # hide y ticks
        ax.set_yticks([])
        # hide top and right spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        return

    def _pulselength_as_str(self, pulse_length):
        """
        Returns the pulse length as string.
        For variable time pulses this is the function code.

        Args:
            pulse_length: length of the pulse (float or function)
        """
        length = None
        if callable(pulse_length):
            fct_code = getsourcelines(pulse_length)[0][0]
            fct_start = fct_code.find(":") + 1
            # find last bracket
            fct_end = len(fct_code) - fct_code[::-1].find(")") - 1
            length = fct_code[fct_start: fct_end]
            fct_end = length.find(",")
            if fct_end is not -1:
                length = length[: fct_end]
        elif isinstance(pulse_length, float):
            length = str(pulse_length) + " s"
        if length is None:
            return ""
        return str(length).strip()
