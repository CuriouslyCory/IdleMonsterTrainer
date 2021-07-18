import keyboard
import mss
import cv2
import numpy
from time import time, sleep
import pyautogui
import tkinter as tk

pyautogui.PAUSE = 0


class App(tk.Frame):
    
    #set all variables
    marks = []

    #get timestamp for reference
    starttime = time()
    droneTime =  0
    spellTime = 0

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

    # locations
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

    # read the needles and get shapes
    chest = cv2.imread('Chest2.png', cv2.IMREAD_GRAYSCALE)

    chest_w = chest.shape[1]
    chest_h = chest.shape[0]

    sct = mss.mss()
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.startLoops()
        
        
    def createWidgets(self):


        #create buttons
        self.setMarkersBtn = tk.Button(self)
        self.setMarkersBtn["text"] = "Mark Towers"
        self.setMarkersBtn["command"] = self.markTowers
        self.setMarkersBtn.grid(column=1, row=0)

        self.pauseBtn = tk.Button(self)
        self.pauseBtn["text"] = "Pause"
        self.pauseBtn["command"] = self.pause
        self.pauseBtn.grid(column=1, row=1)

        #create debug text
        self.locationTxt = tk.Label(self)
        self.locationTxt.grid(column=1, row=2)
        
        self.chestDebug = tk.Label(self)
        self.chestDebug.grid(column=1, row=3)


    def markTowers(self):
        # user defined monster positions
        self.marks = []
        print("Put mouse over targets and press 'm' to mark.")
        while len(self.marks) < 10:
            keyboard.wait('m')
            x, y = pyautogui.position()
            self.marks.append([x, y])
            print("Marks: {}, Position: {}, {}".format(len(self.marks), x, y))

    # check for a flying chest
    def findAndClickChest(self):
        
        scr = numpy.array(self.sct.grab(self.dimensions))
        scr_remove = cv2.cvtColor(scr, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(scr_remove, self.chest, cv2.TM_CCOEFF_NORMED)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        debugStr = "Max Val: {} Max Loc: {}".format(max_val, max_loc)
        self.chestDebug["text"] = debugStr
        src = scr.copy()
        if max_val > .75:
            x = max_loc[0] + self.dimensions['left'] + (self.chest_w / 2)
            y = max_loc[1] + self.dimensions['top'] + (self.chest_h /2)
            cv2.rectangle(scr, max_loc, (max_loc[0] + self.chest_w, max_loc[1] + self.chest_h), (0,255,255), 2)
            # click chest location
            pyautogui.click(x=x, y=y)
            sleep(0.02)

            # click modal close button
            pyautogui.click(self.chest_modal_close[0], self.chest_modal_close[1])

        #cv2.imshow('Screen Shot', scr_remove)
        #cv2.waitKey(1)
        self.master.after(500, self.findAndClickChest)
    

    def upgradeMonsters(self):
        if(len(self.marks) > 0):
            for mark in self.marks:
                # click the monster
                pyautogui.click(mark[0], mark[1])
                sleep(0.02)
                # click the upgrade button
                pyautogui.click(self.tower_menu_upgrade[0], self.tower_menu_upgrade[1])
                sleep(0.02)
            
            # click where the flying chest close button is just in case it got hit by accident
            pyautogui.click(self.chest_modal_close[0], self.chest_modal_close[1])
            sleep(0.02)

            # close out of the tower selection
            pyautogui.click(self.tower_menu_close[0], self.tower_menu_close[1])
            sleep(0.02)
        self.master.after(4000, self.upgradeMonsters)


    def clickAllSpells(self):
        pyautogui.click(self.spell1[0], self.spell1[1])
        sleep(0.02)
        pyautogui.click(self.spell2[0], self.spell2[1])
        sleep(0.02)
        pyautogui.click(self.spell3[0], self.spell3[1])
        sleep(0.02)
        pyautogui.click(self.spell4[0], self.spell4[1])
        self.master.after(30000, self.clickAllSpells)


    def spawnDroneSwarm(self):
        pyautogui.click(self.drone_spawn_button[0], self.drone_spawn_button[1])
        sleep(0.02)
        pyautogui.click(self.drone_spawn_start[0], self.drone_spawn_start[1])
        sleep(0.02)
        self.clickAllSpells()
        self.master.after(120000, self.spawnDroneSwarm)

    def pause(self):
        #do some pause
        self.state = False if self.state == True else False

    def logPosition(self):
        # debug logging the position of the mouse
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        self.locationTxt["text"] = positionStr
        self.master.after(500, self.logPosition)


    def startLoops(self):
        # check for a flying chest
        self.findAndClickChest()
        
        # every 4 seconds try and upgrade all monsters
        self.upgradeMonsters()

        # spawn drones every 20 minutes
        self.spawnDroneSwarm()

        # click all spells every 30 seconds
        self.clickAllSpells()

        #log position every half second
        self.logPosition()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()