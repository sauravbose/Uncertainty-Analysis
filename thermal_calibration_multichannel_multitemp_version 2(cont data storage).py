import numpy as np
from matplotlib import pyplot as plt
from scipy import optimize
import math
import pylab as pl
import visa
import serial
import time

a=serial.Serial(0)                                                      #to open serial port
k=visa.instrument("TCPIP::169.254.198.115::1394::SOCKET")
visa.VI_ATTR_TCPIP_KEEPALIVE                                        #define the instrument


new=open("zero_error.txt","r")                  #reads the zero error from the txt file
t=new.read()

t2=t.split(' ')


t3=t2[4]
t3=float(t3)

new.close()



zerr=t3

def steady(k):
    s1=[]
    k.write("ROUT:SCAN:LSEL INT")
    s1= k.ask("READ?\n")
    s1=s1.split(',')
    s1=s1[0]
    s1=s1.split('V')
    s1=s1[0]
    s1=float(s1)
    return s1

def steadycheck(k):                                             #Func to check steady state
    x=0
    while(x%2==0):
        c1=steady(k)
        print"check1\n",c1
        time.sleep(120)
        c2=steady(k)
        print"\ncheck2\n",c2
        if(((c2-c1)/c1)<0.05):
            print"\nSteady state reached"
            flag=1
            return flag
        else:
            time.sleep(120)
            x=x+2

        


def init_inst(k):                                                   #func initializing the instrument
 
    k.term_chars='\n'

    print k.ask("*IDN?\n")
    k.write("*RST")
    k.write("SENS:FUNC 'VOLT:DC'")
    k.write("SENS:VOLT:DC:DIG 7")
    k.write("SENS:VOLT:DC:NPLC 2")
    k.write("SENS:VOLT:DC:RANG:AUTO OFF")
    k.write("SENS:VOLT:DC:RANG 0.01")
    k.write("SYST:AZER:STAT ON")
    k.write("SENS:VOLT:DC:AVER:WIND 1")                            #remove commented lines to set filter window
    k.write("SENS:VOLT:DC:AVER:COUN 10")
    k.write("SENS:VOLT:DC:AVER:TCON REP")
    k.write("SENS:VOLT:DC:AVER:STAT ON")


init_inst(k)


print"Enter the number of reference temperatures"
numref=input()
numreftemp=0
mfinaltemp=[]

print"\n How many channels do you wish to scan?\n"
count=input()

print "Enter the number of readings in each set: "                  #input the number of readings in each set
num=input()

print "Press a key to start measurements."                     #press y as long as you want to continue taking readings
inp=raw_input()
m6=[]

while(numreftemp!=numref):                                          #loop for refence temperature

    k.write("DISP:TEXT:STAT ON")
    k.write("DISP:TEXT:DATA 'MEASURING'")                               #measurement process starts
    m3=[]

    
    tempcount=1
    #k.write("ROUT:SCAN (@101:10%i)"%count)
    
    rghcalib=open("rough_calib.txt","a")
    rghcalib.write("\nRef temp "+"%i\n"%(numreftemp+1))
    m8=[]
    while(tempcount!=count+1):                                      #loop for number of channels
        rghcalib.write("\nChannel %i\n"%tempcount)
        
        print"Please wait..."
        time.sleep(5)
        k.write("ROUT:CLOS (@10%i)"%tempcount)                                     #closes channel 101
    

        k.write("TRAC:CLE")
        k.write("INIT:CONT OFF")                                        #channel settings: clears buffer, triggers immediately and sets the number of scan to 1
        k.write("TRIG:SOUR IMM")
        k.write("SAMP:COUN 1")
        k.write("ROUT:SCAN (@10%i)"%tempcount)
        k.write("ROUT:SCAN:TSO IMM")

        #print"Waiting for steady state\n"
        #steadycheck(k)

        print "Scanning channel ",k.ask("ROUT:CLOS?\n")
        
        for i in range(num):                                            #loop for number of readings per channel per ref temp
            m1=[]
            k.write("ROUT:SCAN:LSEL INT")                           #loop scans channel 101 num number of times - num is the number of readings in each set.
            m1.append(k.ask("READ?\n"))
            time.sleep(2)
            
            mtemp=m1
            mtemp=str(mtemp)
            
            
            mtemp=mtemp.split(',')
                        
            mtemp=mtemp[0]
            
            mtemp=mtemp.split('\'')
            mtemp=mtemp[1]
                              
            mtemp=mtemp.split('V')
            
            mtemp=mtemp[0]

            
            mtemp=float(mtemp)
            mtemp=abs(mtemp)

            mtemp=mtemp-zerr
            
            m8.append(mtemp)
            mtemp=str(mtemp)
            
            rghcalib.write(mtemp+"\n")
            
        k.write("ROUT:SCAN:LSEL NONE")
        k.write("ROUT:OPEN:ALL")
        time.sleep(2)
           
    
        tempcount=tempcount+1
    m8=np.array(m8)
    mfinalref=m8.astype(float)
    mfinalref=np.array(mfinalref)

    mfinalref.resize(count,num)                                        #restructures the array of data into a 2D array with count rows and num columns - count is the number of sets.

    mfinaltemp.append(mfinalref)


    k.write("DISP:TEXT:STAT OFF")
   
    
   
    
    

    print"Measurement complete for current ref temp. Change the calibrator temp"
    #time.sleep(1200)                                                               #time to set calibrator temp and wait for stability
    print"Temp set. Proceding to measurement"

    numreftemp=numreftemp+1
    
rghcalib.close()

mfinaltemp=np.array(mfinaltemp)


mfinal=mfinaltemp


mfinal=np.array(mfinal)                                                     #These lines take care of the inherent zero error


    




cn = np.array([0.000000000000E+00,0.387481063640E-01,0.332922278800E-04,0.206182434040E-06,
              -0.218822568460E-08,0.109968809280E-10,-0.308157587720E-13,0.454791352900E-16,-0.275129016730E-19])


cni=np.array([0.000000E+00,2.592800E+01,-7.602961E-01])                                                             #NIST coefficients corresponding to T type thermocouple.


ttest=np.array([12.71,4.303,3.182,2.776,2.571,2.447,2.365,2.306,2.262,2.228,2.201,2.179,2.160,2.145,2.131,2.120,2.110,2.101,2.093,2.086,2.080,2.074,2.069,2.064,2.060,2.056,2.052,2.048,2.045,2.042])


a=0
b=0
c=0
choice=0


def ptruetemp(numref):                                                               #Allows user to enter the reference temp used
    Ttruef=[]
    for i in range(numref):
        print"Enter ref temp ",(i+1),"\n"
        a=input()
        Ttruef.append(a)
        
    
    print "The true temperatures are \n",Ttruef

    
    return Ttruef


def pmeasemf(mfinal,count):                                                     #measures the emf from the DMM and displays data in a formatted way. The for loop does the formatting
    
    k.write("DISP:TEXT:STAT ON")
    k.write("DISP:TEXT:DATA 'CHECK OUTPUT'")
    
    print "The measurements are:\n"
    for j in range(numref):
        print"Reference temperature ",j+1," : \n"
        for i in range (count):
            print"Channel %i: "%(i+1),mfinal[j][i],"\n"                                    #mfinal is the final array of data
    print"Please wait till prompted"
    time.sleep(5)                                                               #waits for 5s before you are allowed to proceed 
    
    k.write("DISP:TEXT:STAT OFF")
    k.write("*RST")                                                             #important to reset instrument after measurements are taken
    return mfinal
    

   


def mean(Emeastemp,count,num,numref):                                            #Calculates the mean of the measured emfs and the mean of the measured temperatures(temp corresponding to the measured emfs via NIST for now).
    Emean=[]
    
    print "The mean of measured emfs:\n"
    for k in range(numref):
        
        for i in range(0,count):
            esum=0
            for j in range(0,num):
                esum+=Emeastemp[k][i,j]
            emeanr=esum/num
            Emean.append(emeanr)
    Emean=np.array(Emean)
    Emean.resize(numref,count)
    print Emean
    print
    
    return Emean

def stdev(Emeastemp,count,num,numref):                                       #calculates the population and sample standard deviations of the emf data and corresponding temp data.
                                                                                    #Note that the analysis af the corresponding temp data becomes redundant when thermocouples are hooked up and must be replaced by
                                                                                    #true temp readings in order to successfully callibrate.
    
    sigmaEpop=[]
    
    
    print"Population standard deviation of emfs:\n"
    for k in range(numref):
        for i in range(0,count):
            e_stdpoptemp=Emeastemp[k][i].std()
            sigmaEpop.append(e_stdpoptemp)
    sigmaEpop=np.array(sigmaEpop)
    sigmaEpop.resize(numref,count)
    print sigmaEpop
    print
    print "Sample standard deviation of emfs:\n"
        
    sigmaEsamp=sigmaEpop*((num/9.0)**(1.0/2.0))
    print sigmaEsamp
    sigmaEsamp=np.array(sigmaEsamp)
      
    
    return sigmaEpop

def tdist(Emeastemp,sigmasamp,Emeantemp,count,num,ttest,numref):                                             #finds the standard deviation of the emf sample of data for 95% confidence
    
    err2=[]
    print "This program gives us the 95% confidence interval of finding the mean for :\n"

    for k in range(numref):
        
        den=sigmasamp[k]/((num)**(1.0/2.0))

   
        numb=ttest[num-2]*den*(-1)                                                                      #formula to find the uncertainity 
        lowerlimit=Emeantemp[k]+numb

        numb2=ttest[num-2]*den
        upperlimit=Emeantemp[k]+numb2
        err=[]
        print"For ref temp",(k+1)," :\n"
        for i in range(0,count):
            errset=[]
            errset.append(((upperlimit[i]-lowerlimit[i])/2.0))
            err.append(errset)
            print "The error in measurement of ",Emeantemp[k][i]," is ",errset
            print
        err2.append(err)
    err2=np.array(err2)
    err2.resize(numref,count)
    
    
    err4=[]
    
    for m in range(numref):
        err3=err2[m].mean()
        err4.append(err3)

    err4=np.array(err4)
    err5=err4.mean()
    print"The errors due to noise for the tested reference temperatures from the probability curve are :\n",err4
    
    
    return err5             
      
           
def scatterplot(Emeastemp,Ttruetemp,numref,count,num):                                                       #plots the measured emfs and the corresponding temperatures to get a polynomial relation p
                                                                                            #Note when thermocouples are hooked up, replace the measured temp with the known temp values for callibration
    Et=Emeastemp
    Tt=Ttruetemp
   
    
    x=Et.ravel()   
    x=np.array(x)
    
    k=count*num
    Ty=[]
    for i in range(k):
        Ty.append(Tt)
    Ty=np.array(Ty)
    Ty=Ty.T
    y=Ty.ravel()
               
    
    p=np.poly1d(np.polyfit(x,y,2))
    print"The polynomial is:\n",p
    pl.plot(x,y,'o')
    
    pl.xlabel("Measured Emfs")
    pl.ylabel("Reference Temperatures")
    plt.show()                                                                              #Must close the plot window to continue during execution
    
    return p,x,y

def avgstd(pol,sigmasamp,Em,num,Tm,count,numref):
    
    pred=[]
    p=pol
    astd=[]
    sigmas=sigmasamp
    sigmas=np.array(sigmas)
    for k in range(numref):
        
        astd1=sigmas[k].mean()
        astd.append(astd1)
    
    print "The errors due to noise for the tested reference temperatures from the data points are: \n",astd    #Average error due to noise

    for i in range((num*count*numref)):
        a=p(Em[i]) 
        pred.append(a)
        
    
    pred=np.array(pred)
    Tm=np.array(Tm)
    dev=pred-Tm
    
    print "The deviations from the curve are: \n",dev," \nand the max deviation is: ",dev.max()

    
    devs=dev**2
    
    deviation1=devs.sum()
    
    deviation2=deviation1/(num*count*numref)
   
    deviation=deviation2**(1.0/2.0)

    print"The deviation from the curve is: ",deviation                                                      #Average error from the curve fit
    return deviation


def guesstemp(pol,err_noise,err_curvefit):
    print"The error due to instrument noise is: ",err_noise,"\n\nThe error due to curve fit is: ",err_curvefit
    print "\nEnter the emf: "
    e=input()
    tot_uncertainity=((((err_noise**2)+(err_curvefit**2))/2)**(1.0/2.0))                                    #total uncertainity is the root mean of the error due to noise and the error from the curve
    t=pol(e)
    print "The temperature is ",t," and the uncertainity is ",tot_uncertainity                              #Uses the polynomial relation p to guess the temp for entered emf and gives the associated uncertainty corresponding to
                                                                                                            #noise and curve fit
    

        
def storecalib(count,num,Em,Tm,numref,Emeastemp,Ttruetemp):                                                              #Stores the calibration data into a txt file

    
    Tm=np.array(Tm)
    
    filarrfinal=[]
    
    tempnum=[]
    rdgnum=[]
    filarr=[]
    for k in range(numref):               
        
        n=count*num
        for i in range(count):
            for j in range(num):
                tempnum.append((i+1))
    tempnum=np.array(tempnum)                                                                               #defines the temperature number array
    

    for k in range(numref):
        for i in range(count):
            for j in range(num):
                rdgnum.append((j+1))
    rdgnum=np.array(rdgnum)         
    
    filarr.append(tempnum)
    filarr.append(rdgnum)
    filarr.append(Em)                                                                                #Adds the temp num , rdg num , measured emf,measured temp(to be replaced by true temp) to a single array
    filarr.append(Tm)
        
    filarr=np.array(filarr)
    filarr=filarr.T

    
    filarr2=[[' Channel num','    Reading num','      Emf','         Temp      ']]                          #Adds the headers to the final array to be stored in the txt file
    filarr2.append(filarr)
    filarr2=np.array(filarr2)
    print "The calibration data has been stored in a text file called calibdata.txt"

    np.savetxt('calibdata.txt',filarr2,fmt='%s')      
        

def menu():
    

    print "______________________________MENU__________________________________\n"
    print '''1. Print the measured emfs\n2. Print the reference temperatures\n3. Calculate the mean measured emf and measured temperature
4. Calculate the standard deviation of the measured emf \n5. t-distribution
6. View scatter plot of measurements\n7. Display standard deviation\n8. Guess temperature\n9. Store to file\n10. Quit'''
    print "_____________________________________________________________________\n"

menu()

while choice!=10:
    print "Enter your choice"
    choice = input()
    if choice == 1:
        
        Emeas=pmeasemf(mfinal,count)
        Emeastemp=Emeas

    elif choice == 2:
        Ttrue=ptruetemp(numref)
        Ttruetemp=Ttrue

    elif choice == 3:
        Emean=mean(Emeastemp,count,num,numref)
        Emeantemp=Emean
        
        
    elif choice == 4:
        
        sigmasamp=stdev(Emeastemp,count,num,numref)

    elif choice ==5:
        err_noise=tdist(Emeastemp,sigmasamp,Emeantemp,count,num,ttest,numref)
        
    elif choice ==6:
        pol,Em,Tm=scatterplot(Emeastemp,Ttruetemp,numref,count,num)
        

    elif choice == 7:
        err_curvefit=avgstd(pol,sigmasamp,Em,num,Tm,count,numref)

    elif choice == 8:
        guesstemp(pol,err_noise,err_curvefit)

    elif choice == 9:
        storecalib(count,num,Em,Tm,numref,Emeastemp,Ttruetemp)
