# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:39:42 2020

@author: janam
"""

# server.py 
import socket                                         
import time
import pandas as pd
from sklearn.externals import joblib

# create a socket object
serversocket = socket.socket(
	        socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 19999                                           

# bind to the port
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)
print("ready to connect")
rfc = joblib.load('model/rf_model')
while True:
    # establish a connection
    clientsocket,addr = serversocket.accept()      

    print("Got a connection from %s" % str(addr))
    datarec=clientsocket.recv(1024)
   
    print(datarec)
    x=datarec.decode().split("/")
    predictiondata=pd.DataFrame({'latitude':[x[0]],'longitude':[x[1]]})
    print(predictiondata)
    predictiondata['timestamp']=[x[2]]
    print(predictiondata)
    data=predictiondata
    cols = data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    data = data[cols]

    data['timestamp'] = pd.to_datetime(data['timestamp'].astype(str))
    data['timestamp'] = pd.to_datetime(data['timestamp'], format = '%d/%m/%Y %H:%M:%S')
    column_1 = data.iloc[:,0]
    
    DT=pd.DataFrame({"year": column_1.dt.year,
              "month": column_1.dt.month,
              "day": column_1.dt.day,
              "hour": column_1.dt.hour,
              "dayofyear": column_1.dt.dayofyear,
              "week": column_1.dt.week,
              "weekofyear": column_1.dt.weekofyear,
              "dayofweek": column_1.dt.dayofweek,
              "weekday": column_1.dt.weekday,
              "quarter": column_1.dt.quarter,
             })
    data=data.drop('timestamp',axis=1)
    final=pd.concat([DT,data],axis=1)
    X=final.iloc[:,[1,2,3,4,6,10,11]].values
    my_prediction = rfc.predict(X)
    if my_prediction[0][0] == 1:
            my_prediction='Predicted crime : Act 379-Robbery'
    elif my_prediction[0][1] == 1:
            my_prediction='Predicted crime : Act 13-Gambling'
    elif my_prediction[0][2] == 1:
            my_prediction='Predicted crime : Act 279-Accident'
    elif my_prediction[0][3] == 1:
            my_prediction='Predicted crime : Act 323-Violence'
    elif my_prediction[0][4] == 1:
            my_prediction='Predicted crime : Act 302-Murder'
    elif my_prediction[0][5] == 1:
            my_prediction='Predicted crime : Act 363-kidnapping'
    else:
         my_prediction='Place is safe no crime expected at that timestamp.'
    print(my_prediction)
    res = bytes(my_prediction, 'utf-8') 
    clientsocket.send(res)
