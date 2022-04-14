def p():
    import time
    import os
    import subprocess
    import sys

    W = 0
    WLAN = 0

    try:
        while W == 0 or W == 10:
            W = W +1
            time.sleep(10)
            print(W)
            ip = "www.google.de"
            if os.system("ping -c 1 " + ip) == 0:
                print("IP ist erreichbar")
                WLAN = 1
            else:
                subprocess.call("/home/pi/recon.sh")
                print("wlan reconnected")
                WLAN = 0
            
            
            
    except KeyboardInterrupt:
        print("process terminated")
        sys.exit()
