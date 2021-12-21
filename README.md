2021_12_13: 4GB-SD-Karte defekt, wiederholte Ausf√§lle des Pi wegen Schreib/Lesefehlern.
- 32GB-Karte mit rpi-imager erstellt(inkl ssh und WLAN Fritzbox Keller)
- git installiert, ssh installiert und √ºber git clone.... alles von USS aus github geclont
- erster Schritt war dann git add --all, git commit -am "text", git push --all
- noip installiert, crontab Eintr√§ge aus cron.uss √ºbernommen
- Ordner NAS und data erstellt
- pip3 istalliert
- smbus und smbus2 via pip3
- pip install RPi.bme280
- f¸r Email: NICHT!!!(pip3 install numpy, pip3 uninstall numpy) sondern:sudo apt-get install python3-numpy
- NAS:sudo apt install samba cifs-utils
      mkdir ~/NAS
      /home/pi/NAS/                   nano ~/.smbcredentials
                                              username=sraspi
                                              password=StJ19raspbian
- etc/fstab erg‰nzen: 
  //192.168.178.1/FRITZ.NAS/ /home/pi/NAS cifs credentials=/home/pi/.smbcredentials,vers=3.0,noserverino,uid=1000,gid=1000,x-systemd.automount,x-systemd.requires=network-online.target 0 0
- crontab erg‰nzen:
- @reboot sleep 120 && mount -a

- l√§uft ab 13.12.2021
