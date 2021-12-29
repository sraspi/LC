import sys
from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import os
import shutil

# Import the ADS1115 module.
# Create an ADS1115 ADC (16-bit) instance.
from ADS1x15 import ADS1115
adc = ADS1115()


#GPIO_setup:
GPIO.setmode(GPIO.BCM)
GPIO.setup(9, GPIO.OUT)        #V1_on
GPIO.setup(10, GPIO.OUT)       #V2_on
GPIO.setup(11, GPIO.OUT)       #V3_on
GPIO.setup(12, GPIO.OUT)       #V1_off
GPIO.setup(13, GPIO.OUT)       #V2_off
GPIO.setup(21, GPIO.OUT)       #V3_off

GPIO.setup(20, GPIO.OUT)       #T1_Start ueber LC
GPIO.setup(27, GPIO.OUT)       #K1_OFF ueber Transistor
GPIO.setup(16, GPIO.OUT)       #T2_in(Start)

GPIO.output(27, GPIO.LOW)      # K1_OFF ueber Transistor
GPIO.output(20, GPIO.HIGH)     # T1_init
GPIO.output(16, GPIO.HIGH)     # T2_init

#ADS settings:
values = [0]*4
channel = 0
GAIN = 1

#Listen fuer Einzel-ADS-Werte 
A0 = [0]*5
A1 = [0]*5
A2 = [0]*5
A3 = [0]*5

# gerundeter Mittelwert aus 5 Messungen:
A0_mi = 0
A1_mi = 0
A2_mi = 0
A3_mi = 0

NAS = True
mov = True

          
timestr = time.strftime("%Y%m%d_%H%M%S")
Dateiname = "/home/pi/LC/logfile.txt"
Startzeit = time.time() #Versuchsstartzeit
th = datetime.datetime.now()
t1 = th.hour
#header = ('\n' + "LC2.0.py started at: " + timestr + '\n' + "Zeit ,"  + "                t[h] , " +  "                                 CPU_temp, " + '\n')

   
def ads(): # Read all the ADC channel values in a list.
    global A0_mi
    global A1_mi
    global A2_mi
    global A3_mi
    for n in range(5):   #  Mittelwerte aus n Werten
        # Read the specified ADC channel using the previously set gain value.
        A0[n] = adc.read_adc(0, gain=GAIN)
        A1[n] = adc.read_adc(1, gain=GAIN)
        A2[n] = adc.read_adc(2, gain=GAIN)
        A3[n] = adc.read_adc(3, gain=GAIN)
        
    A0_mi=round(sum(A0)/5*0.000125,4)
    A1_mi=round(sum(A1)/5*0.000125,4)
    A2_mi=round(sum(A2)/5*0.000125,4)
    A3_mi=round(sum(A3)/5*0.000125,4)


try:
    
    while True:
        #Bildschirmnausgabe und Datei schreiben:
        Endzeit = time.time()
        delta = (Endzeit - Startzeit)/60/60  # Zeit in Stunden seit Versuchsstart
        cpu = CPUTemperature()
        cput = float(cpu.temperature)
        Datum=time.strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) +   ': ' + "             A0: "  + str(A0_mi) + "        A1: " + str(A1_mi) + "             A2 "  + str(A2_mi)   +  "             A3 "  + str(A3_mi))
        
        fobj_out = open(Dateiname,"a" )
        fobj_out.write(Datum + " , " + str(round(delta,3)) + " , "  +  str(A0_mi) +  ' , ' + str(A1_mi) + " , " + str(A2_mi) + ' , ' + str(A3_mi) + ' , ' + str(cput) + '\n' )
        fobj_out.close()
        time.sleep(10)
        th = datetime.datetime.now()
        t2 = th.hour
        
        if t2-t1 == 0:
            th = datetime.datetime.now()
            t2 = th.hour
            
        else:
           
            
            if t2 == 0 and mov:
                Datum = time.strftime("%Y_%m_%d")
                print("new day: move logfile.txt to NAC/LC")
                shutil.move("/home/pi/LC/logfile.txt", "/home/pi/NAS/LC/" + Datum + ".txt")
                mov = False

          
            

except KeyboardInterrupt:
    print("keyboardInterrupt")
    timestr = time.strftime("%Y%m%d_%H%M%S")
    d = open(Dateiname, "a")
    d.write("KeyboardInterrupt at: " + timestr + "\n")
    d.close()
    GPIO.cleanup()
    print("\nBye")
   
    sys.exit()

except:
    e = sys.exc_info()[1]
    print(e)
    fobj_out = open("/home/pi/NAS/LC.log", "a" )
    fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + str(e) + '\n' )
    fobj_out.close()
    print("ERROR")
    e = sys.exc_info()[1]
    print(e)
    GPIO.cleanup()
    sys.exit()



    

