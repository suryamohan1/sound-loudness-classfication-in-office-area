# This code will be performing k means clustering, finding out the mean square error to get the value of k for k means clustering.
# Then we find the variance from the clusster values to decide on wether to update the threshold value or not.
# This code runs every hour and calculates the threshold value for noise.

from __future__ import division
import sys;
import math; #For pow and sqrt
from random import shuffle, uniform,choice;
import numpy as np;
from matplotlib import pyplot;
import matplotlib.pyplot as plt
import csv
import pandas
import datetime as d
import binascii
import MySQLdb
import time
import smtplib

#code for email
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

###_Pre-Processing_###
def ReadData(fileName):
    #Read the file, splitting by lines
    f = open(fileName,'r');
    lines = f.read().splitlines();
    f.close();
    #sprint lines;
    items = [];
    
    for i in range(1,len(lines)):
        line = lines[i].split(',');
        itemFeatures = [];
        #print line;
        #for j in range(len(line)-1):
        j=1;
        v = float(line[j]); #Convert feature value to float
        itemFeatures.append(v); #Add feature value to dict
        
        items.append(itemFeatures);
    
    shuffle(items);
    #print (items);
    return items;

# calculate the sum of squared error of a list :
def sum_sq_error(results,length):
    m = sum(results) / length
    # calculate variance using a list comprehension
    varRes = sum([(xi - m)**2 for xi in results])
    varRes = varRes / length
    return (varRes)

# calculate the sum of squared error of a list of list:
def sum_sq_err(results,length,mm):
    sum=0
    m=mm[0]
    for i,x in enumerate(results):
        y=x[0]
        #print (y)
        sum=sum + ((y- m) **2)
    #print (sum)
    try :
        sum=sum/length
    except ZeroDivisionError :
        print ("hour_log.csv doesnt have enough data")
        print("zero division by error occurs")
    #print (sum)
    return (sum)

###_Auxiliary Function_###
def FindColMinMax(items):
    n = len(items[0]);
    #print (n)
    minima = [sys.maxint for i in range(n)];
    maxima = [-sys.maxint -1 for i in range(n)];
    
    for item in items:
        for f in range(len(item)):
            if(item[f] < minima[f]):
                minima[f] = item[f];
            
            if(item[f] > maxima[f]):
                maxima[f] = item[f];

    return minima,maxima;

def EuclideanDistance(x,y):
    S = 0; #The sum of the squared differences of the elements
    for i in range(len(x)):
        S += math.pow(x[i]-y[i],2);
    
    return math.sqrt(S); #The square root of the sum

def InitializeMeans(items,k,cMin,cMax):
    #Initialize means to random numbers between
    #the min and max of each column/feature
    
    f = len(items[0]); #number of features
    means = [[0 for i in range(f)] for j in range(k)];
    
    for mean in means:
        for i in range(len(mean)):
            #Set value to a random float
            #(adding +-1 to avoid a wide placement of a mean)
            mean[i] = uniform(cMin[i]+1,cMax[i]-1);

    return means;

def UpdateMean(n,mean,item):
    for i in range(len(mean)):
        m = mean[i];
        m = (m*(n-1)+item[i])/float(n);
        mean[i] = round(m,3);
    
    return mean;


###_Core Functions_###
def FindClusters(means,items):
    clusters = [[] for i in range(len(means))]; #Init clusters
    
    for item in items:
        #Classify item into a cluster
        index = Classify(means,item);
        
        #Add item to cluster
        clusters[index].append(item);
    
    return clusters;

def Classify(means,item):
    #Classify item to the mean with minimum distance
    
    minimum = sys.maxint;
    index = -1;
    
    for i in range(len(means)):
        #Find distance from item to mean
        dis = EuclideanDistance(item,means[i]);
        
        if(dis < minimum):
            minimum = dis;
            index = i;
    
    return index;


def CalculateMeans(k,items,maxIterations=100000):
    #Find the minima and maxima for columns
    cMin, cMax = FindColMinMax(items);
    
    #Initialize means at random points
    means = InitializeMeans(items,k,cMin,cMax);
    
    #Initialize clusters, the array to hold
    #the number of items in a class
    clusterSizes = [0 for i in range(len(means))];
    
    #An array to hold the cluster an item is in
    belongsTo = [0 for i in range(len(items))];
    
    #Calculate means
    for e in range(maxIterations):
        #If no change of cluster occurs, halt
        noChange = True;
        for i in range(len(items)):
            item = items[i];
            #Classify item into a cluster and update the
            #corresponding means.
            
            index = Classify(means,item);
            
            clusterSizes[index] += 1;
            means[index] = UpdateMean(clusterSizes[index],means[index],item);
            
            #Item changed cluster
            if(index != belongsTo[i]):
                noChange = False;
            
            belongsTo[i] = index;
        
        #Nothing changed, return
        if(noChange):
            print ("jdgjf")
            break;
    
    return means;

def PlotClusters(clusters):
    n = len(clusters);
    #Cut down the items to two dimension and store to X
    X = [[] for i in range(n)];
    
    for i in range(n):
        cluster = clusters[i];
        for item in cluster:
            X[i].append(item);

    colors = ['r','b','g','c','m','y','k'];
    
    for x in clusters:
        #Choose color randomly from list, then remove it
        #(to avoid duplicates)
        c = choice(colors);
        colors.remove(c);
        
        Xa = [];
        #Xb = [];
        
        for item in x:
            Xa.append(item[0]);
        #Xb.append(item[0]);
        
        pyplot.plot(Xa,'o',color=c);
    
    pyplot.show();

###_Pre-Processing_###
def ReadData2(fileName):
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
    
    lines = ReadData2('hour_log.csv');
    # initialising all the lists
    supercluster=[]
    meancluster = []
    mcluster= []
    cluster=[]
    sizecluster = []
    scluster = []
    x=lines[0]
    cluster.append(x);
    pivot = x
    mindiff=0
    maxdiff=0

    # code to make clusters of data to be further clustered through k means
    for x in lines[1:] :
        if (x>=pivot):
            diff = x-pivot
            if(diff > maxdiff):
                maxdiff = diff
        elif (x<pivot):
            diff=pivot-x
            if(diff > mindiff):
                mindiff = diff
        
        #print (maxdiff + mindiff)
        if((maxdiff + mindiff)<=4):
            #print (maxdiff + mindiff)
            cluster.append(x)
        else:
            supercluster.append(cluster)
            mcluster.append(mean(cluster))
            #print(mcluster)
            mcluster = [ round(elem, 3) for elem in mcluster ]
            #print(mcluster)
            meancluster.append(mcluster)
            scluster.append(len(cluster))
            mcluster.append(len(cluster))
            sizecluster.append(scluster)
            mcluster = []
            cluster = []
            scluster = []
            pivot = x
            cluster.append(x)
            mindiff = 0
            maxdiff = 0

    supercluster.append(cluster)
    mcluster.append(mean(cluster))
    mcluster.append(len(cluster))
    meancluster.append(mcluster)
    scluster.append(len(cluster))
    sizecluster.append(scluster)
    cluster = []
    mcluster = []
    print(supercluster)
    print ( meancluster)
    pd = pandas.DataFrame(meancluster)
    pd.to_csv("output.csv")

    items = ReadData('output.csv');

    # running the k means algorithm for different values of k
    k=2
    sse_list=[]
    k_list=[]
    super_means = []
    
    while(k and k<6):
        print ("k = ",k)
        means = CalculateMeans(k,items);
        print ("Means = ", means);
        super_means.append(means)
        clusters = FindClusters(means,items);
        #for i,x in enumerate(clusters):
        #print ("i             : ",x)
        #print ("\n")
        #print ("Clusters: ", clusters);
        
        min_ind = means.index(min(means))
        #print(min_ind)
        loud_clusters = clusters[min_ind]
        
        #PlotClusters(loud_clusters)
        #print (loud_clusters)
        #PlotClusters(clusters);
        sse=0
        for i,x in enumerate(clusters):
            sse += sum_sq_err(x,len(x),means[i])
        print (sse)
        print("Means Sq. Error : ",sse)
        sse_list.append(sse)
        k_list.append(k)
        k=k+1

    print(sse_list)
    print (super_means)
    #k= range(2,6)
    #plt.plot(k,sse_list)
    #plt.xlabel("K")
    #plt.ylabel("SSE")
    #plt.title("SSE vs K :")
    #plt.show()

    #deciding the value of K on the basis of mean square error
    decide_k = 100
    min_diff_sse = -100
    for i,x in enumerate(sse_list):
        if (i == 0) or (i == 1):
            value1 = x
        elif((value1 - x) > min_diff_sse):
                min_diff_sse = value1 - x
                print (min_diff_sse)
                decide_k = i + 2
                value1 = x
    print (decide_k)

    print(super_means[decide_k - 2])
    means = super_means[decide_k - 2]
    
    # find variance of means to decide the threshold:
    min_means = 100
    max_means = -100
    for i,x in enumerate(means):
        if (x[0] < min_means):
            min_means = x[0]
        elif (x[0] > max_means):
            max_means = x[0]

    print (min_means)
    print (max_means)

    means_variance = max_means - min_means
    print(means_variance)

    #code for database for threshold
    db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="office web",db="week")
    cursor = db.cursor()
    """sql ="select thresh from thresh where hour = '%s'" % \
                (10)  


    print sql
    cursor.execute(sql)
    results  = cursor.fetchall()
    #print results
    for row in results:
        userid = row[0]
        print "token = %s" % \
                (userid)"""
    #hour_number = 10
    

    #code to get the day and hour slot:

    #print ( time.strftime("%A"))  -- MONDAY
    #print ( time.strftime("%H"))
    day = time.strftime("%A")
    current_hour = time.strftime("%H")
    print (day)
    print ( current_hour )
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
    print hour_number
    
    #updating db values in database:
    if (means_variance >=7):
        subject = 'Day  : %s , hour :%s' % (day,current_hour)
        print subject
        sql ="select thresh from thresh where hour = '%s'" % \
                (current_hour)  
        print sql
        cursor.execute(sql)
        results  = cursor.fetchall()
        #print results
        for row in results:
            prev_t = row[0]
            print "previous threshold = %s" % \
                    (prev_t)
        message = 'threshold value changes: from %s to %s' % (prev_t , min_means)
        print message
        sendemail(subject, message)
        sql= "UPDATE thresh SET thresh='%s' WHERE hour ='%s'" % (min_means,hour_number)
        print sql
        cursor.execute("UPDATE thresh SET thresh='%s' WHERE hour ='%s'" % (min_means,hour_number))
        db.commit()
        
    
        
    

if __name__ == "__main__":
    main();
