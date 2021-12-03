# First XGBoost model for Pima Indians dataset
import numpy
import pandas as pd
from xgboost import XGBClassifier
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
#acelerometer imports
import time
import board
import busio
import adafruit_adxl34x
import RPi.GPIO as GPIO

from twilio.rest import Client
import mysql.connector

from math import sqrt

#package for selenium
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import warnings

warnings.filterwarnings("ignore")

# path = "/content/drive/MyDrive/DataSet/new_sensor_raw.csv"
new_path = "mysensordata.csv"
dataframe = pd.read_csv(new_path)
array = dataframe.values
x = array[:,1:7]
y = array[:,0:1]
            # split data into train and test sets
test_size = 0.12
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state= 0)
                # fit model no training data
#model = XGBClassifier(eval_metric='mlogloss')
#new_path = "SENSORDATA.csv"
#dataframe = pd.read_csv(new_path)
#array = dataframe.values
#x = array[:2222,1:8]
#y = array[:2222,0:1]
            # split data into train and test sets
#test_size = 0.5
#X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state= 0)
                # fit model no training data
#model = XGBClassifier(eval_metric='mlogloss')
#model.fit(X_train, y_train)
#model.fit(X_train, y_train)
train = xgb.DMatrix(X_train,label=y_train)
test = xgb.DMatrix(X_test,label=y_test)
param = {
    'max_depth' : 3,
    'eta' : 0.7,
    'objective': 'multi:softmax',
    'num_class':2
}
epochs = 99
model = xgb.train(param,train,epochs)
predictions = model.predict(test)
#accuracy = accuracy_score(y_test, predictions)

accident = 0

ph_numb=""
relative_numb=""
pwd="pass"
call_count = 0
r=1
print("ACCIDENT DETECTION AND ALERT SYSTEM")
print("===================================")
#print("Accuracy: %.4f%%" % (accuracy * 100.0))
while(r==1):
    print("Login Console")
    User_Name = input("Enter the User Name :")
    password = input("Enter Password :")
    if(pwd == password):
        print("Login Successful")
        ph_numb = "+91" + str(input("Enter the User's Phone Number(eg : 9176252768) :"))
        relative_numb = "+91" + str(input("Enter the Relative's Phone Number :"))
        r=0
    else:
        print("Password Mismatch")
        r=1
#User_Name = "Siva"
#ph_numb = "+919176252768"
#relative_numb="+917200110017"
print("\nDetection System Activated")

channel = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.IN)

#def callback(channel):
        
# evaluate predictions
s=""
s1=""

#def mycallback(channel):
def mycallback(channel):
    GPIO.remove_event_detect(channel)
    if True:
        i2c = busio.I2C(board.SCL, board.SDA)
        accelerometer = adafruit_adxl34x.ADXL345(i2c)
        accelerometer.enable_tap_detection(tap_count=1, threshold=150, duration=50, latency=100, window=255)
        while True:
            detect = "False"
            detect = str(accelerometer.events['tap'])
            if (detect == "True"):
                s = time.time()
                x,y,z=accelerometer.acceleration
                gx=x*6.533
                gy=y*6.533
                gz=z*6.533
                l1 = []
                l2 = []
                l1.append(x)
                l1.append(y)
                l1.append(z)
                l1.append(gx)
                l1.append(gy)
                l1.append(gz)
                l2.append(l1)
                sensor_data = xgb.DMatrix(l2)
                model = xgb.train(param,train,epochs)
                print("Shock Detected in Sensor\n Current Acceleration Data")
                print(l2)
                predictions = model.predict(sensor_data)
                index = round(predictions[0])
                print(index)
                if(index == 0):
                    print("Accident At Front")
                    accident = 1
                elif(index == 1):
                    accident = 1
                    print("Accident At Back")
                
                if(accident==1):
                    client = Client("AC1aaee3c50b11dcb77de3fca9b93e1deb", "63486573b4e7b69ce676ce13f7b7ed26")
                    call_count = 0
                    print("Calling the user to verify the accident is occured or not")
                    while call_count != 1:
                        call = client.calls.create(
                                                twiml=f'<Response><Say voice = "Polly.Emma" language = "en-IN"><prosody volume="10dB" rate="slow">Checker Call.. Are you fine User!!</prosody></Say></Response>',
                                                to= ph_numb,
                                                from_='+13649003355'
                                            )
                        calls = client.calls(call.sid).fetch()
                        time.sleep(27)
                        calls = client.calls(call.sid).fetch()
                        print("Call Status : " + calls.status)
                        call_count+=1
                        
                    if calls.status == "ringing" and calls.status != "completed":
                        print("Accident is Confirmed , Alert System Activated !!")
                        e = time.time()
                        fore = "{:.2f}".format(e-s)
                        s1=time.time()
                        print("Time Taken to Detect the Accident : " + fore + "sec")
                        # connection
                        mydb = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="hospital"
                        )
                        #chrome_options = Options()
                        #chrome_options.add_argument("--headless")
                        driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver')
                        # in-built lat and long of current place
                        latitude = 12.987184
                        longitude = 79.973227
                        print(f"User Latitude and Longitude Coords :{latitude},{longitude}")
                        z = 14
                        url = 'https://www.google.com/maps/@' + str(latitude) + ',' + str(longitude) + ',' + str(z) + 'z'
                        driver.get(url)
                        achains = ActionChains(driver)
                        time.sleep(15)
                        right_click = driver.find_element(By.XPATH,"//body")
                        achains.context_click(right_click).perform()
                        time.sleep(2)
                        what = driver.find_element(By.CSS_SELECTOR,".nbpPqf-menu-x3Eknd[aria-checked='false'][data-index='3']")
                        what.click()
                        time.sleep(2)
                        area = driver.find_element(By.XPATH,"//div[@class='GaSlwc-uhFGfc-WsjYwc-Q7Zjwb-RWgCYc GaSlwc-uhFGfc-WsjYwc-c8csvc']").text
                        place = driver.find_element(By.XPATH,"//div[@class='GaSlwc-uhFGfc-WsjYwc-Q7Zjwb-RWgCYc']").text
                        print("Accident Area : "+ area + " " + place)
                        pincode = str(place[-6:-1]) + str(place[-1])
                        pincode1=str(602117)
                        # query for getting all hospital list :
                        mycursor = mydb.cursor()
                        mycursor.execute(f"SELECT * FROM hospital_list WHERE Pincode = {pincode1}")
                        myresult = mycursor.fetchall()
                        #print("DB : ",myresult)
                        LatLong_list = []
                        # appending the lat,long values to a list
                        for datalist in myresult:
                            LatLong_list.append([datalist[0], datalist[1]])
                        # calculation Eucledian Distance between current lat,long with all hopital's lat,long
                        distance_list = []
                        for pos in LatLong_list:
                            lat = pos[0]
                            lon = pos[1]
                            distance = sqrt((latitude - lat) * (latitude - lat) + (longitude - lon) * (longitude - lon))
                            distance_list.append(distance)
                            distance = 0
                        # getting smaller distance value and finding its index
                        min_val = min(distance_list)
                        index = distance_list.index(min_val)
                        # getting lat and long values having smaller Eucledian Distance
                        hospital_lat = LatLong_list[index][0]
                        hospital_long = LatLong_list[index][1]
                        # getting hospital Phone Number and Name :
                        mycursor.execute(f"SELECT PhoneNumber,Name,Address FROM hospital_list WHERE Latitude = {hospital_lat} AND Longitude = {hospital_long}")
                        detail = mycursor.fetchone()
                        Phone, Hospital_Name, Address = detail[0], detail[1], detail[2]
                        print(f"{Hospital_Name} is Nearest whose location is @{hospital_lat, hospital_long} and contact @{Phone}")
                        #Voice call -> Hospital
                        while calls.status != "completed":
                            call = client.calls.create(
                                                twiml=f'<Response><Say voice = "Polly.Emma" language = "en-IN"><prosody volume="10dB" rate="slow">This is regarding an emergency happened at {place}. Corresponding latitude  is {latitude} and longitude is {longitude}</prosody></Say></Response>',
                                                to= Phone,
                                                from_='+13649003355'
                                            )
                            calls = client.calls(call.sid).fetch()
                            time.sleep(55)
                            calls = client.calls(call.sid).fetch()
                            print("Call done to hospital : ",calls.status)
                            e1 = time.time()
                            fore1 = "{:.2f}".format(e1-s1)
                            print("Time Taken to Send notification to the Hospital : " + fore1 + "sec")
                            time.sleep(10)

                        #Voice call -> Relative
                        call = client.calls.create(
                                                twiml=f'<Response><Say voice = "Polly.Emma" language = "en-IN"><prosody volume="10dB" rate="slow">It\'s emergency , your relative {User_Name} have met with an accident  and admitted in the hospital. Hospital address is  {Address}. I repeat address is  {Address}.</prosody></Say></Response>',
                                                to= relative_numb,
                                                from_='+13649003355'
                                            )
                        calls = client.calls(call.sid).fetch()
                        time.sleep(60)
                        calls = client.calls(call.sid).fetch()
                        print("Call done to Relative : ",calls.status)
                        #Message -> Relative
                        account_sid = 'AC1aaee3c50b11dcb77de3fca9b93e1deb'
                        auth_token = '63486573b4e7b69ce676ce13f7b7ed26'
                        client = Client(account_sid, auth_token)
                        message = client.messages.create(
                            messaging_service_sid='MG95c370dd6dbd6b867b4fe04328f6ecda',
                            body=f"It's emergency , your relative {User_Name} have met with an accident  and admitted in {Hospital_Name}.  {Address}.",
                            to= relative_numb
                        )
                        print("Message sent to relative ")
                        time.sleep(0.5)
                        break
                    else:
                        print("Major Accident not occured")
                        e = time.time()
                        fore = "{:.2f}".format(e-s)
                        print("Time Taken to Detect the Accident : " + fore + "sec")

    #GPIO.add_event_callback(channel,callback)

GPIO.add_event_detect(channel,GPIO.BOTH,callback=mycallback)

while True:
    time.sleep(0.5)        
        

