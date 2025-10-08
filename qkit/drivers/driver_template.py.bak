    # qtLAB driver for microwave sources Anritsu MG37022, Anritsu MG3692C (*)
    # filename: Anritsu_MG37022.py
    # Pascal Macha <pascalmacha@googlemail.com>, 2010
    # Jochen Braumueller <jochen.braumueller@kit.edu> 2016

    # (*) phase offset functions not supported by Anritsu MG3692C

    #
    # This program is free software; you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation; either version 2 of the License, or
    # (at your option) any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program; if not, write to the Free Software
    # Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import qkit
from qkit.core.instrument_base import Instrument
from qkit import visa
import types
import logging
import math
from time import sleep

class Device_name(Instrument):
    '''
    This is the python driver for any generic device as a template for device drivers
    Note this uses SCPI commands, which are not always the same for different devices, so you will have to change them.
    Communication is through ETHERNET, GPIB, USB, or whatever you want to use but VISA takes care of that as VISA is the API for all of them .
    If the device uses a differnt API, a second template is provided using custom driver API. Check custom_driver_template.py.

    1. Copy this file to a new file with the name of your device.
    2. Change the class name to the name of your device.
    3. Add the parameters
    4. Add the do_get and do_set functions for each parameter
    5. Check for VISA version and use query or ask accordingly

    How this works :
    Each driver file uses the underlying backbone structure of the Instrument class. 
    Each parameter is a type of Instrument Attribute defined in the Instrument class. The parameter has get/set options. The Instrument class also has some custom aded funtions, which we can define from the driver class. These functions also have some properties, they are of get/set type and so on.

    - you create the parameter here, and define the get and set functions
    - this whole backbone is checked by conditions written in the Instrument class and then it becomes a foolproof working driver..


    Usage:
    Initialise with
    <name> = instruments.create('<name>', address='<GPIB address>')
    '''

    def __init__(self, name, address, model = 'Generic'):
        '''
        Initializes the Generic Driver, and communicates with the VISA wrapper.
        
        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            model : (string)
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address
        self._model = model
        self._visainstrument = visa.instrument(self._address) #this is the VISA wrapper that takes care of communicationq
        self._param3 = None   #set _param3 to True if frequency dependent power compensation is requested
        sleep(1)

        # Implement parameters
        self.add_parameter('parameter', type=float, flags=Instrument.FLAG_GETSET,  minval=0, maxval=20e9, maxstep=1e6, units='Hz',tags=['sweep']) #this is a parameter that can be set and get and swept over
               
        if ("MODEL1" not in self.ask("*IDN?").split(",")):
            self.add_parameter('param2', type=float, flags=Instrument.FLAG_GETSET,minval=-360, maxval=360, units='deg')

        
        self.add_parameter('param3', type=float, flags=Instrument.FLAG_GETSET, minval=0, maxval=100,units='dB@10GHz')
        
        self.add_parameter('status', type=bool,flags=Instrument.FLAG_GETSET)

        #-----------------------------------------------

        # Implement functions
        self.add_function('get_all') #this is a function that gets logged  as part of the instrument class and can be called from outside
        self.get_all()
        
    # initialization related
    def get_all(self):
        self.get_parameter()  # by default through the iunstrument class, this will be mapped to the do-get-parameter() function.
        self.get_param2()
        self.get_param3()

    #Communication with device
    def do_get_parameter(self):
        '''
        Get frequency of device

        Input:
            -

        Output:
            microwave frequency (Hz)
        '''
        # self._frequency = float(self.ask('SOUR:FREQ:CW?'))
        return self._frequency
        
    def do_set_parameter(self, parameter):
        '''
        Set frequency of device

        Input:
            freq (float) : Frequency in Hz

        Output:
            None
        '''
        #logging.debug(__name__ + ' : setting frequency to %s Hz' % (frequency*1.0e9))
        self.write('SOUR:FREQ:CW %i' % (int(parameter)))
        self._frequency = float(parameter)
        if(self._param3 != None): 
            self.do_set_param3()

#-------------------------------------------------------------------------
                    
    def do_get_param2(self):
        '''
        Get the RF output phase offset

        Input:
            -

        Output:
            phase offset (deg)
        '''
        # return float(self.ask('PHAS:ADJ?'))
        
    def do_set_param2(self, param2):
        '''
        Set the RF output phase offset and display phase offset

        Input:
            phase offset in degrees (-360.0 .. 360.0)

        Output:
            Nones
        '''
        # self.write('PHAS:ADJ %.1f DEG' %param2
        # self.write('PHAS:DISP ON')


#-------------------------------------------------------------------------
            
    def do_get_param3(self):
        '''
        Get attribute '_param3'

        Input:
            -

        Output:
            param3 applied to calculate power values
            None if no param3 is set
        '''
        return self._param3
        
    def do_set_param3(self, param3):
        '''
        Set param3 of output power to use at different frequencies.
        Assumes a cable attenuation of attn[dB] ~ attn(f0)*sqrt(f/f0), f0=10GHz

        Input:
            param3 (float) : param3 to apply to power values.
        '''
        self._param3 = param3
        
   
            
    def do_get_status(self):
        '''
        Get status of output channel

        Input:
            -

        Output:
            True (on) or False (off)
        '''
        # stat = bool(int(self.ask('OUTP:STAT?')))
        return stat
        
    def do_set_status(self,status):
        '''
        Set status of output channel

        Input:
            status : True or False

        Output:
            None
        '''
        # logging.debug(__name__ + ' : setting status to "%s"' % status)
        # # if status == True:
        #     self.write('OUTP:STAT ON')
        # elif status == False:
        #     self.write('OUTP:STAT OFF')
        # else:
        #     logging.error('set_status(): can only set True or False')     

            
    #shortcuts to make call to own functions easier
    def off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        self.set_status(False) 

    def on(self):
        '''
        Set status to 'on'

        Input:
            None

        Output:
            None
        '''
        self.set_status(True)
        

    #--------------VERSION SUPPORT-----------------------------------------------------------
    #sending customized messages
    def write(self,msg):
      return self._visainstrument.write(msg)
    
    if qkit.visa.qkit_visa_version == 1:
        def ask(self,msg):
            return self._visainstrument.ask(msg)
    else:
        def ask(self, msg):
            return self._visainstrument.query(msg)
