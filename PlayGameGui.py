#import keyboard
import mss
import cv2
import numpy
from time import time, sleep
import pyautogui
import tkinter as tk
from pynput import keyboard, mouse

pyautogui.PAUSE = 0


class App(tk.Frame):
    
    #set all variables
    marks = []
    active = True

    #get timestamp for reference
    starttime = time()

    # define the window position and size
    dimensions = {
            'left': 1270,
            'top': 30,
            'width': 650,
            'height': 1040
        }

    # locations
    locations = {
        "tower_menu_close": {"x": 1888, "y": 930},
        "tower_menu_upgrade": {"x": 1675, "y":930},
        "drone_spawn_button": {"x": 1306, "y": 220},
        "drone_spawn_start": {"x": 1593, "y": 707},
        "chest_modal_close": {"x": 1639, "y": 350},
        "carrier_spawn_button": {"x": 1304, "y": 288},
        "carrier_spawn_start": {"x": 1595, "y": 796},
        "spell1": {"x": 1464, "y": 939},
        "spell2": {"x": 1546, "y": 939},
        "spell3": {"x": 1634, "y": 939},
        "spell4": {"x": 1739, "y": 939},
    }
    

    # read the needles and get shapes
    chest = cv2.imread('Chest5.png', cv2.IMREAD_GRAYSCALE)

    chest_w = chest.shape[1]
    chest_h = chest.shape[0]

    locBtns = {}

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

        for key in self.locations:
            self.locBtns[key] = tk.Button(self)
            self.locBtns[key]["text"] = "Set {} location".format(key)
            self.locBtns[key]["command"] = lambda arg1=key: self.setLoc(arg1)
            self.locBtns[key].grid(column=1)

    def setLoc(self, key):
        print("Location {}".format(key))
        self.updatingLocation = key
        listener = mouse.Listener(
            on_click = self.updateLocation
        )
        listener.start()

    def updateLocation(self, x, y, button, pressed):
        self.locations[self.updatingLocation][x] = x
        self.locations[self.updatingLocation][y] = y
        print("{}: {},{}".format(self.updatingLocation, x, y))
        self.updatingLocation = None
        return False

    def markTowers(self):
        # user defined monster positions
        self.marks = []
        listener =  keyboard.Listener(
            on_press = self.on_press,
            on_release = self.markTower
        )
        listener.start()
        
    def on_press(self, key):
        print("listener hears press")

    def markTower(self, key):
        if key.char == "m":
            x, y = pyautogui.position()
            self.marks.append([x, y])
            print("Marks: {}, Position: {}, {}".format(len(self.marks), x, y))

        if len(self.marks) >= 10:
            return False


    # check for a flying chest
    def findAndClickChest(self):
        if self.active == False:
            self.master.after(500, self.findAndClickChest)
            return

        scr = numpy.array(self.sct.grab(self.dimensions))
        scr_remove = cv2.cvtColor(scr, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(scr_remove, self.chest, cv2.TM_CCOEFF_NORMED)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        debugStr = "Max Val: {} Max Loc: {}".format(max_val, max_loc)
        self.chestDebug["text"] = debugStr
        src = scr.copy()
        if max_val > .65:
            x = max_loc[0] + self.dimensions['left'] + (self.chest_w / 2)
            y = max_loc[1] + self.dimensions['top'] + (self.chest_h /2)
            cv2.rectangle(scr, max_loc, (max_loc[0] + self.chest_w, max_loc[1] + self.chest_h), (0,255,255), 2)
            # click chest location
            pyautogui.click(x=x, y=y)
            sleep(0.02)

            # click modal close button
            pyautogui.click(self.locations["chest_modal_close"]["x"], self.locations["chest_modal_close"]["y"])
            sleep(0.02)

        cv2.imshow('Result', scr_remove)
        cv2.waitKey(1)
        self.master.after(500, self.findAndClickChest)
    

    def upgradeMonsters(self):
        if self.active == False:
            self.master.after(500, self.upgradeMonsters)
            return
        if(len(self.marks) > 0):
            for mark in self.marks:
                # click the monster
                pyautogui.click(mark[0], mark[1])
                sleep(0.02)
                # click the upgrade button
                pyautogui.click(self.locations["tower_menu_upgrade"]["x"], self.locations["tower_menu_upgrade"]["y"])
                sleep(0.02)
            
            # click where the flying chest close button is just in case it got hit by accident
            pyautogui.click(self.locations["chest_modal_close"]["x"], self.locations["chest_modal_close"]["y"])
            sleep(0.02)

            # close out of the tower selection
            pyautogui.click(self.locations["tower_menu_close"]["x"], self.locations["tower_menu_close"]["y"])
            sleep(0.02)
        self.master.after(4000, self.upgradeMonsters)


    def clickAllSpells(self):
        if self.active == False:
            self.master.after(500, self.clickAllSpells)
            return
        pyautogui.click(self.locations["spell1"]["x"], self.locations["spell1"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell2"]["x"], self.locations["spell2"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell3"]["x"], self.locations["spell3"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell4"]["x"], self.locations["spell4"]["y"])
        self.master.after(30000, self.clickAllSpells)


    def spawnDroneSwarm(self):
        if self.active == False:
            self.master.after(500, self.spawnDroneSwarm)
            return
        pyautogui.click(self.locations["drone_spawn_button"]["x"], self.locations["drone_spawn_button"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["drone_spawn_start"]["x"], self.locations["drone_spawn_start"]["y"])
        sleep(0.02)
        self.clickAllSpells()
        self.master.after(120000, self.spawnDroneSwarm)

    def pause(self):
        #do some pause
        self.active = False if self.active == True else True
        self.pauseBtn["text"] = "Pause" if self.active == True else "Unpause"

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