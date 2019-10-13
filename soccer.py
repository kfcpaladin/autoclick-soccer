import pyautogui
from pynput.keyboard import *
import numpy as np
import mss
import mss.tools
import cv2
from PIL import Image

from detect import *



pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

# take sc, process and get coord
def find_ball(model, rect):
    t0 = time.time()
    with mss.mss() as screen:
        image = screen.grab(rect)

    data = np.array(image)
    x = data[:,:,:3] / 255
    x = cv2.resize(x, (320, 455))
    x = x[...,::-1].copy()
    x = np.swapaxes(x, 0, 2)
    
    # only get first 3 channels 
    x = torch.from_numpy(x).to(torch.device('cuda:0'), dtype=torch.float)
    if x.ndimension() == 3:
        x = x.unsqueeze(0)

    pred = model(x)[0]
    pred = non_max_suppression(pred, 0.3, 0.5)
    
    if (pred is not None):
        for prediction in pred:
            if (prediction is not None):
                pre = prediction.cpu().detach().numpy()
                t1 = time.time()
                centre_y = (pre[0][0]+pre[0][2])/2
                centre_x = (pre[0][1]+pre[0][3])/2
                
                print("Y Coordinate:{0:0=3.0f}".format(centre_y), "X Coordinate:{0:0=3.0f}".format(centre_x), "Confidence:{0:.2f} %".format(pre[0][4]*100), "Time Taken:{0:.5f}".format(t1-t0), sep="      ", end = "\r")
                t1 = time.time()
                return centre_x, centre_y,
            else:
                return 0, 0
    else:
        return 0, 0
    
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
    print("// AutoClicker by NeedtobeatVictor")
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

    print("Loading Device 0...")
    # replace with 'cpu' if using cpu
    device = torch.device('cuda:0')


    print("Loading weights...")
    model = Darknet('cfg/dean.cfg', (320, 455))
    model.load_state_dict(torch.load('weights/best.pt', map_location=device)['model'])
    model.to(device).eval()
    torch.no_grad()

    print("Graph initialized")

    rect = {'left': 1384, 'top': 154, 'width': 320, 'height': 455}

    display_controls()

    '''

    with open("../assets/model/large_model/model.h5", "rb") as file:
        model = LiteModel(file.read())

    '''
    accel = 1200
    prevy = rect['top']+rect['height'] - 10
    prevx = rect['left']+rect['width']*0.5
    t0 = time.time()
    while running:
        t1 = time.time()
        dt = t1-t0
        t0 = t1
        pyautogui.PAUSE = 0.0
        centreX, centreY = find_ball(model, rect)
        if centreX == 0 and centreY == 0:
            continue
        dx = centreX-prevx
        dy = centreY-prevy
        prevx = centreX
        prevy = centreY
        centreX = centreX + rect['left'] + dx
        centreY = centreY + rect['top'] + dy + dt*accel
        if centreY>rect['top']+rect['height']/3:
            if centreY<rect['top']+rect['height']-5 and centreX>rect['left']+2 and centreX < rect['left']+rect['width']-2:
                pyautogui.click(x=centreX, y=centreY)

    
           
    lis.stop()


if __name__ == "__main__":
    main()