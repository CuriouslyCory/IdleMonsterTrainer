#import keyboard
import mss
import cv2
import numpy
from time import time, sleep
import pyautogui
import tkinter as tk
from pynput import keyboard, mouse
from random import randrange
import pickle

pyautogui.PAUSE = 0


class App(tk.Frame):
    
    # set all variables
    marks = []
    
    # should the loops be running?
    active = True

    # debug = true prints extra debug information to console
    show_debug = True;

    # get timestamp for reference
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
        "prestige_menu_btn": {"x": 1300, "y": 155},
        "prestige_trigger": {"x": 1585, "y": 865},
        "prestige_map_select": {"x": 1482, "y": 390},
        "load_monster_main_btn": {"x": 1891, "y": 152},
        "load_monster_first_btn": {"x": 1764, "y": 447},
        "tower_menu_close": {"x": 1888, "y": 930},
        "tower_menu_upgrade": {"x": 1675, "y":930},
        "drone_spawn_button": {"x": 1300, "y": 220},
        "drone_spawn_start": {"x": 1593, "y": 707},
        "chest_modal_close": {"x": 1811, "y": 356},
        "carrier_spawn_button": {"x": 1300, "y": 288},
        "carrier_spawn_start": {"x": 1595, "y": 796},
        "spell1": {"x": 1464, "y": 939},
        "spell2": {"x": 1546, "y": 939},
        "spell3": {"x": 1634, "y": 939},
        "spell4": {"x": 1739, "y": 939},
        "close_rate_modal": {"x": 1813, "y": 300},
        "close_monster_menu": {"x": 1840, "y": 158}
    }

    # maps
    maps = [
        'Enchanted Forest',
        'Snowfall',
        'Lava Cave',
        'Dead Woods',
        'Cursed Clouds',
        'Beach Run'
        ]
    map_needles = {}

    locBtns = {}

    defeats_this_prestige = 0
    defeats_before_prestige = 10
    needles = {}

    sct = mss.mss()
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.geometry('400x850')
        self.pack()
        self.createWidgets()
        self.loadNeedles()
        
        self.startLoops()
        
        
    def loadNeedles(self):
        # read the needles and get shapes
        self.chest = cv2.imread('Chest5.png', cv2.IMREAD_GRAYSCALE)
        self.chest_w = self.chest.shape[1]
        self.chest_h = self.chest.shape[0]

        self.needles['defeat'] = cv2.imread('needles/defeat.png', cv2.IMREAD_GRAYSCALE)
        self.needles['rate_me'] = cv2.imread('needles/RateMeButton.png')
        self.needles['monster_menu'] = cv2.imread('needles/MonsterMenu.png')
        self.needles['monster_details_menu'] = cv2.imread('needles/MonsterDetailsMenu.png')

    def createWidgets(self):
        self.debug("Create Widgets")

        #create buttons

        self.loadMarkersBtn = tk.Button(self)
        self.loadMarkersBtn["text"] = "Load Map Markers"
        self.loadMarkersBtn["command"] = self.loadMap
        self.loadMarkersBtn.grid(column=1, row=0)
        
        self.setMarkersBtn = tk.Button(self)
        self.setMarkersBtn["text"] = "Mark Towers"
        self.setMarkersBtn["command"] = self.markTowers
        self.setMarkersBtn.grid(column=1, row=1)

        self.loadMarkersBtn = tk.Button(self)
        self.loadMarkersBtn["text"] = "Save Map Markers"
        self.loadMarkersBtn["command"] = self.saveMap
        self.loadMarkersBtn.grid(column=1, row=2)

        self.pauseBtn = tk.Button(self)
        self.pauseBtn["text"] = "Pause"
        self.pauseBtn["command"] = self.pause
        self.pauseBtn.grid(column=1, row=3)

        for key in self.locations:
            self.locBtns[key] = tk.Button(self)
            self.locBtns[key]["text"] = "Set {} location".format(key)
            self.locBtns[key]["command"] = lambda arg1=key: self.setLoc(arg1)
            self.locBtns[key].grid(column=1)

        self.defeatLbl = tk.Label(self)
        self.defeatLbl["text"] = "0 defeats"
        self.defeatLbl.grid(column=1)

        #create debug text
        self.locationTxt = tk.Label(self)
        self.locationTxt.grid(column=1)
        
        self.chestDebug = tk.Label(self)
        self.chestDebug.grid(column=1)

        self.currentMapLbl = tk.Label(self)
        self.currentMapLbl.grid(column=1)

    def loadMap(self):
        map = self.guessMapName()
        if map:
            self.loadMapMarkers(map)

    def saveMap(self):
        map = self.guessMapName()
        if map:
            self.saveMapMarkers(map)
    
    def setLoc(self, key):
        self.debug("Location {}".format(key))
        self.updatingLocation = key
        listener = mouse.Listener(
            on_click = self.updateLocation
        )
        listener.start()

    def updateLocation(self, x, y, button, pressed):
        self.locations[self.updatingLocation][x] = x
        self.locations[self.updatingLocation][y] = y
        self.debug("{}: {},{}".format(self.updatingLocation, x, y))
        self.updatingLocation = None
        return False

    def markTowers(self):
        self.debug("Mark Towers")
        # user defined monster positions
        self.marks = []
        listener =  keyboard.Listener(
            on_press = self.on_press,
            on_release = self.markTower
        )
        listener.start()
        
    def on_press(self, key):
        self.debug("listener hears press")

    def markTower(self, key):
        if key.char == "m":
            x, y = pyautogui.position()
            self.marks.append([x, y])
            self.debug("Marks: {}, Position: {}, {}".format(len(self.marks), x, y))

        if len(self.marks) >= 10:
            return False


    # check for a flying chest
    def findAndClickChest(self):
        #self.debug("Find and Click Chest")
        if self.active == False:
            self.master.after(500, self.findAndClickChest)
            return

        result_confidence, max_loc = self.detectNeedle(self.chest, grayscale=True)
        if result_confidence > .65:
            x = max_loc[0] + self.dimensions['left'] + (self.chest_w / 2)
            y = max_loc[1] + self.dimensions['top'] + (self.chest_h /2)
            # cv2.rectangle(scr, max_loc, (max_loc[0] + self.chest_w, max_loc[1] + self.chest_h), (0,255,255), 2)
            # click chest location
            pyautogui.click(x=x, y=y)
            sleep(0.02)

            # click modal close button
            pyautogui.click(self.locations["chest_modal_close"]["x"], self.locations["chest_modal_close"]["y"])
            sleep(0.02)

        #cv2.imshow('Result', scr_remove)
        #cv2.waitKey(1)
        self.master.after(500, self.findAndClickChest)
    

    def upgradeMonsters(self, loop = True):
        #self.debug("Upgrade Monsters")
        if self.active == False and loop == True:
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
        if loop == True:
            # create a random amount of time between 3 and 5 seconds
            rand_wait = randrange(3000,5000)
            self.master.after(rand_wait, self.upgradeMonsters)


    def clickAllSpells(self, loop = True):
        self.debug("Click all spells")
        if self.active == False and loop == True:
            self.master.after(500, self.clickAllSpells)
            return
        pyautogui.click(self.locations["spell1"]["x"], self.locations["spell1"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell2"]["x"], self.locations["spell2"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell3"]["x"], self.locations["spell3"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["spell4"]["x"], self.locations["spell4"]["y"])
        if loop == True:
            self.master.after(30000, self.clickAllSpells)


    def spawnDroneSwarm(self):
        self.debug("Spawn Drone Swarm")
        if self.active == False:
            self.master.after(500, self.spawnDroneSwarm)
            return
        pyautogui.click(self.locations["drone_spawn_button"]["x"], self.locations["drone_spawn_button"]["y"])
        sleep(0.02)
        pyautogui.click(self.locations["drone_spawn_start"]["x"], self.locations["drone_spawn_start"]["y"])
        sleep(0.02)
        self.clickAllSpells(False)
        sleep(0.02)
        self.master.after(1200000, self.spawnDroneSwarm)

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
        # update screenshot
        self.updateScreenShot()

        # loadMapNeedles
        self.loadMapNeedles()

        # check for a flying chest
        self.findAndClickChest()
        
        # every 4 seconds try and upgrade all monsters
        self.upgradeMonsters()

        # spawn drones every 20 minutes
        self.spawnDroneSwarm()

        # click all spells every 30 seconds
        self.clickAllSpells()

        # log position every half second
        self.logPosition()

        # watch for the defeat screen
        self.defeatWatch()
        
        # make sure no empty tower locations are being clicked
        self.checkMonstersLoaded()

        # watch for the rate me modal and close it
        self.detectRateMe()

    def debug(self, msg):
        if self.show_debug == True:
            print(msg)

    def saveMapMarkers(self, map_name):
        with open('save/' + map_name + '.pkl', 'wb+') as f:
            pickle.dump(self.marks, f, pickle.HIGHEST_PROTOCOL)

    def loadMapMarkers(self, map_name):
        try:
            with open('save/' + map_name + '.pkl','rb') as f:
                self.marks = pickle.load(f)
        except:
            self.debug("Map not found in saves")

    def loadMapNeedles(self):
        for map in self.maps:
            # read the needles and get shapes
            try:
                self.debug("Loading needle for {}".format(map))
                self.map_needles[map] = cv2.imread("needles/" + map + ".png")
                #cv2.imshow('Result', self.map_needles[map])
                #cv2.waitKey()
            except:
                self.debug("Couldn't load needle for {}".format(map))


    def guessMapName(self):
        for key in self.map_needles:
            if self.map_needles[key] is not None:
                result_confidence, max_loc = self.detectNeedle(self.map_needles[key])
                
                if result_confidence > .80:
                    self.debug("Map is {}".format(key))
                    self.currentMapLbl["text"] = "Current Map: {}".format(key)
                    return key
                
    def triggerPrestige(self):
        # disable other loops while this is happening
        self.active = False

        # reset deaths
        self.resetDefeat()
        # click on the main menu button
        pyautogui.click(self.locations["prestige_menu_btn"]["x"], self.locations["prestige_menu_btn"]["y"])
        sleep(0.5)
        # click to accept prestige
        pyautogui.click(self.locations["prestige_trigger"]["x"], self.locations["prestige_trigger"]["y"])
        sleep(0.5)
        # select primary map rotation
        pyautogui.click(self.locations["prestige_map_select"]["x"], self.locations["prestige_map_select"]["y"])
        sleep(6)

        self.loadMonsterLayout()
        
        # reenable normal loops
        self.active = True

    def loadMonsterLayout(self):
        # open monster layout manager
        pyautogui.click(self.locations["load_monster_main_btn"]["x"], self.locations["load_monster_main_btn"]["y"])
        sleep(0.02)
        # select primary monster layout
        pyautogui.click(self.locations["load_monster_first_btn"]["x"], self.locations["load_monster_first_btn"]["y"])
        sleep(0.02)
        # load markers for tower locations
        self.loadMap()

    def updateScreenShot(self):
        scr = numpy.array(self.sct.grab(self.dimensions))
        self.scr = scr[:,:,:3]
        self.scr_gray = cv2.cvtColor(scr, cv2.COLOR_BGR2GRAY)
        self.master.after(500, self.updateScreenShot)

    def checkMonstersLoaded(self):
        if self.active == False:
            self.master.after(500, self.checkMonstersLoaded)
            return
            
        result_confidence, max_loc = self.detectNeedle(self.needles['monster_menu'])
        if result_confidence > 0.85:
            pyautogui.click(self.locations["close_monster_menu"]["x"], self.locations["close_monster_menu"]["y"])
            sleep(0.05)
            pyautogui.click(self.locations["close_monster_menu"]["x"], self.locations["close_monster_menu"]["y"])
            sleep(0.05)
            self.loadMonsterLayout()

        result_confidence, max_loc = self.detectNeedle(self.needles['monster_details_menu'])
        if result_confidence > 0.85:
            pyautogui.click(self.locations["close_monster_menu"]["x"], self.locations["close_monster_menu"]["y"])
            sleep(0.05)
            pyautogui.click(self.locations["close_monster_menu"]["x"], self.locations["close_monster_menu"]["y"])
            sleep(0.05)
            self.loadMonsterLayout()
        self.master.after(10000, self.checkMonstersLoaded)

    def detectRateMe(self):
        result_confidence, max_loc = self.detectNeedle(self.needles['rate_me'])
        if result_confidence > 0.85:
            pyautogui.click(self.locations["close_rate_modal"]["x"], self.locations["close_rate_modal"]["y"])
            sleep(0.05)

            self.loadMonsterLayout()
        self.master.after(10000, self.detectRateMe)

    def defeatWatch(self):
        # self.debug("Watch for defeat")
        
        result_confidence, max_loc = self.detectNeedle(self.needles['defeat'], grayscale=True)
        if result_confidence > .85:
            self.addDefeat()
            self.master.after(10000, self.defeatWatch)
            return

        self.master.after(500, self.defeatWatch)

    def addDefeat(self):
        self.defeats_this_prestige += 1
        self.updateDefeatLbl()
        if self.defeats_this_prestige >= self.defeats_before_prestige:
            pyautogui.click(self.locations["prestige_menu_btn"]["x"], self.locations["prestige_menu_btn"]["y"])
            self.master.after(5000, self.triggerPrestige)

    def resetDefeat(self):
        self.defeats_this_prestige = 0
        self.updateDefeatLbl()

    def updateDefeatLbl(self):
        self.defeatLbl["text"] = "{} defeats this prestige".format(self.defeats_this_prestige)

    def detectNeedle(self, needle, grayscale=False):
        if grayscale == True:
            scr = self.scr_gray
        else: 
            scr = self.scr
        
        for key in self.map_needles:
            if self.map_needles[key] is not None:
                result = cv2.matchTemplate(scr, needle, cv2.TM_CCOEFF_NORMED)
            
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                #debugStr = "Max Val: {} Max Loc: {}".format(max_val, max_loc)
                #self.debug(debugStr)
                return max_val, max_loc

if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()