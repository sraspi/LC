def Uend(U_end):                       #E-Mail an sraspi21@gmail.com:
    try:  
        import urllib
        import smtplib, ssl
        import email
        import sys
        import time
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        Inhalt = ("U-End Gel-Accu vor dem Abschalten " ) 
        Betreff = ("LC finished, U_end: " +str(U_end) + " V")
        sender_email = "sraspi21@gmail.com"
        receiver_email = "sraspi21@gmail.com"
        password = "rwnqyynanebneqbj"
        #password = Inputs("Type your password and press enter:")

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = Betreff
        message["Bcc"] = receiver_email  # Recommended for mass emails

        
        message.attach(MIMEText(Inhalt, "plain"))
        text = message.as_string()

            # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        print("LC-status sent, U_end: " + str(U_end))
    
    except:
        e = sys.exc_info()[1]
        print("error", e)
        timestr = time.strftime("%Y%m%d_%H%M%S")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        f = open("/home/pi/data/LC.log", "a")
        f.write( '\n' + timestr + "LC-status-mail error:  " + str(e) + '\n')
        f.close() 
