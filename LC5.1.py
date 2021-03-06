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
from datetime import date
import calendar

import mail_lc_status
import mail_14
import mail_12
import mailstart


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




#ADS settings
values = [0]*4
channel = 0
GAIN = 1

#Listen fuer Einzel-ADS-Werte 
A0 = [0]*5
A1 = [0]*5
A2 = [0]*5
A3 = [0]*5
a = 0

# gerundeter Mittelwert aus 5 Messungen:
I_ges = 0
I_pi = 0
I_bat = 0
A2_mi = 0
U_bat = 0

Start= True
mov = True
Ub14 = True
U_min = True


def check_U12():
    if U_bat > 12 and U_min:
        print("U_bat>12V")
    else:
        print("U_bat<12V,")
        mail_12.mail12()
        time.sleep(20)
        #subprocess.call("/home/pi/LC/shutdown.sh")
        time.sleep(10)
       

def check_U14():
    global Ub14
    if GPIO.input(23) == GPIO.LOW:
        print("K2_LOW") 
        #Zustand K2 in LC.log schreiben
        
    if GPIO.input(23) == GPIO.HIGH:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        print("------------------U_bat> 13.75V !!!!------------------")
        print("K2_OFF(HIGH)")
        if Ub14:
            try:
                
                mail_14.mail14()
            except:
                ("Error by mail-sent")
            
            #Zustand K2 in LC.log schreiben + 1*Email
            try:
                fobj_out = open("/home/pi/NAS/LC.log",  "a" )
                fobj_out.write("\n" + "\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: "  + "--------U_bat>13.75V-----" + str(Ub14) + '\n' )
                fobj_out.close()
            except:
                fobj_out = open("/home/pi/data/LC.log",  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + "network ERROR!! --------U_bat>13.75V-----" + str(Ub14) + '\n' )
                fobj_out.close()
            Ub14 = False


time.sleep(60) #Service-Zeit vor Start des Programms!

try:
    try:
        mailstart.start()
    except:
        e = sys.exc_info()[1]
        print("Error: ", e)
        fobj_out = open("/home/pi/data/LC.log", "a" )
        fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + "mailstart failed" + str(e) + '\n' )
        fobj_out.close()
    try:
       
        
        subprocess.call("/home/pi/LC/mount.sh")
        print("mounted")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        f = open("/home/pi/NAS/LC.log", "a")
        f.write( '\n' + "mounted at: " + timestr)
        f.close() 
    except:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        f = open("/home/pi/data/LC.log", "a")
        f.write( '\n' + "NAS-mount-error: " + timestr)
        f.close() 
        print("NAS not mounted")
    
    try:                                     #Loop-Auswahl:
        curr_date = date.today()
        wd = (calendar.day_name[curr_date.weekday()]) 
        print(wd)
        l = open("/home/pi/NAS/loop.txt", "r")
        data = l.read()
        data = [int(i) for i in data]
        data = sum(data)
        l.close()
        print(data)
        if wd == "Tuesday" or wd == "Thursday":
            data = 2
        #if wd == "Friday":
            #data = 3
        
    except:
        e = sys.exc_info()[1]
        timestr = time.strftime("%Y%m%d_%H%M%S")
        f = open("/home/pi/data/LC.log", "a")
        f.write( '\n' + "Network-error, loop not changed, remains at 1, Error: " + str(e) + timestr)
        f.close()
        print("not mounted, Error: ", e)
        data = 1    # default loop
   
    if data == 1:
        print("--Loop1 GPIO9_grosse Schleife------")

        #mit GPIO9 auf grosse Schleife:
        GPIO.output(9, GPIO.LOW)          # K4_init
        GPIO.output(9, GPIO.HIGH)         # N_K4_ON_
        time.sleep(0.1)
        GPIO.output(9, GPIO.LOW)         # N_K4_OFF
        
        #mit GPIO11 Baum include:
        GPIO.output(11, GPIO.LOW)          # K4_init
        GPIO.output(11, GPIO.HIGH)         # N_K4_ON_
        time.sleep(0.1)
        GPIO.output(11, GPIO.LOW)         # N_K4_OFF

    if data == 2:
                        
        print("--Loop2 GPIO_10_kleine Schleife --")
        GPIO.output(10, GPIO.LOW)          # K4_init
        GPIO.output(10, GPIO.HIGH)         # K4_ON_gelb
        time.sleep(0.1)
        GPIO.output(10, GPIO.LOW)         # K4_OFF
        
    if data == 3:
        print("-----------------Loop3 grosse Schleife exkl. Baum-- --")

        #mit GPIO10 Baum exclude:
        GPIO.output(10, GPIO.LOW)          # K4_init
        GPIO.output(10, GPIO.HIGH)         # K4_ON_gelb
        time.sleep(0.1)
        GPIO.output(10, GPIO.LOW)         # K4_OFF

        #mit GPIO9 wieder auf grosse Schleife schalten
        GPIO.output(9, GPIO.LOW)          # K4_init
        GPIO.output(9, GPIO.HIGH)         # K4_ON_
        time.sleep(0.1)
        GPIO.output(9, GPIO.LOW)         # K4_OFF
        
        
    if data < 1 or data >3:
        print("-------------------------------------error-----------------------------")
    


except:
    e = sys.exc_info()[1]
    print("Error: ", e)
    fobj_out = open("/home/pi/data/LC.log", "a" )
    fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + "generel network Error: " + str(e) + '\n' )
    fobj_out.close()
    
    
check_U14()              #erste Kontrolle von K2

#K2 reset setzen:
print("K2 reset")
GPIO.output(15, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(15, GPIO.LOW)

check_U14()              #zweite Kontrolle von K2 nach reset
 
   
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
        A1[n] = -(adc.read_adc_difference(1, 1, 8))*0.000125*100/18*1000*1.02 #1: Channel 0_ge minus channel 3_rt (I_ges)
        A2[n] = -(adc.read_adc_difference(2, 1, 8))*0.000125*100/18*1000*1.02 #2: Channel 1_gn minus channel 3_rt (I_ges+I_bat)
        A3[n] = adc.read_adc(1, 1, )*0.000125*100/18
      

        
    I_bat = round(sum(A0)/5,1) #I_bat
    I_ges = round(sum(A1)/5,1) #I_ges
    I_pi = round((I_ges - I_bat),1)
    A2_mi = round(sum(A2)/5,1) # I_ges+I_bat
    U_bat = round(sum(A3)/5,2)
       
    
try:
    while True:
        if Start:
            Startzeit = time.time() #Versuchsstartzeit
            th = datetime.datetime.now()
            t1 = th.hour
            timestr = time.strftime("%Y%m%d_%H%M%S")
            try:
            
                f = open("/home/pi/NAS/LC.log", "a")
                f.write("\n" + "LC5.1.py started at: " + timestr + "  Loop: " + str(data))
                f.close()
            except:
                f = open("/home/pi/data/LC.log", "a")
                f.write("\n" + "network error, LC5.1.py started without NAS at: " + timestr + "  Loop: " + str(data))
                f.close()
                print("NAS not mounted, started LC5.1.py without NAS")
            Start = False
        try:
            ads()                                # ADS-Sensorwerte abfragen
        except:
            print("ADS-ERROR")

        #Bildschirmnausgabe und Datei schreiben:
        Endzeit = time.time()
        delta = (Endzeit - Startzeit)/60/60  # Zeit in Stunden seit Versuchsstart
        cpu = CPUTemperature()
        cput = float(cpu.temperature)
        Datum=time.strftime("%Y-%m-%d %H:%M:%S")
        print("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) +   ': ' + "             I_ges: "  + str(I_ges) + "        I_bat: " + str(I_bat) + "             I_pi "  + str(I_pi)   +  "             U_bat: "  + str(U_bat))
        try:
            fobj_out = open("/home/pi/data/logfile.txt", "a" )
            fobj_out.write(Datum + " , " + str(round(delta,3)) + " , "  +  str(I_ges) +  ' , ' + str(I_bat) + " , " + str(I_pi) + ' , ' + str(U_bat) + ' , ' + str(cput) + '\n' )
            fobj_out.close()
        except:
            print("nothing")
        time.sleep(6)
        th = datetime.datetime.now()
        t2 = th.hour
        
        if U_min:
            check_U12()     
            U_min = False   

        check_U14()
        time.sleep(102)

        if t2 == 20:
            
            th = datetime.datetime.now()
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
                fobj_out = open("/home/pi/NAS/LC.log",  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "--LC5.1 shutdown--" + '\n' )
                fobj_out.close()
            except:
                fobj_out = open("/home/pi/data/LC.log",  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "network ERROR!!--LC5.1 shutdown--" + '\n' )
                fobj_out.close()

            
            try:
                if t2 == 20 and mov:
                    Datum = time.strftime("%Y_%m_%d")
                    shutil.move("/home/pi/data/logfile.txt", "/home/pi/data/" + Datum + ".txt")
                    mov = False
                    
            except:
                fobj_out = open("/home/pi/data/LC.log",  "a" )
                fobj_out.write("\n" + time.strftime("%Y-%m-%d %H:%M:%S") + "     t: " + str(round(delta,3)) + "network ERROR, no file moving" + '\n' )
                fobj_out.close()

            try:
                mail_lc_status.lc_mail()
            except:
                print("status mail failed")
        
            
            time.sleep(20)
            subprocess.call("/home/pi/LC/shutdown.sh")
            print("\nBye")

    
    print("\nBye")
    time.sleep(0.1)
    GPIO.cleanup()
               

except KeyboardInterrupt:
    print("keyboardInterrupt")
    timestr = time.strftime("%Y%m%d_%H%M%S")
    d = open("/home/pi/data/logfile.txt", "a")
    d.write("KeyboardInterrupt at: " + timestr + "\n")
    d.close()
    GPIO.cleanup()
    print("\nBye")
    sys.exit()