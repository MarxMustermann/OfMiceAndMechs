import src


class SiegeManager(src.items.Item):
    '''
    ingame item to control a base during sieges
    '''
    type = "SiegeManager"
    def __init__(self, name="SiegeManager"):
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

    def getActionList(self):
        '''
        get an ordered list of scheduled actions
        '''
        actionList = []
        items = list(self.schedule.items())
        items.sort(key = lambda x: x[0])
        counter = 0
        for (i,(tick,tickList)) in enumerate(items):
            for action in tickList:
                actionList.append((counter,tick,action))
                counter += 1
        return actionList

    def scheduleLoop(self,params):
        '''
        show the scheduling menu
        '''

        # upack the parameters
        character = params["character"]

        # enforce cursor bounds
        if not "cursor" in params:
            params["cursor"] = 0
        if params["cursor"] >= len(self.getActionList()):
            params["cursor"] = len(self.getActionList())-1
        if params["cursor"] < 0:
            params["cursor"] = 0

        # show state and get user input
        if not "action" in params:

            # draw header
            text = []
            text.append("schedules:\n\n")
            text.append("0" + " " * 14 + "tick"+ " " * 12 + "3375" + "\n")
            actions_by_index = {}
            indices_by_arrow = {}
            for scheduledAction in self.getActionList():
                arrowNumber = int((scheduledAction[1]/3375)*35)
                if not arrowNumber in indices_by_arrow:
                    indices_by_arrow[arrowNumber] = []

                indices_by_arrow[arrowNumber].append(scheduledAction[0])
                actions_by_index[scheduledAction[0]] = scheduledAction[2]

            # draw line
            for i in range(35):
                if i in indices_by_arrow:
                    # mark selected arrow
                    color = "#aab"
                    for index in indices_by_arrow[i]:
                        if index == params["cursor"]:
                            color = "#fff"
                    text.append((src.interaction.urwid.AttrSpec(color, "default"), "+"))
                else:
                    text.append((src.interaction.urwid.AttrSpec("#aab", "default"), "-"))
            text.append("\n")

            # draw arrows
            for i in range(35):
                if i in indices_by_arrow:
                    # mark selected arrow
                    color = "#aab"
                    for index in indices_by_arrow[i]:
                        if index == params["cursor"]:
                            color = "#fff"
                    text.append((src.interaction.urwid.AttrSpec(color, "default"), "^"))
                else:
                    text.append(" ")
            text+= "\n"
            for i in range(35):
                if i in indices_by_arrow:
                    # mark selected arrow
                    color = "#aab"
                    for index in indices_by_arrow[i]:
                        if index == params["cursor"]:
                            color = "#fff"
                    text.append((src.interaction.urwid.AttrSpec(color, "default"), "|"))
                else:
                    text+= " "
            text+= "\n"

            # draw numbers
            for i in range(35):
                if i in indices_by_arrow:
                    # mark selected number
                    color = "#aab"
                    for index in indices_by_arrow[i]:
                        if index == params["cursor"]:
                            color = "#fff"

                    # draw number
                    num = indices_by_arrow[i][0]
                    if num > 9:
                        numRender = str(num+1)[-1]
                    else:
                        numRender = str(num+1)
                    text.append((src.interaction.urwid.AttrSpec(color, "default"), numRender))
                else:
                    text.append(" ")
            text.append("\n")
            text.append("\n")

            # draw the current planned actions
            for scheduledAction in self.getActionList():
                # draw the action
                line = ""
                if scheduledAction[0] == params["cursor"]:
                    line += "> "
                    color = "#fff"
                else:
                    line += "  "
                    color = "#bbc"
                line += str(scheduledAction[0]+1) + "- tick: "+str(scheduledAction[1])+" - "+str(scheduledAction[2]["type"])+"\n"

                text.append((src.interaction.urwid.AttrSpec(color, "default"), line))

            # show the key available to press
            text.append("\n")
            text.append("\n")
            text.append("press w/s to move cursor by 1\n")
            text.append("press r to delete selected action\n")
            text.append("press a/d to move selected action by 1\n")
            text.append("press q/e to move selected action by 10\n")
            text.append("press Q/E to move selected action by 100\n")
            text.append("press A/D to move selected action by 250\n")
            text.append("\n")
            text.append("press c to add new action\n")
            text.append("press C to clear schedule\n")
            text.append("press f to set faction\n")
            text.append("\n")

            # show UI and wait for user input
            submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu([text],targetParamName="action")
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

        # move the selected action
        if params["action"] in ("a","d","A","D","q","e","Q","E"):
            # fetch action to move
            scheduledAction = self.getActionList()[params["cursor"]]

            # remove the action from the old spot
            self.schedule[scheduledAction[1]].remove(scheduledAction[2])
            if not self.schedule[scheduledAction[1]]:
                del self.schedule[scheduledAction[1]]

            # apply the tick change
            tick = scheduledAction[1]
            if params["action"] == "a":
                offset = -1
            if params["action"] == "d":
                offset = 1
            if params["action"] == "q":
                offset = -10
            if params["action"] == "e":
                offset = 10
            if params["action"] == "Q":
                offset = -100
            if params["action"] == "E":
                offset = 100
            if params["action"] == "A":
                offset = -250
            if params["action"] == "D":
                offset = 250
            tick += offset
            if tick < 0:
                tick = 15*15*15+tick
            if tick > 15*15*15:
                tick = tick-(15*15*15)

            # readd the action to the new slot
            if not tick in self.schedule:
                self.schedule[tick] = []
            self.schedule[tick].append(scheduledAction[2])

            # set cursor to inserted action
            counter = 0
            for checkScheduledAction in self.getActionList():
                if checkScheduledAction[2] != scheduledAction[2]:
                    counter += 1
                    continue
                params["cursor"] = counter
                break
            
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

            # assume ticks for actions
            if params["actionType"] == "unrestrict outside":
                params["actionTick"] = 1000
            if params["actionType"] == "silence alarms":
                params["actionTick"] = 1000
            if params["actionType"] == "mop up":
                params["actionTick"] = 1200
            if params["actionType"] == "restrict outside":
                params["actionTick"] = 2500
            if params["actionType"] == "sound alarms":
                params["actionTick"] = 2500

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
            if not tick in self.schedule:
                self.schedule[tick] = []
            action = {"type":params.get("actionType")}
            self.schedule[tick].append(action)
            character.addMessage("added schedule")

            # set cursor to inserted action
            counter = 0
            for scheduledAction in self.getActionList():
                if scheduledAction[2] != action:
                    counter += 1
                    continue
                params["cursor"] = counter
                break

        # delete the scheduled action
        if params["action"] in ("r","delete"):

            # delete action
            for scheduledAction in self.getActionList():
                if params["cursor"] != scheduledAction[0]:
                    continue
                self.schedule[scheduledAction[1]].remove(scheduledAction[2])
                if not self.schedule[scheduledAction[1]]:
                    del self.schedule[scheduledAction[1]]
                break

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
        actions = self.schedule.get(tick)
        
        # run action
        if actions:
            for event in actions:
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
