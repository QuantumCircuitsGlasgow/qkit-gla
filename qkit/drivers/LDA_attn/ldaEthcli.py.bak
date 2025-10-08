''' 
    Python based CLI Application interface control for vaunix LDA devies
    JA 01/10/2021    Initial Verison oF CLI control Interface
    (c) 2020-2021 by Vaunix Technology Corporation, all rights reserved
'''
from ctypes import *
import ctypes
import os
import time
import sys, getopt
from time import sleep

class CLI_Vaunix_Attn:

    DEVICES=0

    def __init__(self, name="ldaApi", port=''):
        # print('Using ', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VNX_atten64.dll'))
        self.vnx = cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VNX_Eth_Attn64.dll'))
        if CLI_Vaunix_Attn.DEVICES == 0:
            self.vnx.fnLDA_Init()
        self.vnx.fnLDA_SetTestMode(False)   
        if port != '':
            # ip=port.encode('utf-8')

            x=self.check_deviceexists(port) 
            print("Device status", x, "#", CLI_Vaunix_Attn.DEVICES)
            CLI_Vaunix_Attn.DEVICES+=1
            #check if the device exists VERY IMPORTANT

        
    def check_deviceexists(self, devip):
        self.vnx.fnLDA_InitDevice(devip)
        return self.vnx.fnLDA_CheckDeviceReady(devip)
    

    

    def get_devices_number(self):
        return self.vnx.fnLDA_GetNumDevices()


    
    # Get Model Name
    def get_modelname(self, devip):
        self.data = ctypes.create_string_buffer(32)
        self.vnx.fnLDA_GetModelName(devip, ctypes.byref(self.data))
        return self.data.value

    # Ger Serial Number
    def get_serial_number(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetSerialNumber(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Software Version
    def get_swversion(self, devip):
        self.data = ctypes.create_string_buffer(32)
        self.vnx.fnLDA_GetSoftwareVersion(devip, ctypes.byref(self.data))
        return self.data.value

    # Get IP mode Static/DHCP
    def get_ipmode(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetIPMode(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Ip Address
    def get_ipaddress(self, devip):
        self.data = ctypes.create_string_buffer(32)
        self.vnx.fnLDA_GetIPAddress(devip, ctypes.byref(self.data))
        return self.data.value
        
    # Get subnet mask
    def get_subnetmask(self, devip):
        self.data = ctypes.create_string_buffer(32)
        self.vnx.fnLDA_GetNetmask(devip, ctypes.byref(self.data))
        return self.data.value

    # Get gateway
    def get_gateway(self, devip):
        self.data = ctypes.create_string_buffer(32)
        self.vnx.fnLDA_GetGateway(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Min.Frequency
    def get_minfrequency(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetMinWorkingFrequency(devip, ctypes.byref(self.data))
        return (self.data.value/10)

    # Get Max. Frequency
    def get_maxfrequency(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetMaxWorkingFrequency(devip, ctypes.byref(self.data))
        return (self.data.value/10)

    # Get Min. Attenuation
    def get_minattenuation(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetMinAttenuation(devip, ctypes.byref(self.data))
        return (self.data.value/20.0)

    # Get Max. Attenuation
    def get_maxattenuation(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetMaxAttenuation(devip, ctypes.byref(self.data))
        return (self.data.value/20.0)

    # Get Channel #
    def get_currentchannel(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetChannel(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Current Frequency
    def get_currentfrequency(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetWorkingFrequency(devip, ctypes.byref(self.data))
        return (self.data.value/10)

    # Get Current Attenuation
    def get_currentattenuation(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetAttenuation(devip, ctypes.byref(self.data))
        return (self.data.value/20.0)

    # Get Ramp Start
    def get_rampstart(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetRampStart(devip, ctypes.byref(self.data))
        return (self.data.value/20.0)
        
    # Get Ramp End
    def get_rampend(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetRampEnd(devip, ctypes.byref(self.data))
        return (self.data.value/20.0)
        
    # Get Dwell time
    def get_dwelltime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetDwellTime(devip, ctypes.byref(self.data))
        return self.data.value

    # Get bi-directional ramp dwelltime
    def get_bidirectional_dwelltime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetDwellTimeTwo(devip, ctypes.byref(self.data))
        return self.data.value
        
    # Get Idle time
    def get_idletime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetIdleTime(devip, ctypes.byref(self.data))
        return self.data.value
        
    # Get hold time
    def get_holdtime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetHoldTime(devip, ctypes.byref(self.data))
        return self.data.value

    # Get profile count
    def get_profilecount(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetProfileCount(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Profile Max length
    def get_profilemaxlength(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetProfileMaxLength(devip, ctypes.byref(self.data))
        return self.data.value

    # Get Profile Dwell time
    def get_profiledwelltime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetProfileDwellTime(devip, ctypes.byref(self.data))
        return self.data.value        

    # Get Profile Idle time
    def get_profileidletime(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetProfileIdleTime(devip, ctypes.byref(self.data))
        return self.data.value
        
    # Get Profile Index
    def get_profileindex(self, devip):
        self.data= ctypes.c_int(0) # create c-var
        self.vnx.fnLDA_GetProfileIndex(devip,  ctypes.byref(self.data))
        return self.data.value
    
    def close_device(self, devip):
        try :
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return "Device Connection Terminated"
    
    # Set Attenuation
    def set_attenuation(self, devip, attenuation):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetAttenuation(devip, int(attenuation)*20)
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set Frequency
    def set_frequency(self, devip, frequency):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetWorkingFrequency(devip, int(frequency)*10)
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set Channel
    def set_channel(self, devip, channel):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetChannel(devip, int(channel))
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set Ramp Start
    def set_rampstartattenuation(self, devip, attenuation):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetRampStart(devip, int(attenuation)*20)
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set Ramp End
    def set_rampendattenuation(self, devip, attenuation):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetRampEnd(devip, int(attenuation)*20)
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set dwell time
    def set_dwelltime(self, devip, dwelltime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetDwellTime(devip, int(dwelltime))
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
        
    # Set idle time
    def set_idletime(self, devip, idletime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetIdleTime(devip, int(idletime))
            # self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set bidirectional dwell time
    def set_bidirectionaldwelltime(self, devip, dwelltime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetDwellTimeTwo(devip, int(dwelltime))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
       
    # Set hold time
    def set_holdtime(self, devip, holdtime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetHoldTime(devip, int(holdtime))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True


    # Set Ramp direction  -- True: Upwards, False: Downwards
    def set_rampdirection(self, devip, rampdirection):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetRampDirection(devip, int(rampdirection))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set bidirectional Ramp direction  -- True: Bi-directional, False: Uni-directional
    def set_rampbidirectional(self, devip, rampdirection):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetRampBidirectional(devip, int(rampdirection))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
       
    # Set Rampmode -- True - Continuous, False - Once
    def set_rampmode(self, devip, rampmode):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetRampMode(devip, int(rampmode))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
        
    # Set profile element data
    def set_profilelements(self, devip, profileindex, profiledata): 
        try:
            self.vnx.fnLDA_InitDevice(devip)
#            print('profiledata:%r', int(profiledata)*10)
            self.vnx.fnLDA_SetProfileElement(devip, int(profileindex), int(profiledata)*2)
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
        
    # Set profile count
    def set_profilecount(self, devip, profilelen):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetProfileCount(devip, int(profilelen))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True       

    # Set profile Idletime
    def set_profileidletime(self, devip, idletime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetProfileIdleTime(devip, int(idletime))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True     

    # Set profile Dwell time
    def set_profiledwelltime(self, devip, dwelltime):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SetProfileDwellTime(devip, int(dwelltime))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Set profile mode  0 - Off, 1 - Profile Once, 2 - Repeat 
    def set_profilemode(self, devip, profilemode):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_StartProfile(devip, int(profilemode))
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True
        
    def set_savesettings(self,devip):
        try:
            self.vnx.fnLDA_InitDevice(devip)
            self.vnx.fnLDA_SaveSettings(devip)
            self.vnx.fnLDA_CloseDevice(devip)
        except:
            print("An exception occurred")
        return True

    # Main Function call   
    def main(argv):
        ipaddress = ''
        attenuation = ''
        frequency = ''
        attobj = CLI_Vaunix_Attn()
        try:
            opts, args = getopt.getopt(argv,"hi:a:f:c:s:e:w:d:o:b:D:M:B:C:I:W:O:S:F:r",["iipaddr=","aattn=","ffreq=", "cchnl=", "srmst=", "ermed=", "wdwtm=", "didtm=", "ohdtm=", "bdwtm=", "Drmdi=", "Bbimd=", "Mrmmd=", "Cprct=", "Iprit=", "Wprdt=", "Oprmd=", "Svst=", "Fprel="
            ])
        except getopt.GetoptError as err:
            print(err)
            print ('ldacli.py argument error')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print ('ldacli.py -i <ipaddress> -a <attenuation> -f <frequency> -c <channel> -s <rampstart> -e <rampend> -w <dwelltime> -d < idletime> -o <holdtime> -b <bidirectional-dwelltime> -D <rampdirection[0-Up,1-Down]> -M <rampmode[0-Once,1-Continuous,2-Off]> -B <rampbidirectional[0-Unidirectional,1-Bidirectional]> -C <profilecount> -I <profileidletime> -W <profiledwelltime>  -O <profilemode[0-Off,1-Once,2-Repeat]> -S <savesetting> -F <profilefile> -r <read>')
                sys.exit()
            elif opt in ("-i", "--iipaddr"):
                ipaddress = arg.encode('utf-8')
                print ('Ip Address:', ipaddress )
            
            # Set Attenuation
            elif opt in ("-a", "--aattn"):
                attenuation = arg
                print ('Attenuation:', attenuation)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_attenuation(ctypes.c_char_p(ipaddress), attenuation)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set Frequency
            elif opt in ("-f", "--ffreq"):
                frequency = arg
                print ('frequency:', frequency)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_frequency(ctypes.c_char_p(ipaddress), frequency)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")                    

            # Set Channel
            elif opt in ("-c", "--cchnl"):
                channel = arg
                print ('channel:', channel)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_channel(ctypes.c_char_p(ipaddress), channel)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")  
                    
            # Set Rampstart
            elif opt in ("-s", "--srmst"):
                rampstart = arg
                print ('rampstart:', rampstart)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_rampstartattenuation(ctypes.c_char_p(ipaddress), rampstart)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set RampEnd
            elif opt in ("-e", "--ermed"):
                rampend = arg
                print ('rampend:', rampend)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_rampendattenuation(ctypes.c_char_p(ipaddress), rampend)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set Dwell time
            elif opt in ("-w", "--wdwtm"):
                dwelltime = arg
                print ('dwelltime:', dwelltime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_dwelltime(ctypes.c_char_p(ipaddress), dwelltime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set Idle time
            elif opt in ("-d", "--didtm"):
                idletime = arg
                print ('idletime:', idletime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_idletime(ctypes.c_char_p(ipaddress), idletime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set hold time
            elif opt in ("-o", "--ohdtm"):
                holdtime = arg
                print ('holdtime:', holdtime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_holdtime(ctypes.c_char_p(ipaddress), holdtime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set bi-directional dwell time
            elif opt in ("-b", "--bdwtm"):
                bddwelltime = arg
                print ('bddwelltime:', bddwelltime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_bidirectionaldwelltime(ctypes.c_char_p(ipaddress), bddwelltime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!") 

            # Set ramp direction
            elif opt in ("-D", "--Drmdi"):
                rmpdir = arg
                print ('ramp direction:', rmpdir)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_rampdirection(ctypes.c_char_p(ipaddress), rmpdir)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set ramp bi-direction
            elif opt in ("-B", "--Bbimd"):
                rmpdir = arg
                print ('ramp bi-direction:', rmpdir)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_rampbidirectional(ctypes.c_char_p(ipaddress), rmpdir)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")
                    
            # Set ramp mode
            elif opt in ("-M", "--Mrmmd"):
                rmpmode = arg
                print ('ramp mode:', rmpmode)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_rampmode(ctypes.c_char_p(ipaddress), rmpmode)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set Profile count
            elif opt in ("-C", "--Cprct"):
                profilecount = arg
                print ('profile count:', profilecount)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_profilecount(ctypes.c_char_p(ipaddress), profilecount)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set Profile idletime
            elif opt in ("-I", "--Iprit"):
                profileidletime = arg
                print ('profile idle-time:', profileidletime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_profileidletime(ctypes.c_char_p(ipaddress), profileidletime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set Profile dwelltime
            elif opt in ("-W", "--Wprdt"):
                profiledwelltime = arg
                print ('profile dwell-time:', profiledwelltime)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_profiledwelltime(ctypes.c_char_p(ipaddress), profiledwelltime)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set Profile mode
            elif opt in ("-O", "--Oprmd"):
                profilemode = arg
                print ('profile mode:', profilemode)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_profilemode(ctypes.c_char_p(ipaddress), profilemode)
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")

            # Set savesettings
            elif opt in ("-S", "--Svst"):
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        attobj.set_savesettings(ctypes.c_char_p(ipaddress))
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")
          
            # Set Profile File
            elif opt in ("-F", "--Fprel"):
                profilefilename = arg
                print ('profile Filename:', profilefilename)
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        profilefile = open(profilefilename, 'r')
                        count = 0
                        dwelltime = 0
                        idletime = 0
                        profilelength = 0
                        profileindex=0
                        for linedata in profilefile.readlines():
                            if "dwell=" in linedata:
                                dwelltime = linedata.split("dwell=",1)[1] 
                                attobj.set_profiledwelltime(ctypes.c_char_p(ipaddress), int(float(dwelltime)*1000))
                            elif "idle=" in linedata:
                                idletime = linedata.split("idle=",1)[1]
                                attobj.set_profileidletime(ctypes.c_char_p(ipaddress), int(float(idletime)*1000))
                            elif "length=" in linedata:
                                profilelength = linedata.split("length=",1)[1]
                                attobj.set_profilecount(ctypes.c_char_p(ipaddress), int(profilelength))
                            else:
#                                print("Line{}: {}".format(profileindex, linedata.strip()))
#                                print('profiledata-1:%r',int(float(linedata.strip())))
                                attobj.set_profilelements(ctypes.c_char_p(ipaddress), profileindex, int(float(linedata.strip())*10))
                                profileindex = profileindex + 1
                                sleep(0.05) # delay 50mec
                            
                        print("Reading File Done")
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print ("Device IP missing.. Please Check!")
                    
            elif opt in ("-r", "--rdata"):
                if(ipaddress !=''):
                    if not attobj.check_deviceexists(ctypes.c_char_p(ipaddress)):
                        print("*****************Current Information of the device**********")     
                        print("Model Name:",attobj.get_modelname(ctypes.c_char_p(ipaddress)))
                        print("Serial #:",attobj.get_serial_number(ctypes.c_char_p(ipaddress)))
                        print("SW Version:",attobj.get_swversion(ctypes.c_char_p(ipaddress)))
                        print("IP Mode:",attobj.get_ipmode(ctypes.c_char_p(ipaddress)))
                        print("IP Address:",attobj.get_ipaddress(ctypes.c_char_p(ipaddress)))
                        print("Subnet Mask:",attobj.get_subnetmask(ctypes.c_char_p(ipaddress)))
                        print("Gateway:",attobj.get_gateway(ctypes.c_char_p(ipaddress)))
                        print("Min Frequency(MHz):",attobj.get_minfrequency(ctypes.c_char_p(ipaddress)))
                        print("Max Frequency(MHz):",attobj.get_maxfrequency(ctypes.c_char_p(ipaddress)))
                        print("Min Attenuation(dB):",attobj.get_minattenuation(ctypes.c_char_p(ipaddress)))
                        print("Max Attenuation(dB):",attobj.get_maxattenuation(ctypes.c_char_p(ipaddress)))
                        print("Channel #:",attobj.get_currentchannel(ctypes.c_char_p(ipaddress)))
                        print("Frequency(MHz):",attobj.get_currentfrequency(ctypes.c_char_p(ipaddress)))
                        print("Attenuation(dB):",attobj.get_currentattenuation(ctypes.c_char_p(ipaddress)))
                        print("Ramp Start Attn(dB):",attobj.get_rampstart(ctypes.c_char_p(ipaddress)))
                        print("Ramp End Attn(dB):",attobj.get_rampend(ctypes.c_char_p(ipaddress)))
                        print("Dwell Time(ms):",attobj.get_dwelltime(ctypes.c_char_p(ipaddress)))
                        print("Idle Time(ms):",attobj.get_idletime(ctypes.c_char_p(ipaddress)))
                        print("Hold Time:",attobj.get_holdtime(ctypes.c_char_p(ipaddress)))
                        print("Bi-directional Dwell Time:",attobj.get_bidirectional_dwelltime(ctypes.c_char_p(ipaddress)))
                        print("Profile Count:",attobj.get_profilecount(ctypes.c_char_p(ipaddress)))
                        print("Profile Maxlength:",attobj.get_profilemaxlength(ctypes.c_char_p(ipaddress)))
                        print("Profile dwelltime(ms):",attobj.get_profiledwelltime(ctypes.c_char_p(ipaddress)))
                        print("Profile idletime(ms):",attobj.get_profileidletime(ctypes.c_char_p(ipaddress)))
                        print("Profile index:",attobj.get_profileindex(ctypes.c_char_p(ipaddress)))
                    else:
                        print ("Device not exists.. Please Check!")
                else:
                    print("Device IP missing.. Please Check!")
                

if __name__ == '__main__':
    CLI_Vaunix_Attn.main(sys.argv[1:])
    
