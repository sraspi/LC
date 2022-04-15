def p():
    #Bibliotheken einbinden 
    import time
    import sys
    import subprocess
    import os

    try:
        WLAN = 0
        W = 0
        while W < 10 and WLAN == 0:
            time.sleep(1)
            print(W)
            ip = "www.google.de"
            if os.system("ping -c 1 " + ip) == 0:
                print("IP ist erreichbar")
                WLAN = 1
            else:
                subprocess.call("/home/pi/LC/recon.sh")
                print("wlan reconnected")
                WLAN = 0
                W = W + 1
                  

 
        if WLAN == 0 and W > 8:
            print("not connected, wifi error, W:" + str(W))
           
        else:
            print("connected, go on!")
    
                    
    except KeyboardInterrupt:
        print("process terminated")
        sys.exit()
