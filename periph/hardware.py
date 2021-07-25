
#Initialization
import RPi.GPIO as GPIO
import smtplib
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import time
from picamera import PiCamera
import os
import shutil
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import model_from_json
camera=PiCamera()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#Variable-init
i=0
Plastics_Count=0
Non_Plastics_Count=0
Papers_Count=0
Metals_Count=0
#Metal GPIO-init
INDUCTIVE=27 #15
GPIO.setup(INDUCTIVE,GPIO.IN)
#slider-init
GPIO.setup(13,GPIO.OUT)
q=GPIO.PWM(13,50)
#rotate bin-init
GPIO.setup(12,GPIO.OUT)
p=GPIO.PWM(12,50)
#Functions-init
#Mailing Function
def mail( msg):
 s = smtplib.SMTP('smtp.gmail.com', 587)
 s.starttls()
 s.login("autowastesegregator@gmail.com", "sixsigma")
 s.sendmail("autowastesegregator@gmail.com", "merwinajay@gmail.com", msg)
 s.quit() 
#Check if Bin is Empty
def isEmpty():
 if (Plastics_Count==20):
  msg="Plastic Bin is Full"
  print(msg)
  mail(msg)
  return 0
 elif (Non_Plastics_Count==20):
  msg="Non Plastic Bin is Full"
  mail(msg)
  return 0
 elif (Metals_Count==20):
  msg="Metal Bin is Full"
  mail(msg)
  return 0
 elif (Papers_Count==20):
  msg="Paper Bin is Full"
  mail(msg)
  return 0
 else:
  return 1
#Slider-func
def slide():
 q.start(0)
 time.sleep(2)
 q.ChangeDutyCycle(12.5)
 time.sleep(2.5)
 q.ChangeDutyCycle(2.5)
 time.sleep(2.5)
 q.stop(0)
#Rotate-bin-nonplastic
def rot_bin_np():
 p.start(0)
 time.sleep(1)
 p.ChangeDutyCycle(2)
 time.sleep(5)
 p.ChangeDutyCycle(6)
 time.sleep(2)
 slide()
 time.sleep(1)
 p.ChangeDutyCycle(10)
 time.sleep(5)
 p.stop(0)
#Rotate-bin-Paper
def rot_bin_paper():
 p.start(0)
 time.sleep(1)
 p.ChangeDutyCycle(2.5)
 time.sleep(5)
 p.ChangeDutyCycle(10)
 time.sleep(2)
 slide()
 time.sleep(1)
 p.ChangeDutyCycle(2.5)
 time.sleep(5)
 p.stop(0)
def rot_bin_metal():
 p.start(0)
 time.sleep(1)
 p.ChangeDutyCycle(2.5)
 time.sleep(5)
 p.ChangeDutyCycle(10)
 time.sleep(2)
 slide()
 time.sleep(1)
 p.ChangeDutyCycle(2.5)
 time.sleep(5)
 p.stop(0)
#Main code
#Labels-init
#Variables_init
DATADIR="/home/pi/FYP/FYP_FINAL_DATASET"
CATEGORIES=["BATTERY","BULBS","CARDBOARD","CIGARETTES","DIAPERS","MEDICINE_BOTTLES","PAPER","PAPER_CUPS","PESTICIDE_BOTTLES","PLASTIC_BAGS","PLASTIC_BOTTLES","PLASTIC_WRAPPERS"]

while (isEmpty()):
 #Camera-on
 time.sleep(2)
 camera.start_preview()
 time.sleep(5)
 camera.capture('/home/pi/FYP/CAPTURED_IMAGE/image'+str(i)+'.jpg')
 camera.stop_preview()
 time.sleep(1)
 #Image-preprocess
 IMG_SIZE = 299
 img_array = cv2.imread('/home/pi/FYP/CAPTURED_IMAGE/image'+str(i)+'.jpg')
 new_array = cv2.resize(img_array,(IMG_SIZE,IMG_SIZE))
 b,g,r=cv2.split(new_array)
 new_array=cv2.merge([r,g,b])
 #Object-presence-check
 edges=cv2.Canny(new_array,IMG_SIZE,IMG_SIZE)
 white=np.sum(edges==255)
 print(white)
 if(white<=50):
  continue
 else:
  while (isEmpty()):
   if (GPIO.input(INDUCTIVE) == False):
    rot_bin_metal()
    slide()
    print("METAL")
    Metals_Count=Metals_Count+1
    time.sleep(3)
   else:
    print("NO")
    new_array=new_array / 255.0
    X = new_array.reshape([-1,IMG_SIZE,IMG_SIZE,3])
     #Load saved model
    model=keras.models.load_model("/home/pi/FYP/FYP_MODELS/FYP_TF_MOBILENET_FINAL.h5")
   #Prediction
    prediction = model.predict(X)
   #Label prediction-concat
    Plastic=prediction[0,5]+prediction[0,8]+prediction[0,9]+prediction[0,10]+prediction[0,11]
    Paper=prediction[0,2]+prediction[0,6]+prediction[0,7]
    Non_Plastic=prediction[0,0]+prediction[0,1]+prediction[0,3]+prediction[0,4]
   #hardware-mechanism
    if(Plastic>Non_Plastic and Plastic>Paper):
     Plastics_Count=Plastics_Count+1
     print("2")
     shutil.move('/home/pi/FYP/CAPTURED_IMAGE/image'+str(i)+'.jpg','/home/pi/FYP/Reinforcement_Learning/Plastic')
     slide()
     time.sleep(1)
     break
    elif(Non_Plastic>Plastic and Non_Plastic>Paper):
     Non_Plastics_Count=Non_Plastics_Count+1
     shutil.move('/home/pi/FYP/CAPTURED_IMAGE/image'+str(i)+'.jpg','/home/pi/FYP/Reinforcement_Learning/Non_Plastic')
     rot_bin_np()
     time.sleep(1)
     break
    else:
     Papers_Count=Papers_Count+1
     shutil.move('/home/pi/FYP/CAPTURED_IMAGE/image'+str(i)+'.jpg','/home/pi/FYP/Reinforcement_Learning/Paper')
     rot_bin_paper()
     time.sleep(1)
     break
   i=i+1
GPIO.cleanup()







