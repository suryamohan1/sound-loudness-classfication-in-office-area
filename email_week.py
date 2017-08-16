# Code to send the data for the entire week via email
#!/usr/bin/env python
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys


#recipients = ['shub']
recipients = ['surya.mohan@wynk.in'] 
emaillist = [elem.strip().split(',') for elem in recipients]
msg = MIMEMultipart()
#msg['Subject'] = str(sys.argv[1])
msg['Subject'] = 'week sound log file'
msg['From'] = 'officeweb125@gmail.com'
msg['Reply-to'] = 'suryamohan567@gmail.com'
 
msg.preamble = 'Multipart massage.\n'
 
part = MIMEText("Hi, please find the attached file")
msg.attach(part)
 
part = MIMEApplication(open("/home/pi/Desktop/week_log.csv","rb").read())
part.add_header('Content-Disposition', 'attachment', filename='week_log.csv')
#part = MIMEApplication(open(str(sys.argv[1]),"rb").read())
#part.add_header('Content-Disposition', 'attachment', filename=str(sys.argv[1]))
msg.attach(part)
 

server = smtplib.SMTP("smtp.gmail.com:587")
server.ehlo()
server.starttls()
server.login("officeweb125@gmail.com", "office web")
 
server.sendmail(msg['From'], emaillist , msg.as_string())
f = open ("/home/pi/Desktop/week_log.csv",'w')
f.truncate()
f.close()
