def mail12():                       #E-Mail an sraspi21@gmail.com:
  
    import urllib
    import smtplib, ssl
    import email
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    Inhalt = ("logfile.txt")
    Betreff = str("U_bat<12V")
    sender_email = "sraspi21@gmail.com"
    receiver_email = "sraspi21@gmail.com"
    password = "rwnqyynanebneqbj"
    #password = input("Type your password and press enter:")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = Betreff
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(Inhalt, "plain"))

    filename = "/home/pi/data/logfile.txt" # In same directory as script
       
    # Open PDF file in binary mode  
    with open(filename, "rb") as attachment:
        #Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)


            
        # Add header as key/value pair to attachment part
        part.add_header("Content-Disposition", "attachment; filename=logfile.txt",)
        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    print("U_bat<12V, no reboot, shutdown now sent")
  


