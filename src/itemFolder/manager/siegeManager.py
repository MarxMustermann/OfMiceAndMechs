import src


class SiegeManager(src.items.Item):
    """
    """


    type = "SiegeManager"

    def __init__(self, name="SiegeManager", noId=False):
        """
        set up the initial state
        """

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
        self.scheduleLoop({"character":character})

    def scheduleLoop(self,params):
        character = params["character"]

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

        items = list(self.schedule.items())
        items.sort(key = lambda x: x[0])
        for (i,(tick,schedule)) in enumerate(items):
            text += str(i+1) + "- tick: "+str(tick)+" - "+str(schedule["type"])+"\n"
        text += "\n"

        if not "action" in params:
            options = []
            index = 0
            options.append(("exit",f"close schedule"))
            options.append(("add",f"schedule action"))
            options.append(("delete",f"delete action"))
            options.append(("clear",f"clear schedule"))
            options.append(("faction",f"set faction"))
            submenue = src.menuFolder.selectionMenu.SelectionMenu(text,options,targetParamName="action")
            submenue.tag = "configure siege manager main"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
            return

        if params["action"] in ("exit",None):
            return

        if params["action"] == "add":
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

            if params["actionType"] == None:
                self.scheduleLoop({"character":character})
                return

            if not "actionTick" in params:
                submenue = src.menuFolder.sliderMenu.SliderMenu(f'choose the tick to schedule the action "{params["actionType"]}" for:\n\n',maxValue = 3375,targetParamName="actionTick")
                character.macroState["submenue"] = submenue
                submenue.tag = "configure siege manager time selection"
                character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
                return

            if params["actionType"] in (""," ",None):
                self.scheduleLoop({"character":character})
                return

            tick = int(params["actionTick"])

            self.schedule[tick] = {"type":params.get("actionType")}
            character.addMessage("added schedule")

        if params["action"] == "delete":
            if not "actionTick" in params:
                options = []
                for (key,value) in self.schedule.items():
                    options.append((key,str(key)+" - "+str(value)))
                submenue = src.menuFolder.selectionMenu.SelectionMenu("select action to delete:\n\n",options,targetParamName="actionTick")
                character.macroState["submenue"] = submenue
                character.macroState["submenue"].followUp = {"container":self,"method":"scheduleLoop","params":params}
                return

            if params["actionTick"] == None:
                self.scheduleLoop({"character":character})
                return

            if params["actionTick"] in self.schedule:
                del self.schedule[params["actionTick"]]

            self.scheduleLoop({"character":character})
            return

        if params["action"] == "clear":
            self.schedule = {}

        if params["action"] == "faction":
            self.faction = character.faction

        character.addMessage("set schedule")

        self.scheduleLoop({"character":character})

    def orderHunkerDown(self,character):
        #removeme
        pass
        terrain = self.getTerrain()

    def restrictOutside(self,character=None):
        terrain = self.getTerrain()
        terrain.alarm = True
        if character:
            character.addMessage("restricted outside")
            character.changed("did restricted outside",{})

    def unrestrictOutside(self,character=None):
        terrain = self.getTerrain()
        terrain.alarm = False
        if character:
            character.addMessage("unrestricted outside")
            character.changed("did unrestricted outside",{})

    def checkCharacter(self,toCheck,faction=None):
        if faction and toCheck.faction != faction:
            return False
        return True

    def orderMopUp(self,character):

        allCharacters = []
        terrain = self.getTerrain()
        for char in terrain.characters:
            if self.checkCharacter(char,faction=self.faction):
                allCharacters.append(char)
        for room in terrain.rooms:
            for char in room.characters:
                if self.checkCharacter(char,faction=self.faction):
                    allCharacters.append(char)

        for char in allCharacters:
            quest = src.quests.questMap["ClearTerrain"]()
            if char != src.gamestate.gamestate.mainChar:
                quest.autoSolve = True
            char.assignQuest(quest,active=True)
            char.addMessage("you were orderd to do a mopup operation")

        if character:
            character.addMessage("you orderd a mopup operation")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def soundAlarms(self,character=None):
        terrain = self.getTerrain()

        foundAlarm = False
        for room in terrain.rooms:
            if room.getItemByType("AlarmBell"):
                room.alarm = True
                foundAlarm = True

        if character:
            if foundAlarm:
                character.addMessage("you sound the AlarmBells")
            else:
                character.addMessage("no AlarmBells to sound")

    def silenceAlarms(self,character=None):
        terrain = self.getTerrain()

        for room in terrain.rooms:
            room.alarm = False
        if character:
            character.addMessage("you silence the AlarmBells")

    def handleTick(self):
        if not self.bolted:
            return

        tick = src.gamestate.gamestate.tick%(15*15*15)
        event = self.schedule.get(tick)
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

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1)
        event.setCallback({"container": self, "method": "handleTick"})
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addEvent(event)

    def boltAction(self,character=None):
        self.bolted = True
        if character:
            character.addMessage("you bolt down the ScrapCompactor")
            character.changed("boltedItem",{"character":character,"item":self})
        self.numUsed = 0
        self.handleTick()

    def unboltAction(self,character=None):
        self.bolted = False
        if character:
            character.addMessage("you unbolt the ScrapCompactor")
            character.changed("unboltedItem",{"character":character,"item":self})
        self.numUsed = 0


src.items.addType(SiegeManager)
