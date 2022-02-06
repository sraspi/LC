from __future__ import unicode_literals
import urllib
import smtplib, ssl
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import os
import shutil

import mail_lc_status
import mail_14

# Import the ADS1115 module.
# Create an ADS1115 ADC (16-bit) instance.
from ADS1x15 import ADS1115
adc = ADS1115()

#GPIO_setup
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

GPIO.setup(15, GPIO.OUT)                      #K2_OFF ueber 6,8k 10_gn
GPIO.setup(18, GPIO.OUT)                      #K2_OUT_Check 12_bl
GPIO.setup(23, GPIO.IN, GPIO.PUD_DOWN)        #K2_status_16_gn

GPIO.output(15, GPIO.LOW)                     #K2_init_LOW
GPIO.output(18, GPIO.HIGH)                    #K2_OUT_init

mail_14.mail14()


#Check if U_bat > 14V:
if GPIO.input(23) == GPIO.LOW:
    print("LOW")
if GPIO.input(23) == GPIO.HIGH:
    print("------------------U_bat> 14V !!!!------------------")

    #Zustand K2 in LC.log schreiben
    try:
        fobj_out = open(name_log,  "a" )
        fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "--------U_>14,8V-----" + '\n' )
        fobj_out.close()
    except:
        fobj_out = open("/home/pi/data/LC.log",  "a" )
        fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "network ERROR!! --------U_>14,8V-----" + '\n' )
        fobj_out.close()

    
#K2 wieder auf HIGH setzen:
GPIO.output(15, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(15, GPIO.LOW)


#ADS settings
values = [0]*4
channel = 0
GAIN = 1

#Listen fuer Einzel-ADS-Werte 
A0 = [0]*5
A1 = [0]*5
A2 = [0]*5
A3 = [0]*5

# gerundeter Mittelwert aus 5 Messungen:
I_ges = 0
I_pi = 0
I_bat = 0
A2_mi = 0
U_bat = 0

Start= True
mov = True

time.sleep(1)
 
   
def ads(): # Read all the ADC channel values in a list.
    # Read the difference between channel 0 and 1 (i.e. channel 0 minus channel 1).
    # Note you can change the differential value to the following:
    #  - 0 = Channel 0 minus channel 1
    #  - 1 = Channel 0 minus channel 3
    #  - 2 = Channel 1 minus channel 3
    #  - 3 = Channel 2 minus channel 3

    global I_bat
    global I_ges
    global I_pi
    global A2_mi
    global U_bat
    
    for n in range(5):   #  Mittelwerte aus n Werten
        # Read the specified ADC channel using the previously set gain value.
        A0[n] = (adc.read_adc_difference(0, 1, 8))*0.000125*100/18*1000*1.03 # 0: Channel 0_ge minus channel 1_gn (I_bat)
        A1[n] = -(adc.read_adc_difference(1, 1, 8)-6)*0.000125*100/18*1000*1.02 #1: Channel 0_ge minus channel 3_rt (I_ges)
        A2[n] = -(adc.read_adc_difference(2, 1, 8)-6)*0.000125*100/18*1000*1.02 #2: Channel 1_gn minus channel 3_rt (I_ges+I_bat)
        A3[n] = adc.read_adc(1, 1, )*0.000125*100/18
      

        
    I_bat = round(sum(A0)/5,1) #I_bat
    I_ges = round(sum(A1)/5,1) #I_ges
    I_pi = round((I_ges - I_bat),1)
    A2_mi = round(sum(A2)/5,1) # I_ges+I_bat
    U_bat = round(sum(A3)/5,2)
    



try:
    try:
        name_log = "/home/pi/NAS/LC.log"
        subprocess.call("/home/pi/LC/mount.sh")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        f = open(name_log, "a")
        f.write( '\n' + "mounted at: " + timestr)
        f.close()
    except:
        e = sys.exc_info()[1]
        print("Error: ", e)
        name_log = "/home/pi/data/LC.log"
        fobj_out = open(name_log, "a" )
        fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + " Error: " + str(e) + '\n' )
        fobj_out.close()

    while True:
        if Start:
            
            Dateiname = "/home/pi/data/logfile.txt"
            Startzeit = time.time() #Versuchsstartzeit
            th = datetime.datetime.now()
            t1 = th.hour
            timestr = time.strftime("%Y%m%d_%H%M%S")
            f = open(name_log, "a")
            f.write( '\n' + "LC3.0.py started at: " + timestr)
            f.close()
            Start = False
        ads()                                # ADS-Sensorwerte abfragen

        #Bildschirmnausgabe und Datei schreiben:
        Endzeit = time.time()
        delta = (Endzeit - Startzeit)/60/60  # Zeit in Stunden seit Versuchsstart
        cpu = CPUTemperature()
        cput = float(cpu.temperature)
        Datum=time.strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) +   ': ' + "             I_ges: "  + str(I_ges) + "        I_bat: " + str(I_bat) + "             I_pi "  + str(I_pi)   +  "             U_bat: "  + str(U_bat))
        fobj_out = open(Dateiname,"a" )
        fobj_out.write(Datum + " , " + str(round(delta,3)) + " , "  +  str(I_ges) +  ' , ' + str(I_bat) + " , " + str(I_pi) + ' , ' + str(U_bat) + ' , ' + str(cput) + '\n' )
        fobj_out.close()
        time.sleep(10)
        th = datetime.datetime.now()
        t2 = th.hour
        
       
        t1 = t2
        if t2-t1 == 0:
            th = datetime.datetime.now()
            t2 = th.hour
            print("nothing to do")
        else:
            GPIO.output(20, GPIO.HIGH)          # T1_init
            GPIO.output(16, GPIO.LOW)           # T2_start & K2_ON 
            time.sleep(0.1)
            GPIO.output(16, GPIO.HIGH)          # T2_init
            print("T2_start & K2_ON & T2_init")
            GPIO.output(20, GPIO.LOW)           # T1_start
            time.sleep(0.2)
            GPIO.output(20, GPIO.HIGH)          # T1_init
            GPIO.output(27, GPIO.HIGH)          # K1_OFF
            time.sleep(0.1)                     
            GPIO.output(27, GPIO.LOW)           # K1_OFF_init
            
            try:
                fobj_out = open(name_log,  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "-3.0 shutdown-" + '\n' )
                fobj_out.close()
            except:
                fobj_out = open("/home/pi/data/LC.log",  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "network ERROR!!---3.0 shutdown---" + '\n' )
                fobj_out.close()

            
            if t2 == 18 and mov:
                Datum = time.strftime("%Y_%m_%d")
                shutil.move("/home/pi/data/logfile.txt", "/home/pi/data/" + Datum + ".txt")
                mov = False
                mail_lc_status.lc_mail()
        
            
            time.sleep(10)
            subprocess.call("/home/pi/LC/shutdown.sh")
            print("\nBye")

    
    print("\nBye")
    time.sleep(0.1)
    GPIO.cleanup()
               

except KeyboardInterrupt:
    print("keyboardInterrupt")
    timestr = time.strftime("%Y%m%d_%H%M%S")
    d = open(Dateiname, "a")
    d.write("KeyboardInterrupt at: " + timestr + "\n")
    d.close()
    GPIO.cleanup()
    print("\nBye")
    sys.exit()

