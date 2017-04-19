import numpy as np
import serial
import visa
import time


m1=[]
m3=[]
m5=[]

print"This program finds the zero error associated with the Keithley 2701"

a=serial.Serial(0)
k=visa.instrument("TCPIP::169.254.198.115::1394::SOCKET")
visa.VI_ATTR_TCPIP_KEEPALIVE

k.term_chars='\n'

print k.ask("*IDN?\n")
k.write("*RST")
k.write("SENS:FUNC 'VOLT:DC'")
k.write("SENS:VOLT:DC:DIG 7")
k.write("SENS:VOLT:DC:NPLC 2")
k.write("SYST:AZER:STAT ON")
k.write("SENS:VOLT:DC:AVER:WIND 1")                            #remove commented lines to set filter window
k.write("SENS:VOLT:DC:AVER:COUN 10")
k.write("SENS:VOLT:DC:AVER:TCON MOV")
k.write("SENS:VOLT:DC:AVER:STAT ON")

k.write("DISP:TEXT:STAT ON")
k.write("DISP:TEXT:DATA 'ZERO ERROR'")

k.write("ROUT:CLOS (@101)")
k.write("TRAC:CLE")
k.write("INIT:CONT OFF")                                        #channel settings: clears buffer, triggers immediately and sets the number of scan to 1
k.write("TRIG:SOUR IMM")
k.write("SAMP:COUN 1")
k.write("ROUT:SCAN (@101)")
k.write("ROUT:SCAN:TSO IMM")

for i in range(10):
        
    k.write("ROUT:SCAN:LSEL INT")                           
    m1.append(k.ask("READ?\n"))
    time.sleep(2)
        
k.write("ROUT:SCAN:LSEL NONE")
k.write("ROUT:OPEN:ALL")
m3.append(m1)



for i in range(1):
    
    for j in range(10):
        m4=[]
        m4=m3[i][j].split(',')
        m5.extend(m4)

m6=[]
for i in range(30):
        if(i%3==0):
            m6.append(m5[i])
            



m7=[]
for i in range(10):
    m7.extend(m6[i].split('V'))




m8=[]

for i in range(20):
    if(i%2==0):
        m8.append(m7[i])

m8=np.array(m8)
mfinal=m8.astype(float)
mfinal=np.array(mfinal)

k.write("DISP:TEXT:STAT OFF")

print"\n The emfs of the shorted circuit are:\n",mfinal
temp=abs(mfinal)
zeroerr=temp.mean()
zerostor=zeroerr.astype(str)

print"\n\nThe zero error associated with this instrument is : ",zeroerr

out_file= open("zero_error.txt","w")
out_file.write("The zero error is: " + zerostor)
out_file.close()


