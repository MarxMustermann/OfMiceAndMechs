import src


class SiegeManager(src.items.Item):
    '''
    ingame item to control a base during sieges
    '''
    type = "SiegeManager"
    def __init__(self, name="SiegeManager", noId=False):
        super().__init__(display="SM", name=name)

        self.applyOptions.extend(
                        [
                                                                ("restrict outside", "restrict outside movement"),
                                                                ("unrestrict outside", "unrestrict outside movement"),
                                                                ("soundAlarms", "sound alarms"),
                                                                ("silenceAlarms", "silence alarms"),
                                                                ("orderMopUp", "start mop up operation"),
                                                                ("setSchedule", "set schedule"),
                        ]
                        )
        self.applyMap = {
                    "restrict outside": self.restrictOutside,
                    "unrestrict outside": self.unrestrictOutside,
                    "soundAlarms": self.soundAlarms,
                    "silenceAlarms": self.silenceAlarms,
                    "orderMopUp": self.orderMopUp,
                    "setSchedule": self.setSchedule,
                        }

        self.schedule = {}
        self.faction = None

    def setSchedule(self,character):
        '''
        open the scheduling menu
        '''
        self.scheduleLoop({"character":character})

    def scheduleLoop(self,params):
        '''
        show the scheduling menu
        '''

        # upack the parameters
        character = params["character"]

        # enforce cursor bounds
        if not "cursor" in params:
            params["cursor"] = 0
        if params["cursor"] >= len(self.schedule):
            params["cursor"] = len(self.schedule)-1
        if params["cursor"] < 0:
            params["cursor"] = 0

        # show state and get user input
        if not "action" in params:

            # draw header
            text = "schedules:\n\n"
            text+= "0" + " " * 14 + "tick"+ " " * 12 + "3375" + "\n"
            text+= "-" * 35 + "\n"
            actions_by_index = {}
            indices_by_arrow = {}
            counter = 1
            for (tick,action) in self.schedule.items():
                
                indices_by_arrow[int((tick/3375)*35)] = counter
                actions_by_index[counter] = action

                counter += 1

            # draw arrows
            for i in range(35):
                if i in indices_by_arrow:
                    text+= "^"
                else:
                    text+= " "
            text+= "\n"
            for i in range(35):
                if i in indices_by_arrow:
                    text+= "|"
                else:
                    text+= " "
            text+= "\n"

            # draw numbers
            for i in range(35):
                if i in indices_by_arrow:
                    num = indices_by_arrow[i]
                    if num > 9:
                        text = text[:-1] + str(num)
                    else:
                        text+= str(num)
                    num+= 1
                else:
                    text+= " "
            text+= "\n"
            text+= "\n"

            # draw the current planned actions
            items = list(self.schedule.items())
            items.sort(key = lambda x: x[0])
            for (i,(tick,schedule)) in enumerate(items):
                if i == params["cursor"]:
                    text += "> "
                else:
                    text += "  "
                text += str(i+1) + "- tick: "+str(tick)+" - "+str(schedule["type"])+"\n"

            # show the key available to press
            text += "\n"
            text += "\n"
            text += "press c to add new action\n"
            text += "press d to delete action\n"
            text += "press w/s to move cursor\n"
            text += "press C to clear schedule\n"
            text += "press f to set faction\n"
            text += "\n"

            # show UI and wait for user input
            submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text,targetParamName="action")
            submenue.tag = "configure siege manager main"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
            return

        # close menu if requested
        if params["action"] in ("esc","exit",None):
            return

        # move cursor
        if params["action"] == "w":
            params["cursor"] -= 1
        if params["action"] == "s":
            params["cursor"] += 1

        # show ui to schedule new items
        if params["action"] in ("c","add"):

            # get user input on what action to add
            if not "actionType" in params:
                options = []
                options.append(("restrict outside",f"restrict outside"))
                options.append(("unrestrict outside",f"unrestrict outside"))
                options.append(("sound alarms",f"sound AlarmBells"))
                options.append(("silence alarms",f"silence AlarmBells"))
                options.append(("mop up",f"start mop up operation"))
                submenue = src.menuFolder.selectionMenu.SelectionMenu("select action to schedule:\n\n",options,targetParamName="actionType")
                submenue.tag = "configure siege manager task selection"
                character.macroState["submenue"] = submenue
                character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
                return

            # abort, if requested
            if params["actionType"] == None:
                self.scheduleLoop({"character":character})
                return

            # get user input on what action to add
            if not "actionTick" in params:
                submenue = src.menuFolder.sliderMenu.SliderMenu(f'choose the tick to schedule the action "{params["actionType"]}" for:\n\n',maxValue = 3375,targetParamName="actionTick")
                character.macroState["submenue"] = submenue
                submenue.tag = "configure siege manager time selection"
                character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
                return

            # abort, on weird states
            if params["actionType"] in (""," ",None):
                self.scheduleLoop({"character":character})
                return

            # schedule the action
            tick = int(params["actionTick"])
            self.schedule[tick] = {"type":params.get("actionType")}
            character.addMessage("added schedule")

        # show the UI to delete a scheduled action
        if params["action"] in ("d","delete"):

            # get user input on what tick to clear
            if not "actionTick" in params:
                options = []
                for (key,value) in self.schedule.items():
                    options.append((key,str(key)+" - "+str(value)))
                submenue = src.menuFolder.selectionMenu.SelectionMenu("select action to delete:\n\n",options,targetParamName="actionTick")
                character.macroState["submenue"] = submenue
                character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
                return

            # abort on empty input
            if params["actionTick"] == None:
                self.scheduleLoop({"character":character})
                return

            # unschedule the action
            if params["actionTick"] in self.schedule:
                del self.schedule[params["actionTick"]]

            # show schedule main menu
            self.scheduleLoop({"character":character})
            return

        # do shedule clearing
        if params["action"] in ("C","clear"):
            self.schedule = {}

        # set faction, move to complex
        if params["action"] == ("f","faction"):
            self.faction = character.faction

        # show schedule main menu
        self.scheduleLoop({"character":character,"cursor":params["cursor"]})

    def restrictOutside(self,character=None):
        '''
        restrict the outside movement
        
        Parameters:
            character: the character triggering the this (optional)
        '''

        # set the alarm
        terrain = self.getTerrain()
        terrain.alarm = True

        # handle effect on the actor
        if character:
            character.addMessage("restricted outside")
            character.changed("did restricted outside",{})

    def unrestrictOutside(self,character=None):
        '''
        unrestrict the outside movement
        
        Parameters:
            character: the character triggering this (optional)
        '''

        # unset the alarm
        terrain = self.getTerrain()
        terrain.alarm = False

        # handle effect on the actor
        if character:
            character.addMessage("unrestricted outside")
            character.changed("did unrestricted outside",{})

    def checkCharacter(self,toCheck,faction=None):
        '''
        check if a character has a certain faction

        Parameters:
            toCheck: the character to check
            faction: the faction to check
        '''
        if faction and toCheck.faction != faction:
            return False
        return True

    def orderMopUp(self,character):
        '''
        trigger an ingame mop up operation

        Parameters:
            character: the character triggering this (optional)
        '''

        # gather all characters belonging to this base
        allCharacters = []
        terrain = self.getTerrain()
        for char in terrain.characters:
            if self.checkCharacter(char,faction=self.faction):
                allCharacters.append(char)
        for room in terrain.rooms:
            for char in room.characters:
                if self.checkCharacter(char,faction=self.faction):
                    allCharacters.append(char)

        # make each character do a mop up operation
        for char in allCharacters:
            quest = src.quests.questMap["ClearTerrain"]()
            if char != src.gamestate.gamestate.mainChar:
                quest.autoSolve = True
            char.assignQuest(quest,active=True)
            char.addMessage("you were orderd to do a mopup operation")

        # handle effect on the actor
        if character:
            character.addMessage("you orderd a mopup operation")

    def getConfigurationOptions(self, character):
        '''
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        '''
        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def soundAlarms(self,character=None):
        '''
        trigger the alarms on the base

        Parameters:
            character: the character triggering this (optional)
        '''

        # trigger the room alarms
        terrain = self.getTerrain()
        foundAlarm = False
        for room in terrain.rooms:
            if room.getItemByType("AlarmBell"):
                room.alarm = True
                foundAlarm = True

        # handle effect on the actor
        if character:
            if foundAlarm:
                character.addMessage("you sound the AlarmBells")
            else:
                character.addMessage("no AlarmBells to sound")

    def silenceAlarms(self,character=None):
        '''
        stop the alarms on the base

        Parameters:
            character: the character triggering this (optional)
        '''

        # stop the room alarms
        terrain = self.getTerrain()
        for room in terrain.rooms:
            room.alarm = False

        # handle effect on the actor
        if character:
            character.addMessage("you silence the AlarmBells")

    def handleTick(self):
        '''
        a loop to check for and trigger actions each tick
        '''

        # enforce conditions
        if not self.bolted:
            return

        # get action for that tick
        tick = src.gamestate.gamestate.tick%(15*15*15)
        event = self.schedule.get(tick)

        # run action
        if event:
            if event["type"] == "restrict outside":
                self.restrictOutside(None)
            if event["type"] == "unrestrict outside":
                self.unrestrictOutside(None)
            if event["type"] == "mop up":
                self.orderMopUp(None)
            if event["type"] == "sound alarms":
                self.soundAlarms()
            if event["type"] == "silence alarms":
                self.silenceAlarms()

        # retrigger next tick to form a loop
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1)
        event.setCallback({"container": self, "method": "handleTick"})
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addEvent(event)

    def boltAction(self,character=None):
        '''
        bolt down the item

        Parameters:
            character: the character triggering this (optional)
        '''

        # bolt down
        self.bolted = True

        # handle effect on the actor
        if character:
            character.addMessage("you bolt down the ScrapCompactor")
            character.changed("boltedItem",{"character":character,"item":self})

        # trigger side effects
        self.numUsed = 0
        self.handleTick()

    def unboltAction(self,character=None):
        '''
        unbolt the item

        Parameters:
            character: the character triggering this (optional)
        '''

        # unbolt 
        self.bolted = False

        # handle effect on the actor
        if character:
            character.addMessage("you unbolt the ScrapCompactor")
            character.changed("unboltedItem",{"character":character,"item":self})

        # trigger side effects
        self.numUsed = 0

# register the item
src.items.addType(SiegeManager)
