#This code records audio data using a microphone and processes that data in real time.
# taking the value from threshold from the database it makes the decision about if the audio sample is loud , normal or quiet.
# It also makes clusters of the data to be later clustered further using k means.

import sys;
from random import shuffle, uniform;
import csv
import pandas
import numpy
import pyaudio
import analyse
import wave
import RPi.GPIO as GPIO
import time
import math
import struct
import logging
import smtplib
import threading
import MySQLdb

#logging settings 1
logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
frmt =  logging.Formatter ('%(asctime)s,%(message)s')
fh1 = logging.FileHandler('/home/pi/Desktop/hour_log.csv')
fh1.setLevel(logging.INFO)
fh1.setFormatter(frmt)
logger.addHandler(fh1)

#logging settings 2
fh2 = logging.FileHandler('/home/pi/Desktop/week_log.csv', mode ='w')
fh2.setLevel(logging.INFO)
fh2.setFormatter(frmt)
logger.addHandler(fh2)

#email settings
def sendemail(subject, message):
    print 'mail sent {} {}'.format(subject, message)
    sendmail('wynkios@gmail.com',['surya.mohan@wynk.in'],[],subject,message,'wynkios','wynk@music')
    
def sendmail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems

#gpio settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT)

# Initialize PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 48000
RECORD_SECONDS = 6
WAVE_OUTPUT_FILENAME = "file1.wav"

location = 2

#high cuts off bass, low cuts off treble, together they form a bandpass filter.
highpass=9000
lowpass=100

###_Pre-Processing_###
def ReadData(fileName):
    #Read the file, splitting by lines
    f = open(fileName,'r');
    lines = f.read().splitlines()
    f.close()
    #print(type(lines))
    items = [];
    for i in range(1,len(lines)):
        line = lines[i].split(',');
        j=3;
        v = float(line[j]); #Convert feature value to float
        items.append(v);
    return items;

def my_min(sequence):
    """return the minimum element of sequence"""
    low = sequence[0] # need to start with some value
    for i in sequence:
        if i < low:
            low = i
    return low

def mean(nums):
    return sum(nums, 0.0) / len(nums)

def main():

    supercluster=[]
    meancluster = []
    mcluster= []
    cluster=[]
    sizecluster = []
    scluster = []
    mindiff=0
    maxdiff=0
    count1 = 0
    count2 = 0
    db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="office web",db="week")
    cursor = db.cursor()

    while True:
        #code for accessing the database to get the threshold fore that day and that hour slot:
        day = time.strftime("%A")
        current_hour = time.strftime("%H")
        #print (day)
        #print ( current_hour )
        if (day == 'Monday'):
            p = 0
        elif ( day == 'Tuesday'):
            p = 1
        elif ( day == 'Wednesday'):
            p = 2
        elif ( day == 'Thrusday'):
            p = 3
        elif ( day == 'Friday'):
            p = 4
        elif ( day == 'Saturday'):
            p = 5
        elif ( day == 'Sunday'):
            p = 6

        hour_number = 24 * p + int(current_hour)
        #print hour_number
        sql ="select thresh from thresh where hour = '%s'" % \
                (current_hour)  
        #print sql
        cursor.execute(sql)
        results  = cursor.fetchall()
        #print results
        for row in results:
            thresh_current = row[0]
            print "current threshold = %s" % \
                    (thresh_current)
            
        count = 0
        sum = 0
        avg = 0
        GPIO.setup(7, GPIO.OUT)
        GPIO.output(7, GPIO.LOW)
        try:
            # start Recording
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index =2,
                        frames_per_buffer=CHUNK)
        except RuntimeError:
            print "server failed error"
            subject = "microphone not working 0"
            message = "NEEDED Rebooting"
            t1 = threading.Thread(target=sendemail, args=(subject, message))
            t1.start()

        print "recording..."
        frames = []
        flag = 0
        effective_samples = 0

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):

            try:
                data = stream.read(CHUNK, exception_on_overflow = False)
                frames.append(data)
            except RuntimeError:
                print "server failed error"
                subject = "microphone not working 0"
                message = "NEEDED Rebooting"
                t2 = threading.Thread(target=sendemail, args=(subject, message))
                t2.start()

            count = count +1
            # changing the audio data to numpy array
            samps = numpy.fromstring(data, dtype=numpy.int16)

            # filtering the audio data
            lf= numpy.fft.rfft(samps)

            lf[:lowpass]= 0# low pass filter
            #lf[55:66]=0 # line noise
            lf[highpass:]=0 # high pass filter

            cs = numpy.fft.irfft(lf)

            # Getting the decibel value of the sound data to find the loudness
            print analyse.loudness(cs)
            x = analyse.loudness(cs)
            x = -x
            logger.info('location: %s, %s' % (location,x))

            # Deciding the output of the system using the threshold values
            if(x < thresh_current):
                count1+=1
                if(count1 >= 5):
                    print("LOUD")
                    count2 = 0

            if(x > thresh_current):
                count2+=1
                if(count2 >= 3):
                    print("Quiet")
                    count1 = 0

            # clustering of data
            if(i == 0):
                pivot = x
                
            if (x>=pivot):
                diff = x-pivot
                if(diff > maxdiff):
                    maxdiff = diff
            elif (x<pivot):
                diff=pivot-x
                if(diff > mindiff):
                    mindiff = diff

            if((maxdiff + mindiff)<=4):
                #print (maxdiff + mindiff)
                cluster.append(x)
                
            else:
                supercluster.append(cluster)
                mcluster.append(mean(cluster))
                mcluster = [ round(elem, 3) for elem in mcluster]
                meancluster.append(mcluster)
                scluster.append(len(cluster))
                mcluster.append(len(cluster))
                #print(mcluster)
                sizecluster.append(scluster)
                mcluster = []
                cluster = []
                scluster = []
                pivot = x
                cluster.append(x)
                mindiff = 0
                maxdiff = 0

        #print ( meancluster)
        #pd = pandas.DataFrame(meancluster)
        #pd.to_csv("output.csv")

        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()        

        print "finished recording"

if __name__ == "__main__":
    main();
