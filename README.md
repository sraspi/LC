USS:
2021_12_13: 4GB-SD-Karte defekt, wiederholte Ausfälle des Pi wegen Schreib/Lesefehlern.
- 32GB-Karte mit rpi-imager erstellt(inkl ssh und WLAN Fritzbox Keller)
- git installiert, ssh installiert und über git clone.... alles von USS aus github geclont
- erster Schritt war dann git add --all, git commit -am "text", git push --all
- noip installiert, crontab Einträge aus cron.uss übernommen
- Ordner NAS und data erstellt
- pip3 istalliert
- smbus und smbus2 via pip3
- pip install RPi.bme280
- f�r Email: NICHT!!!(pip3 install numpy, pip3 uninstall numpy) sondern:sudo apt-get install python3-numpy
- NAS:sudo apt install samba cifs-utils
      mkdir ~/NAS
      /home/pi/NAS/                   nano ~/.smbcredentials
                                              username=sraspi
                                              password=StJ19raspbian
- etc/fstab erg�nzen: 
  //192.168.178.1/FRITZ.NAS/ /home/pi/NAS cifs credentials=/home/pi/.smbcredentials,vers=3.0,noserverino,uid=1000,gid=1000,x-systemd.automount,x-systemd.requires=network-online.target 0 0
- crontab erg�nzen:
- @reboot sleep 120 && mount -a

- USS läuft ab 13.12.2021
31.12.2021:
LS-Problem NAS-mount wenn Fritzbox aus-boot-Vorgang bleibt bei NAS-mount stehen, LC-launcher wird nicht ausgef�hrt, 2.1 jetzt local: Startzeit dennoch falsch>
beim booten 10 Sekunden Pause (�ber bootjobs.sh sleep 10)

01.01.2022 LC2.1.py verified
21.04.2022: WLAN-Probleme mit USB-Wifi: 
-Wifi autopower off- USBmax double- K4/K5 Verkabelung OK 21.04.2022
Loop1: grosse Schleife inkl. Baum
Loop2: kleine Schleife
Loop3: grosse Schleife exkl. Baum
