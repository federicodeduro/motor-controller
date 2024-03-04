from flask import Flask, render_template, Response, request, send_from_directory
from camera import VideoCamera
import os
import RPi.GPIO as GPIO
from time import sleep

in1 = 24
in2 = 23
en = 25
temp1 = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p = GPIO.PWM(en,5)
p.start(100)

pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.

# App Globals (do not edit)
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

@app.route('/')
def index():
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Take a photo when pressing camera button
@app.route('/picture')
def take_picture():
    pi_camera.take_picture()
    return "None"

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<button>/<intensity>")
def action(button, intensity):
    intensity = float(intensity)
    if button == '0': #Sterzo
        if intensity < 0:
            print("sterzo a sinistra")
        elif intensity > 0:
            print("sterzo a destra")
    elif button == '6': # Acceleratore
        print("Accelera (" + str(intensity) + ")")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        p.ChangeDutyCycle(100*intensity)
    elif button == '7': # Freno
        #print("Frena (" + intensity + ")")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        p.ChangeDutyCycle(100*intensity)
    else:
        # Problem, stop the motor
        print("problem")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)

    return render_template('index.html')

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False)
