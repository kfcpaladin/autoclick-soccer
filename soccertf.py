import pyautogui
from pynput.keyboard import *
import numpy as np
import mss
import os
# uncomment for CPU
# os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import mss.tools
import cv2
from PIL import Image
import time

import tensorflow as tf



pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

# take sc, process and get coord
def find_ball(interpreter, rect, input_details, output_details):
    t0 = time.time()
    with mss.mss() as screen:
        image = screen.grab(rect)
    t2 = time.time()
    data = np.array(image)
    x = data[:,:,:3]
    x = cv2.resize(x, (160, 227))
    x = x[...,::-1].copy()
    
    x = np.expand_dims(x, 0)

    input_data = tf.convert_to_tensor(x, dtype = tf.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    t1 = time.time()
    print("X Coordinate:{0:0=3.0f}".format(output_data[0][0]), "Y Coordinate:{0:0=3.0f}".format(output_data[0][1]), "Time Taken:{0:.5f}".format(t1-t0), "Time Taken:{0:.5f}".format(t2-t0),sep="      ", end = "\r")

    return output_data[0][0], output_data[0][1]
    
    '''

    x_centre, y_centre, width, height = y

    width = rect['width']
    height = rect['height']
    
    return x_centre*width, y_centre*height
    
    '''


#  autoclick buttons
resume_key = Key.f1
pause_key = Key.f2
exit_key = Key.f3

pause = True
running = True

def on_press(key):
    global running, pause

    if key == resume_key:
        pause = False
        print("[Resumed]")
    elif key == pause_key:
        pause = True
        print("[Paused]")
    elif key == exit_key:
        running = False
        print("[Exit]")
        quit()

def display_controls():
    print("// AutoClicker by HouDeanie, Kfcpaladin and FiendChain")
    print("// - Settings: ")
    print("\t delay = " + str(delay) + ' sec' + '\n')
    print("// - Controls:")
    print("\t F1 = Resume")
    print("\t F2 = Pause")
    print("\t F3 = Exit")
    print("\t ESC = For real Exit")
    print("-----------------------------------------------------")
    print('Don\'t need to Press F1 to start ...')

# Number of pixels under ball center to click
delay = 0.0 # in seconds

def main():
    
    desiredscore = 10000
    currentscore = 0
    lis = Listener(on_press=on_press)
    lis.start()



    print("Loading weights...")
    interpreter = tf.lite.Interpreter(model_path="lite/model-055.tflite")
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(input_details)


    print("Graph initialized")

    with mss.mss() as sct:
        screen = sct.shot()
    
    find = cv2.imread('scrnsht.png', cv2.IMREAD_GRAYSCALE)
    screen = cv2.imread(screen, cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(screen,find,cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print("Game window found at " + str(max_loc[0]) + " and " + str(max_loc[1]))

    rect = {'left': max_loc[0], 'top': max_loc[1]-1, 'width': 320, 'height': 455}

    display_controls()

    '''

    with open("../assets/model/large_model/model.h5", "rb") as file:
        model = LiteModel(file.read())

    '''
    accel = 3600
    prevy = rect['top']+rect['height'] 
    prevx = rect['left']+rect['width']*0.5
    t0 = time.time()
    while running:
        t1 = time.time()
        pyautogui.PAUSE = delay
        centreX, centreY = find_ball(interpreter, rect, input_details, output_details)
        if centreX == -1 and centreY == -1:
            continue
        dt = t1-t0
        t0 = t1
        dx = centreX-prevx
        dy = centreY-prevy
        prevx = centreX
        prevy = centreY
        centreX = centreX + rect['left'] + dx
        centreY = centreY + rect['top'] + dy + dt*accel
        if centreY>rect['top']+rect['height']/2 and centreY<rect['top']+rect['height']-5 and centreX>rect['left']+2 and centreX < rect['left']+rect['width']-2:
            pyautogui.click(x=centreX, y=centreY)

    
           
    lis.stop()


if __name__ == "__main__":
    main()