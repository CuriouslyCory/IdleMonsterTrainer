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
chest = cv2.imread('Chest2.png', cv2.IMREAD_GRAYSCALE)
close_button = cv2.imread('CloseButton.png', cv2.IMREAD_GRAYSCALE)

chest_w = chest.shape[1]
chest_h = chest.shape[0]

close_button_w = close_button.shape[1]
close_button_w = close_button.shape[0]

tower_menu_close = [1727, 928]
tower_menu_upgrade = [1521,927]
drone_spawn_button = [1142, 220]
drone_spawn_start = [1646,350]
chest_modal_close = [1639, 350]
carrier_spawn_button = [1139,279]
carrier_spawn_start = [1408,787]
spell1 = [1305, 939]
spell2 = [1388, 939]
spell3 = [1476, 939]
spell4 = [1569, 939]


fps_time = time()

# check for a flying chest
def findAndClickChest():
    
    scr = numpy.array(sct.grab(dimensions))
    scr_remove = cv2.cvtColor(scr, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(scr_remove, chest, cv2.TM_CCOEFF_NORMED)
    
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
        pyautogui.click(chest_modal_close[0], chest_modal_close[1])

    
    #cv2.imshow('Screen Shot', scr_remove)
    #cv2.waitKey(1)
    
    

def upgradeMonsters(marks):
    for mark in marks:
        # click the monster
        pyautogui.click(mark[0], mark[1])
        sleep(0.02)
        # click the upgrade button
        pyautogui.click(tower_menu_upgrade[0], tower_menu_upgrade[1])
        sleep(0.02)
    
    # click where the flying chest close button is just in case it got hit by accident
    pyautogui.click(chest_modal_close[0], chest_modal_close[1])
    sleep(0.02)

    # close out of the tower selection
    pyautogui.click(tower_menu_close[0], tower_menu_close[1])
    sleep(0.02)

def clickAllSpells():
    pyautogui.click(spell1[0], spell1[1])
    sleep(0.02)
    pyautogui.click(spell2[0], spell2[1])
    sleep(0.02)
    pyautogui.click(spell3[0], spell3[1])
    sleep(0.02)
    pyautogui.click(spell4[0], spell4[1])

def spawnDroneSwarm():
    pyautogui.click(drone_spawn_button[0], drone_spawn_button[1])
    sleep(0.02)
    pyautogui.click(drone_spawn_start[0], drone_spawn_start[1])
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


