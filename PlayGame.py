import keyboard
import mss
import cv2
import numpy
from time import time, sleep
import pyautogui

pyautogui.PAUSE = 0
marks = []

print("Press 's' to start playing.")
print("Once started press 'q' to quit.")
keyboard.wait('s')

#get timestamp for reference
starttime = time()
droneTime =  0
spellTime = 0

# user defined monster positions
print("Put mouse over targets and press 'm' to mark.")
while len(marks) < 10:
    x, y = pyautogui.position()
    positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
    print(positionStr, end='')
    print('\b' * len(positionStr), end='', flush=True)
    try:
        if keyboard.is_pressed('m'):
            marks.append([x, y])
            print("marks {}".format(len(marks)))
            keyboard.wait("n")
    except:
        print("Press m to mark")


sct = mss.mss()

# define the window position and size
dimensions = {
        'left': 1120,
        'top': 50,
        'width': 650,
        'height': 930
    }

# init some variables
x = 0
y = 0
loop_num = 0

# read the needles and get shapes
chest = cv2.imread('Chest2.png')
close_button = cv2.imread('CloseButton.png')

chest_w = chest.shape[1]
chest_h = chest.shape[0]
chest_remove = chest[:,:,:3]

close_button_w = close_button.shape[1]
close_button_w = close_button.shape[0]

fps_time = time()

# check for a flying chest
def findAndClickChest():
    scr = numpy.array(sct.grab(dimensions))

    # Cut off alpha
    scr_remove = scr[:,:,:3]
    
    result = cv2.matchTemplate(scr_remove, chest_remove, cv2.TM_CCOEFF_NORMED)
    
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    print(f"Max Val: {max_val} Max Loc: {max_loc}")
    src = scr.copy()
    if max_val > .75:
        x = max_loc[0] + dimensions['left'] + (chest_w / 2)
        y = max_loc[1] + dimensions['top'] + (chest_h /2)
        cv2.rectangle(scr, max_loc, (max_loc[0] + chest_w, max_loc[1] + chest_h), (0,255,255), 2)
        # click chest location
        pyautogui.click(x=x, y=y)
        sleep(0.02)

        # click modal close button
        pyautogui.click(1617, 345)

    
    #cv2.imshow('Screen Shot', scr_remove)
    #cv2.waitKey(1)
    
    

def upgradeMonsters(marks):
    for mark in marks:
        # click the monster
        pyautogui.click(mark[0],mark[1])
        sleep(0.02)
        # click the upgrade button
        pyautogui.click(960 + 635, 850)
        sleep(0.02)
    
    # click where the flying chest close button is just in case it got hit by accident
    pyautogui.click(1617, 345)
    sleep(0.02)

    # close out of the tower selection
    pyautogui.click(1739, 872)
    sleep(0.02)

def clickAllSpells():
    pyautogui.click(1552,867)
    sleep(0.02)
    pyautogui.click(1479,867)
    sleep(0.02)
    pyautogui.click(1408,867)
    sleep(0.02)
    pyautogui.click(1323,867)

def spawnDroneSwarm():
    pyautogui.click(1143,226)
    sleep(0.02)
    clickAllSpells()


# Main Loop
while True:

    # check for a flying chest
    findAndClickChest()
    
    # every 30 loops try and upgrade all monsters
    if loop_num % 30 == 0:
        upgradeMonsters(marks)
        loop_num = 0

    # spawn drones every 20 minutes
    if time() > droneTime + 1205:
        spawnDroneSwarm()
        droneTime = time()

    # click all spells every 30 seconds
    if time() > spellTime + 30:
        clickAllSpells()
        spellTime = time()

    # slow things down a tad
    sleep(.10)
    
    # if q is pressed, quit
    if keyboard.is_pressed('q'):
        break

    # if p is pressed, pause
    if keyboard.is_pressed('p'):
        keyboard.wait('p')

    # debug logging the position of the mouse
    x, y = pyautogui.position()
    positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
    print(positionStr)

    #print('FPS: {}'.format(1 / (time() - fps_time)))
    #print('Loop: {}'.format(loop_num))
    fps_time = time()
    loop_num += 1


