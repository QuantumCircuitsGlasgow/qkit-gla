
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import logging
import os


class Resonator:

    '''
    Theretical Resonator class holds a resonator model information
    Ideally complex S21/S11 data

    1. either store measured data and fit it, will update the fitparams 
        i. calculates the model params
        ii. Calculates SNR
        iii. Photon number

    2. or generate the model with some preset parameters
        i. set the desired parameters
        ii. generate the model will update the Sij based on the parameters



    Attributes:
    1. fr: float -> Resonance frequency
    1a. _fr: float ->frequency Range
    2. Ql: float -> Loaded/External Q
    3. Qc: float -> Coupling Q
    4. Qi: float -> Internal Q
    5. Sij: [complexIQ]/(amplitude,phase) -> Sij data ; either for a single power or multiple power levels
    6. Pow: float -> Power level
    7. Temp: float -> Temperature
    8. photon: float -> Number of photons/ corresponding and calculated from power level 

    Methods :
    1. __init__ : Constructor

    2. generate(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters

    3. generate_mw_model(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters using scipy.mw

    4. save(filename) : Save the model to a file using pandas

    5. plot() : Plot the model

    6. load(filename) : Load the model from a file using pandas


    Note: # powers < the freqeuncy span of the resonator
    either 1D or 2D Sij data

    '''

#GLOBAL VARS



    # def __init__(self):
    #     #Object Vars
    #     self.fr=0.0
    

    def generate(self,power, start_f=4.5e9, stop_f=5.5e9,fano_b=1.0e6):
        '''
        Generate the resonator model from the given parameters of the specific power level, using the fitparams.
        Update the fitparams before generate()
        and this updates the Sij and f based on the fitparams

        - does not care about the power level
        - depends on the SNR can add noise using add_noise(), but generates a very ideal model
        '''
        if self._generate==False and self.validate():
            

            freqs=np.linspace(start_f,stop_f,self._nop)
                # the Sij will be same size of the frequency span
            self.f=freqs
            if self._fr < stop_f and self._fr > start_f:
                fr=self._fr
            else:
                logging.warning("Resonance frequency not in the frequency span. Please check the frequency range, resetting to mid")
                self._fr=(start_f+stop_f)/2
                fr=self._fr

            #check params
            params=self._fitparams
            
            pre_factor=params['a'] * np.exp(1j*params['alpha']) # A*exp(i*alpha)
            enviroment_factor=np.exp(2j*freqs*np.pi*params['delay']) # exp(2j*pi*f*delay)

            ideal_resonator=params['Ql']/np.abs(params['Qc'])*np.exp(1j*params['phi'])

            ideal_resonator=1-(ideal_resonator/(1+2j*params['Ql']*(freqs-fr)/fr))
            sij=pre_factor*enviroment_factor*ideal_resonator


            #updates the Sij
            self.sij=(np.abs(sij),np.angle(sij))
            self.f=freqs
            self._generate=True
            return sij
        else:
            logging.warning("Model already generated. Please use validate to update the model")
            self.validate()
            return self.sij

        

    def generate_mw_model(self,nop=5000, start_f=4.5e9, stop_f=5.5e9,fr=5.0e9,fano_b=1.0e6):

        '''
        Generate the resonator model from the given parameters using scipy.mw
        '''
        #TODO : Implement the function
        pass

    def save(self,filename)->None:
        '''
        Save the model to a file using pandas
        '''
        #TODO : improve the saving format
        # pd.DataFrame.from_dict(self.__dict__).to_csv(str(filename))
        # return None


    def add_noise(self,SNR:float=None,to='both')->None:
        '''
        Add noise to the model,
        Scales the SNR / a
        or sigma = a x r / SNR


        '''
        #TODO : Implement the function
        if SNR is None:
            SNR=self.SNR
        rng=np.random.default_rng()
        sigma=self.fitparams['a']*self.fitparams['r']/SNR #taken from the SNR in the model.
        # ~ actual radius is scaled by a, so the noise should be scaled by a

        noise=rng.normal(0,sigma,np.size(self.sij))
        noise2=rng.normal(0,sigma,np.size(self.sij))
        
        self.fitparams.update({'sigma':sigma})

     
        amp,pha=np.abs(self.sij),np.angle(self.sij)
        if to=='amp':
            self.sij=self.amp_pha2complex(amp+noise,pha)
        elif to=='phase':
            self.sij=self.amp_pha2complex(amp,pha+noise)
        elif to=='both':
            self.sij=self.amp_pha2complex(amp+noise/2,pha)
            amp,pha=np.abs(self.sij),np.angle(self.sij)
            self.sij=self.amp_pha2complex(amp,pha+noise2/2)
      
        return None
    
    def get_SNR(self,sij=None)->float:
        '''
        Calculate the SNR of the model
        '''
        r0=self.fitparams['r'] # either from the fit or the model   
        a=self.fitparams['a'] # either from the fit or the model
        alpha=self.fitparams['alpha'] # either from the fit or the model
        phi=self.fitparams['phi'] # either from the fit or the model
        beta=alpha+phi # either from the fit or the model

        C=a*( np.exp(1j*alpha) - r0*np.exp(1j*beta)) # get the center of the circle
        if sij is None:
            sij=self.sij
        print(np.real(C),np.imag(C))
        ri=np.abs(sij-C) # get the diff of the points from the center
        sigma=np.std(ri-r0) # get the standard deviation of the diff

          
        return r0/sigma,np.std(ri),sigma




    def amp_pha2complex(self,amp,pha)->np.ndarray:
        '''
        Convert amplitude and phase to complex
        '''
        #TODO : Implement the function
        return np.array(np.multiply(amp,np.cos(pha))+(1j*np.multiply(amp,np.sin(pha))),dtype='complex')
    

    def validate(self)->bool:
        '''
        Validate the model, before every generate
        - validates the parameters changed to generate again; need to call before generate
        - not needed for the fit
        '''
        self._generate=False

        if self._fitparams['Ql']!=np.abs(self.Ql):
            logging.warning("Loaded Q cannot be different. Please check the parameters")
            self.Ql=self._fitparams['Ql']
        
        if self._fitparams['Qc']!=np.abs(self.Qc):
            logging.warning("Coupling Q cannot be different. Please check the parameters")
            self.Qc=self._fitparams['Qc']
        
        # if self._fitparams['Qi']!=np.abs(self.Qi):
        #     logging.warning("Internal Q cannot be different. Please check the parameters")
            self.Qi=1/((1/self.Ql)-(1/self.Qc))
            self._fitparams['Qi']=self._Qi

        if self._fitparams['r']<0 or self._fitparams['r'] != self.Ql/2/np.abs(self.Qc):
            logging.warning("Radius or sigma cannot be negative. Please check the parameters")
            self._fitparams['r']=self.Ql/2/np.abs(self.Qc)

        if self._fitparams['sigma']<0 or self._fitparams['sigma'] != self.Ql/np.abs(self.Qc)/self.SNR/2:
            logging.warning("Noise level cannot be negative. Please check the parameters")
            self._fitparams['sigma']=self.Ql/np.abs(self.Qc)/self.SNR/2
    
    
        if self._fitparams['alpha'] + self._fitparams['phi'] != np.mod(np.pi-self._fitparams['theta'],2*np.pi):
            logging.warning("Impedance mismatch should be the sum of alpha and phi. Please check the parameters")
            self._fitparams['theta']=np.pi-(self._fitparams['alpha'] + self._fitparams['phi'])
    
    
    
    
        return True
    

        
    def get_canonical(self)->np.ndarray:
        '''
        Get the canonical form of the data
        '''
        #TODO : Implement the function
        return self.sij/self.fitparams['a']/np.exp(1j*self.fitparams['alpha'])





    def plot(self):
        '''
        Plot the model
        '''
        #TODO : Implement the  phase plot

        real = self.sij.real
        imag = self.sij.imag
        real2 = self.z_data_sim.real
        imag2 = self.z_data_sim.imag
        real_norm=self.z_data_norm.real
        imag_norm=self.z_data_norm.imag

        fig,axs=plt.subplots(2, 2,gridspec_kw={'width_ratios': [1,1],'height_ratios': [1,1]},figsize=(8,7))
        axs[0,0].axvline(0, c="k", ls="--", lw=1)
        axs[0,0].axhline(0, c="k", ls="--", lw=1)
        axs[0,0].plot(real,imag,label='rawdata')
        axs[0,0].plot(real2,imag2,label='fit')
        axs[0,0].set_aspect("equal",adjustable='datalim')
        axs[0,0].set_xlabel('Re(S21)',fontsize = 12)
        axs[0,0].set_ylabel('Im(S21)',fontsize = 12)
        axs[0,0].legend()

        imag_cannonical=imag-self.offrespoint.imag
        axs[0,1].set_aspect("equal",adjustable='datalim')
        axs[0,1].axvline(0, c="k", ls="--", lw=1)
        axs[0,1].axhline(0, c="k", ls="--", lw=1)
        axs[0,1].scatter(real,imag_cannonical,label='raw_canonical',s=3,color='b')
        axs[0,1].scatter(real_norm,imag_norm,label='norm-data',s=2,color='r')
        axs[0,1].set_xlabel('Re(S21)',fontsize = 12)
        axs[0,1].set_ylabel('Im(S21)',fontsize = 12)
        axs[0,1].legend(loc=1)


        axs[1,0].plot(self.f_data*1e-9,np.absolute(self.z_data_raw),label='rawdata')
        axs[1,0].plot(self.f_data*1e-9,np.absolute(self.z_data_sim),label='fit')
        axs[1,0].set_xlabel('f (GHz)',fontsize = 12)
        axs[1,0].set_ylabel('|S21|',fontsize = 12)
        axs[1,0].legend()

        axs[1,1].plot(self.f_data*1e-9,np.angle(self.z_data_raw),label='rawdata')
        axs[1,1].plot(self.f_data*1e-9,np.angle(self.z_data_sim),label='fit')
        axs[1,1].set_xlabel('f (GHz)',fontsize = 12)
        axs[1,1].set_ylabel('arg(|S21|)',fontsize = 12)
        axs[1,1].legend()

        fig.tight_layout()
        plt.show()

    def load(self,filename):
        '''
        Load the model from a file using pandas
        '''
        #TODO : Implement the function
        pass



    @property
    def sij(self):
        return self._sij
    
    @sij.setter
    def sij(self,s):
        '''
        Sij should be a list or a tuple
        if tuple, it should be a tuple of two lists (amplitude,phase)
        amplitude in form of [[pow1],[pow2],[pow3]...] <-> [powers , freqs] : each col is a power level from h5 file
        '''
        #TUPLE
        if (isinstance(s,(tuple,list)) and len(s) ==2)| (isinstance(s[0],list) and np.size(s)==2): #2D

            if np.shape(s[0][0]) == np.shape(s[1][0]) and np.shape(s[0][1]) == np.shape(s[1][1]):
                amps= np.array(s[0][:])
                phas= np.array(s[1][:])
                self._sij=np.array(np.multiply(amps,np.cos(phas))+(1j*np.multiply(amps,np.sin(phas))),dtype='complex')

            else :
                self._sij=None
                raise ValueError("Amplitude and Phase should be of same size")
        
        #LIST 
        elif isinstance(s,(list,np.ndarray)): #1D

            if np.ndim(s)>=1:
                self._sij=np.array(np.reshape(s,-1),dtype='complex')
 
        else:
            self._sij=None
            raise ValueError("Sij should be a list or a tuple")

    @property
    def f(self):
        return self._f
    
    @f.setter
    def f(self,f):
        if np.size(f)!=np.max(np.shape(self._sij)):
            # logging.warning("Frequency should be of same size as Sij")
            self._f=np.arange(np.max(np.shape(self._sij)))
        elif np.size(f)>=1: 
            if (isinstance(f,list) or isinstance(f,np.ndarray)) :
                self._f=f

        else:
            # logging.warning("Frequency should be a list")
            self._f=None
            # raise ValueError("Frequency should be a list/numpy array")
            


    @property
    def fr(self):
        return self._fr


    @fr.setter
    def fr(self, f):
        # if isinstance(self.fr, (np.ndarray, list)):
        #     if isinstance(f, (np.ndarray, list)):
        #         if np.size(f) < self._powers:
        #             self._fr[:np.size(f)] = f
        #         else:
        #             self._fr = f[:self._powers]
        #     elif isinstance(f, tuple):  # scalar #PASS INDEX AS TUPLE
        #         fval, idx = f
        #         self._fr[idx] = fval
        #     else:
        #         self._fr[-1] = f
        # else:  # scalar
        #     if isinstance(f, (np.ndarray, list)):
        #         f = f[0]
        self._fr = f
        if f<np.min(self._f) or f>np.max(self._f):
            logging.warning("Resonance frequency not in the frequency span. Please check the frequency range.")
            self._fr=(np.min(self._f)+np.max(self._f))/2
            self._fr=f



    @property
    def Qi(self):
        return self._Qi

    @Qi.setter
    def Qi(self, q):
        # if isinstance(self.Qi, (np.ndarray, list)):
        #     if isinstance(q, (np.ndarray, list)):
        #         if np.size(q) < self._powers:
        #             self._Qi[:np.size(q)] = q
        #         else:
        #             self._Qi = q[:self._powers]
        #     elif isinstance(q, tuple):  # scalar #PASS INDEX AS TUPLE
        #         qval, idx = q
        #         self._Qi[idx] = qval
        #     else:
        #         self._Qi[-1] = q
        # else:  # scalar
        #     if isinstance(q, (np.ndarray, list)):
        #         q = q[0]
        # self._Qi =float(q)
        self._Qi=1/((1/self.Ql)-(1/self.Qc))
        logging.warning("Qi should not be set directly. It should be calculated from the Ql and Qc")


    @property
    def Ql(self):
        return self._Ql

    @Ql.setter
    def Ql(self, q):

            self._Ql = float(np.abs(q))

    # @property
    # def Qc(self):
    #     Qci = np.divide(np.ones(self._powers), self._Ql) - np.divide(np.ones(self._powers), self._Qi)
    #     return np.divide(np.ones(self._powers), Qci)
    @property
    def Qc(self):
        return self._Qc

    @Qc.setter
    def Qc(self, q):
        # if isinstance(self.Qc, (np.ndarray, list)):
        #     if isinstance(q, (np.ndarray, list)):
        #         if np.size(q) < self._powers:
        #             self._Qc[:np.size(q)] = q
        #         else:
        #             self._Qc = q[:self._powers]
        #     elif isinstance(q, tuple):  # scalar #PASS INDEX AS TUPLE
        #         qval, idx = q
        #         self._Qc[idx] = qval
        #     else:
        #         self._Qc[-1] = q
        # else:  # scalar
        #     if isinstance(q, (np.ndarray, list)):
        #         q = q[0]
            self._Qc = float(np.abs(q))



    # @property #no setter
    # def Qc(self):
    #     Qci= np.divide(np.ones(self._powers),self._Ql)-  np.divide(np.ones(self._powers),self._Qi)
    #     return np.divide(np.ones(self._powers),Qci)
    


    @property
    def temp(self):
        return str(self._temp)
    
    @temp.setter
    def temp(self,t):
        self._temp=t

    @property
    def pow(self):
        return self._pow

    @pow.setter
    def pow(self,p):

        self._pow=int(p) # single value
        # if isinstance(p,(list,np.ndarray)) and  np.ndim(self._sij)==1:
        #     self._pow=[p[0]] # first element of the list
        #     self._powers=1
        # elif isinstance(p,(list,np.ndarray))  and  np.ndim(self._sij)==2 and (np.size(p)!=np.min(np.shape(self._sij))):
        #     self._pow=p[:np.min(np.shape(self._sij))]
        #     self._powers=np.size(self._pow)

        # else:
        #     logging.warning("Power should be a list or a numpy array")
        #     self._pow=[p,] # TODO : fix this; for now taking the first element of the list
        #     self._powers=1

    @property
    def SNR(self):
        return self._SNR
    
    @SNR.setter
    def SNR(self,snr):
        self._SNR=np.abs(snr)

        
    @property
    def fitparams(self):
        return self._fitparams
    
    @fitparams.setter
    def fitparams(self,params,power=0):

        # if isinstance(params,dict) and isinstance(power,(list,np.ndarray)):
        if isinstance(params,dict) :
            # for p in power:
            # idx=self._pow.index(p)
            # self._fitparams['a'][idx]=params['a'][idx]
            # self._fitparams['alpha'][idx]=params['alpha'][idx]
            # self._fitparams['phi'][idx]=params['phi'][idx]
            # self._fitparams['theta'][idx]=params['theta'][idx]
            # self._fitparams['Qc'][idx]=params['Qc'][idx]
            # self._fitparams['Qi'][idx]=params['Qi'][idx]
            # self._fitparams['Ql'][idx]=params['Ql'][idx]
            # self._fitparams['fr'][idx]=params['fr'][idx]
            # self._fitparams['delay'][idx]=params['delay'][idx]
            # self._fitparams['Qi_absqc'][idx]=params['Qi_absqc'][idx]
            # self._fitparams['Qi_absqc_err'][idx]=params['Qi_absqc_err'][idx]
            # # refactor this
            
            self._fitparams.update(params)

        else:
            logging.warning("Fitparams should be a dictionary")
            self._fitparams=None
    

    @property
    def BW(self):
        self._BW=self._f[-1]-self._f[0]
        return self._BW


    def __str__(self):
        return f"Resonator Model : \n fr : {self.fr} Hz \n Qi : {self.Qi} \n Ql : {self.Ql} \n Qc: {self.Qc} \n Temp : {self.temp} K \n Power : {self.pow} dBm\n"

    def __repr__(self):
        return f"Resonator Model : {type(self)} \n fr : {self._fr} Hz \n Qi : {self.Qi} \n Ql : {self.Ql} \n  Qc: {self.Qc} \n Temp : {self.temp} K \n Power : {self.pow} dBm \n"




    
    def __init__(self,Sij,f:list,fr:float=5.0e9 ,nop:int=1001,pow=0., Qi:float=1.0e6,Ql:float=1.0e6,Qc:float=50000,temp:float=26e-3)->None:
        # :
        # 1. ~compare and fix the size of Sij with Power~  # CANCELLED
        # 2. check Sij is complex or not # CANCELLED


        #TODO : update
        # 3. SINGLE POWER LEVEL resonator model


        # MODEL RESONAOTR, NO FITTING 
        # contains the generated model parameters
        self.sij=Sij# calls the setter to set the 
        self.f=f
        self.pow=pow

        # TODO : discard this. Try to use fitparams to store all the resonator model params
        self._fr=fr
        self._Qi=Qi # TODO : calculate from Ql and Qc
        self._Ql=Ql
        self._Qc=Qc


        # Calculated parameters
        self.SNR=100 # captures the r and sigma. This is updated during the fitting. Used for generating noise.
        # r is the radius self.Ql/np.abs(self._Qc) from the fit
        self._nop=nop
        self.temp=temp
        self.photon_number=0.0 # updated during the fitting and genration#TODO
        self._BW=0.0 # bandwidth update during generation and fitting
        self._fit=False # flag to check if the model is fitted or not
        self._generate=False # flag to check if the model is generated or not

        # Parameters to define the lorentzian model, this van be validated and updated during fit and generation
        # generate will read and update the Sij based on these parameters
        # validate checks the model and updates the parameters accordingly from the fit params
        # fit will update the parameters based on the Sij, so use another resonator object to store the fit

        self._fitparams={
            'a':5., # required for fitting
            'alpha':0.785,# required for fitting
            'phi':0.261,   # required for fitting
            'theta':0.785+0.261, # impedance mismatch , not needed for anything
            'Qc':self.Qc, # coupling Q
            'Qi':self.Qi,
            'Ql':self.Ql, # loaded Q
            'fr':self.fr, # resonance frequency required for fitting
            'delay':50e-9, # electrical delay
            'Qc_abs':np.abs(self._Qc), # required for fitting
            'Qi_absqc_err':0.,
            'r':self.Ql/2/np.abs(self.Qc), # radius of the circle
            'sigma':self.Ql/np.abs(self._Qc)/self.SNR, # noise level
        }


class PowerResonator(object):
    '''
    Power Resonator class holds a resonator model information
    Ideally complex S21/S11 data at different power levels
    Attributes:
    1. fr: float -> Resonance frequency
    1a. _fr: float ->frequency Range
    2. Ql: float -> Loaded/External Q
    3. Qc: float -> Coupling Q
    4. Qi: float -> Internal Q
    5. Sij: [complexIQ]/(amplitude,phase) -> Sij data ; either for a single power or multiple power levels
    6. Pow: float -> Power level
    7. Temp: float -> Temperature
    8. photon: float -> Number of photons/ corresponding and calculated from power level 

    Methods :
    1. __init__ : Constructor

    2. generate(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters

    3. generate_mw_model(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters using scipy.mw

    4. save(filename) : Save the model to a file using pandas

    5. plot() : Plot the model

    6. load(filename) : Load the model from a file using pandas


    Note: # powers < the freqeuncy span of the resonator
    either 1D or 2D Sij data

    '''

    def __init__(self,Sij,f:list,power=[0,],**kwargs):

        self.Rs=[]
        logging.info(f"Power Resonator Model : {type(self)} \n   powers : {power} dBm \n")
        if np.size(power)>=1:
                #  print(np.shape(Sij)[1])
                #  print(np.size(power))
                 if np.ndim(Sij)>1 :
                    if np.shape(Sij)[1]!=np.size(power):
                     
                     logging.warning(f'Size of Sij {np.shape(Sij)} should be same as the number of power levels')
                     raise ValueError("Size of Sij should be same as the number of power levels")
                    for i,p in enumerate(power):
                     # always send Sij as a complex array
                        self.Rs.append(Resonator(Sij[:,i],f,pow=p,nop=np.shape(Sij)[0],**kwargs))

                 else:
                        self.Rs.append(Resonator(Sij,f,pow=power,nop=np.shape(Sij)[0],**kwargs))
                         # TODO :
        # 1. compare and fix the size of Sij with Power
        # 2. check Sij is complex or not
 
        # self.sij=Sij# calls the setter
        # self.f=f
        # self.power=power
        # self.delay=kwargs.get('delay',50e-9)
        # self.temp=kwargs.get('temp',26e-3)
        # self._fit=False
        self._pow=power # list of power levels
        self._powers=np.size(power)
        self.ResonatorDF=pd.DataFrame()



#-------------------TESTING-------------------#

if __name__ ==  "__main__":
    s=[[1+1.1j,3.2j],[1.1+7j,3.6j],[1.7+1j,3.2j]]
    s2=[[1+1.1j,3.2j],[1.1+7j,3.6j]]
    f=[3,4,5]
    r1=Resonator((np.abs(s),np.angle(s)),[1,2,3],[6e9,4e5,6e5,7e5],pow=[20,23,24],Qi=[2e6,3.4e6],Ql= [1e5,1e4])
    r2=Resonator(s,[1,2,3],[6e9,4e5,6e5,7e5],pow=[20,23,24],Qi=[2e6,3.4e6],Ql= [1e5,1e4])

    print(r1)
    print(r2)
    # print(r1.sij)
    r1.plot()
    # print(type(r1.Ql))
