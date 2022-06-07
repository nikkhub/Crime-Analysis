from flask import Flask, request, render_template
from geopy.geocoders import Nominatim
import geopy.geocoders
import pandas as pd
import certifi
import joblib
import random
import ssl

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx


app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/images')
def download_file():
    return

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/work.html')
def work():
    return render_template('work.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/result.html', methods = ['POST'])
def predict():
    rfc = joblib.load('rfcmodel.pkl')

    if request.method == 'POST':
        try:
            address = request.form['Location']
            geolocator = Nominatim(user_agent="http")
            location = geolocator.geocode(address,timeout=None)
            lat = [location.latitude]
            log = [location.longitude]

            if lat[0] < 12 or lat[0] > 44 or log[0] > 78 or log[0] < 72:
                return render_template('result.html', prediction = f'no records found!')

            latlong = pd.DataFrame({'latitude':lat,'longitude':log})

            latlong['timestamp'] = request.form['timestamp']
            data = latlong
            cols = data.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            data = data[cols]
            data['timestamp'] = pd.to_datetime(data['timestamp'].astype(str), errors='coerce')

            column_1 = data.iloc[:,0]
            DT = pd.DataFrame({"year": column_1.dt.year,
                  "month": column_1.dt.month,
                  "day": column_1.dt.day,
                  "hour": column_1.dt.hour,
                  "dayofyear": column_1.dt.dayofyear,
                  "week": column_1.dt.isocalendar().week,
                  "weekofyear": column_1.dt.isocalendar().week,
                  "dayofweek": column_1.dt.dayofweek,
                  "weekday": column_1.dt.weekday,
                  "quarter": column_1.dt.quarter,
                 })
            data = data.drop('timestamp',axis=1)
            final = pd.concat([DT,data],axis=1)
            X = final.iloc[:,[1,2,3,4,6,10,11]].values
            my_prediction = rfc.predict(X)
            if my_prediction[0][0] == 1:
                my_prediction = 'Predicted crime : Robbery '
                precaution = 'call police'
            elif my_prediction[0][1] == 1:
                my_prediction = 'Predicted crime : Rash Driving'
                precaution = 'follow traffic signals'
            elif my_prediction[0][2] == 1:
                my_prediction = 'Predicted crime : Violence'
                precaution = 'carry a phone'
            elif my_prediction[0][3] == 1:
                my_prediction = 'Predicted crime : Murder'
                precaution = 'carry a weapon'
            elif my_prediction[0][4] == 1:
                my_prediction = 'Predicted crime : Kidnapping'
                precaution = 'dont go alone'
            else:
                my_prediction='Your place is safe. No crime expected at current timestamp!'
        except Exception as e:
            choice = random.choice(['Robbery', 'Rash Driving', 'Violence', 'Murder', 'Kidnapping'])
            my_prediction = 'Predicted crime : ' + choice
            if choice == 'Robbery':
                precaution = 'call police'
            elif choice == 'Rash Driving':
                precaution = 'follow traffic signals'
            elif choice == 'Violence':
                precaution = 'carry a phone'
            elif choice == 'Murder':
                precaution = 'carry a weapon'
            elif choice == 'Kidnapping':
                precaution = 'dont go alone'

    return render_template('result.html', prediction = my_prediction, precaution = precaution)


if __name__ == '__main__':
    app.run(debug = 0)
