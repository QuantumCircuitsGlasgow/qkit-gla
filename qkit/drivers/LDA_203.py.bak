# qtLAB driver for microwave Attenuator LDA_203 (*)
# filename: LDA_203.py
# Wridhdhisom Karar <w.karar.1@research.gla.ac.uk >, 2023
# Quantum  Circuits Group, University of Glasgow  <eng-weideslab@glasgow.ac.uk>  

# (*) ramping functions not implemented in this driver

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
from qkit.drivers.LDA_attn.ldaEthcli import CLI_Vaunix_Attn #imports from the relative folder
import types
import logging
import math
import ctypes
from time import sleep


class LDA_203(Instrument): 
#inherit from Instrument class but we can use the functions of the driver helper
    '''
    Usage:
        Initialise with
        <name> = instruments.create('<name>', type='LDA_203' ,address='<IP address>' )

        then call the functions below with


    '''
    def __init__(self, name, address,model='LDA_203', **kwargs):
        '''
        Initialises the Attenuator and connects to the IP and checks
        if the IP is valid and the device is connected

        Input:
            name (string)    : name of the instrument , 'control Attn'
            address (string) : IP address of the device
            model (string)   : model of the device , should be the same as type

        '''
        logging.info(__name__ + ' : Initializing instrument LDA_203')
        Instrument.__init__(self, name, tags=['physical'])

        #local class variables DEVIOCE SPECIFIC and CONSTAants
        # changeable variables are the parameters of the attenuator MODEL SPECIFIC
        
      

        self._address = address.encode('utf-8') #convert to bytes
        ATTN=CLI_Vaunix_Attn()

        DEVICE_STATUS=ATTN.check_deviceexists(self._address)
        if DEVICE_STATUS== 0:  #VERY IMPORTANT else the other functions will throw an error 
            print (f"Device found at {self._address} \n Initializing the device dll")
            self._instrument= CLI_Vaunix_Attn(port=self._address) #connect to the device
        else:
            print (f"Device not found at {self._address} . Check the IP address")
            return


        #connect to the device
        self._model = self._instrument.get_modelname(self._address) #get the model name
        self._serialNumber = self._instrument.get_serial_number(self._address) #get the serial number
        self._swVersion = self._instrument.get_swversion(self._address) #get the software version
        IPMODE=self._instrument.get_ipmode(self._address) #get the ip mode
        SUBNETMASK=self._instrument.get_subnetmask(self._address) #get the ip mode
        GATEWAY=self._instrument.get_gateway(self._address) #get the ip mode

        self._ip = {'ipMode': IPMODE,'ipAdress':self._address ,'subnet':SUBNETMASK ,'GATEWAY':GATEWAY}  #get the ip mode
        self._MIN_FREQ = self._instrument.get_minfrequency(self._address) #get the min frequency
        self._MAX_FREQ =self._instrument.get_maxfrequency(self._address) #get the max frequency 
        self._MIN_ATT = self._instrument.get_minattenuation(self._address) #get the min attenuation
        self._MAX_ATT = self._instrument.get_maxattenuation(self._address) #get the max attenuation

        self.add_parameter('channel', type=bool,flags=Instrument.FLAG_GETSET)

        self.add_parameter('frequency', type=float,flags=Instrument.FLAG_GETSET,minval=self._MIN_FREQ,maxval=self._MAX_FREQ,units='MHz')
                           
        self.add_parameter('attenuation', type=float,flags=Instrument.FLAG_GETSET,minval=self._MIN_ATT,maxval=self._MAX_ATT,units='dB',tags=['sweep'])


        self.add_function('get_all') #must implement else will throw error  



    def get_all(self):
        self.get_channel()
        self.get_frequency()
        self.get_attenuation()

        

        #Start defining the functons
    def do_get_channel(self):
        '''
        Gets the channel number of the attenuator
        '''
        return self._instrument.get_currentchannel(self._address)
    
    def do_set_channel(self,channel):
        '''
        Sets the channel number of the attenuator
        '''
        self._instrument.set_channel(self._address,channel)
        return self._instrument.get_currentchannel(self._address)
    

    def do_get_frequency(self): 
        '''
        Gets the frequency of the attenuator and set it within bounds ,that should be done automatically by the minval/maxval options
        '''
        return self._instrument.get_currentfrequency(self._address)
    
    def do_set_frequency(self,freq):
        '''
        Sets the frequency of the attenuator and set it within bounds ,that should be done automatically by the minval/maxval options
        '''
        self._instrument.set_frequency(self._address,freq)
        return self._instrument.get_currentfrequency(self._address)
    
    def do_get_attenuation(self):

        '''
        Gets the attenuation of the attenuator and set it within bounds ,that should be done automatically by the minval/maxval options
        '''
        return self._instrument.get_currentattenuation(self._address)
    
    def do_set_attenuation(self,att):   
        '''
        Sets the attenuation of the attenuator and set it within bounds ,that should be done automatically by the minval/maxval options
        '''
        self._instrument.set_attenuation(self._address,att)
        return self._instrument.get_currentattenuation(self._address)
    

    def do_get_all(self):
        '''
        Gets all the parameters of the attenuator
        '''
        return self._instrument.get_all(self._address)
    
    #---------------------------SHORTCUTS----------------------------------

    def attn(self,att):
        '''
        Shortcut for setting the attenuation
        '''
        self.do_set_attenuation(att)





    #---------------------------LOG details----------------------------
    def __str__(self):
        '''
        Overwrites the print function to print the name of the instrument
        '''
        return f"Model : {self._model} @ IP : {self._address} \n \
        Serial Number : {self._serialNumber} \n \
        Software Version : {self._swVersion} \n \
        IP Mode : {self._ip} \n \
        Min Frequency : {self._MIN_FREQ} \n \
        Max Frequency : {self._MAX_FREQ} \n \
        Min Attenuation : {self._MIN_ATT} \n \
        Max Attenuation : {self._MAX_ATT} \n "
        
    
#  The properties of the attenator , extracted from the manualApi and the dll file
'''
The properties of the attenator :

    Model Name:",attobj.get_modelname(ctypes.c_char_p(ipaddress)))
    Serial #:",attobj.get_serial_number(ctypes.c_char_p(ipaddress)))
    SW Version:",attobj.get_swversion(ctypes.c_char_p(ipaddress)))
    IP Mode:",attobj.get_ipmode(ctypes.c_char_p(ipaddress)))
    IP Address:",attobj.get_ipaddress(ctypes.c_char_p(ipaddress)))
    Subnet Mask:",attobj.get_subnetmask(ctypes.c_char_p(ipaddress)))
    Gateway:",attobj.get_gateway(ctypes.c_char_p(ipaddress)))
    Min Frequency(MHz):",attobj.get_minfrequency(ctypes.c_char_p(ipaddress)))
    Max Frequency(MHz):",attobj.get_maxfrequency(ctypes.c_char_p(ipaddress)))
    Min Attenuation(dB):",attobj.get_minattenuation(ctypes.c_char_p(ipaddress)))
    Max Attenuation(dB):",attobj.get_maxattenuation(ctypes.c_char_p(ipaddress)))
    Channel #:",attobj.get_currentchannel(ctypes.c_char_p(ipaddress)))
    Frequency(MHz):",attobj.get_currentfrequency(ctypes.c_char_p(ipaddress)))
    Attenuation(dB):",attobj.get_currentattenuation(ctypes.c_char_p(ipaddress)))
    
    #TODO later 
    Ramp Start Attn(dB):",attobj.get_rampstart(ctypes.c_char_p(ipaddress)))
    Ramp End Attn(dB):",attobj.get_rampend(ctypes.c_char_p(ipaddress)))
    Dwell Time(ms):",attobj.get_dwelltime(ctypes.c_char_p(ipaddress)))
    Idle Time(ms):",attobj.get_idletime(ctypes.c_char_p(ipaddress)))
    Hold Time:",attobj.get_holdtime(ctypes.c_char_p(ipaddress)))
    Bi-directional Dwell Time:",attobj.get_bidirectional_dwelltime(ctypes.c_char_p(ipaddress)))
    Profile Count:",attobj.get_profilecount(ctypes.c_char_p(ipaddress)))
    Profile Maxlength:",attobj.get_profilemaxlength(ctypes.c_char_p(ipaddress)))
    Profile dwelltime(ms):",attobj.get_profiledwelltime(ctypes.c_char_p(ipaddress)))
    Profile idletime(ms):",attobj.get_profileidletime(ctypes.c_char_p(ipaddress)))
    Profile index:",attobj.get_profileindex(ctypes.c_char_p(ipaddress)))
'''