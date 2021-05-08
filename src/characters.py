########################################################################################################
###
##     the code for the characters belongs here
#
########################################################################################################

# import basic libs
import json

# import the other internal libs
import src.items
import src.saveing
import src.quests
import src.chats
import config
import random

# bad code: containers for global state
characters = None
calculatePath = None
roomsOnMap = None

"""
this is the class for characters meaning both npc and pcs. 
all characters except the pcs always have automated = True to
make them to things on their own
"""
class Character(src.saveing.Saveable):
    charType = "Character"

    def setDefaultMacroState(self):
        import time
        self.macroState = {
            "commandKeyQueue":[],
            "state":[],
            "recording":False,
            "recordingTo":None,
            "replay":[],
            "loop":[],
            "number":None,
            "doNumber":False,
            "macros":{},
            "shownStarvationWarning":False,
            "lastLagDetection":time.time(),
            "lastRedraw":time.time(),
            "idleCounter":0,
            "ignoreNextAutomated": False,
            "ticksSinceDeath": None,
            "footerPosition":0,
            #"footerLength":len(footerText),
            "footerSkipCounter":20,
            "itemMarkedLast":None,
            "lastMoveAutomated":False,
            "stealKey":{},
            "submenue":None,
                }

    '''
    sets basic info AND adds default behaviour/items
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,quests=[],automated=True,name=None,creator=None,characterId=None,seed=None):
        super().__init__()

        if name == None and seed:
            name = config.names.characterFirstNames[(seed)%len(config.names.characterFirstNames)]+" "+config.names.characterLastNames[(seed*10)%len(config.names.characterLastNames)]

        if display == None and not name == None:
            display = displayChars.staffCharactersByLetter[name[0].lower()]

        if name == None:
            name = "Person"
        if display == None:
            display = displayChars.staffCharacters[0]

        self.setDefaultMacroState()

        self.macroStateBackup = None

        # set basic state
        self.specialRender = False
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = {"default":[]}
        self.path = []
        self.subordinates = []
        self.reputation = 0
        self.events = []
        self.room = None
        self.terrain = None
        self.xPosition = 0
        self.yPosition = 0
        self.zPosition = 0
        self.satiation = 1000
        self.dead = False
        self.deathReason = None
        self.questsToDelegate = []
        self.unconcious = False
        self.displayOriginal = display
        self.isMilitary = False
        self.hasFloorPermit = True
        # bad code: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []
        self.questsDone = []
        self.solvers = ["NaiveDropQuest"]
        self.aliances = []
        self.stasis = False
        self.registers = {}
        self.doStackPop = False
        self.doStackPush = False
        self.timeTaken = 0
        self.personality = {}
        self.lastRoom = None
        self.lastTerrain = None
        self.health = 100
        self.heatResistance = 0
        self.godMode = False
        self.submenue = None
        self.jobOrders = []

        self.frustration = 0
        self.aggro = 0
        self.numAttackedWithoutResponse = 0

        self.weapon = None
        self.armor = None
        self.combatMode = None

        self.interactionState = {}
        self.interactionStateBackup = []

        self.baseDamage = 2
        self.randomBonus = 2
        self.bonusMultiplier = 1
        self.staggered = 0
        self.staggerResistant = False

        self.lastJobOrder = ""

        # generate the id for this object
        if characterId:
            self.id = characterId
        else:
            import uuid
            self.id = uuid.uuid4().hex

        # mark attributes for saving
        self.attributesToStore.extend([
               "gotBasicSchooling","gotMovementSchooling","gotInteractionSchooling","gotExamineSchooling",
               "xPosition","yPosition","zPosition","name","satiation","unconcious","reputation","tutorialStart",
               "isMilitary","hasFloorPermit","dead","deathReason","automated","watched","solvers","questsDone",
               "stasis","registers","doStackPop","doStackPush","timeTaken","personality","health","heatResistance","godMode","frustration",
               "combatMode","numAttackedWithoutResponse","baseDamage","randomBonus","bonusMultiplier","staggered",
               "staggerResistant","lastJobOrder",])
        self.objectsToStore.append("serveQuest")
        self.objectsToStore.append("room")

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False
        self.faction = "player"

        import random
        self.personality["idleWaitTime"] = random.randint(2,100)
        self.personality["idleWaitChance"] = random.randint(2,10)
        self.personality["frustrationTolerance"] = random.randint(-5000,5000)
        self.personality["autoCounterAttack"] = True
        self.personality["abortMacrosOnAttack"] = True
        self.personality["autoFlee"] = True
        self.personality["autoAttackOnCombatSuccess"] = 0
        self.personality["annoyenceByNpcCollisions"] = random.randint(50,150)
        self.personality["attacksEnemiesOnContact"] = True

        self.silent = False

        self.messages = []

        self.xPosition = xPosition
        self.yPosition = yPosition

    def addMessage(self,message):
        self.messages.append(message)

    def runCommandString(self,commandString):
        convertedCommand = []
        for char in commandString:
            convertedCommand.append((char,"norecord"))

        self.macroState["commandKeyQueue"] = convertedCommand + self.macroState["commandKeyQueue"]

    def addJobOrder(self,jobOrder):
        self.jobOrders.append(jobOrder)
        self.runCommandString("Jj.j")

    def clearCommandString(self):
        self.macroState["commandKeyQueue"] = []

    def hurt(self,damage, reason = None):
        if reason == "attacked":
            if self.aggro < 20:
                self.aggro += 5
            if self.personality.get("abortMacrosOnAttack"):
                self.clearCommandString()
            if self.personality.get("autoCounterAttack"):
                self.runCommandString("m")
            if self.personality.get("autoRun"):
                self.runCommandString(random.choice(["a","w","s","d"]))

            self.numAttackedWithoutResponse += 1
            damage += self.numAttackedWithoutResponse

        if self.armor:
            damageAbsorbtion = self.armor.getArmorValue(reason)

            if self.combatMode == "defensive":
                damageAbsorbtion += 2
                self.addMessage("passive combat bonus")

            self.addMessage("your armor absorbs %s damage"%(damageAbsorbtion,))
            damage -= damageAbsorbtion

        if damage <= 0:
            return

        if self.health-damage > 0:
            staggerThreshold = self.health//4+1

            self.health -= damage
            self.frustration += 10*damage
            self.addMessage("you took "+str(damage)+" damage")

            if self.combatMode == "defensive":
                staggerThreshold *= 2
            if damage > staggerThreshold:
                self.addMessage("you stager")
                self.staggered += damage//staggerThreshold

            if reason:
                self.addMessage("reason: %s"%(reason,))
        else:
           self.health = 0
           self.die(reason="you died from injuries")

    def attack(self,target):
        if self.numAttackedWithoutResponse > 2:
            self.numAttackedWithoutResponse -= 2
        else:
            self.numAttackedWithoutResponse = 0

        baseDamage = self.baseDamage
        randomBonus = self.randomBonus
        bonusMultiplier = self.bonusMultiplier

        if self.weapon:
            baseDamage = 6
            randomBonus = 7

        if self.combatMode == "agressive":
            bonusMultiplier += 2

        damage = baseDamage+random.randint(0,randomBonus)*bonusMultiplier
        target.hurt(damage,reason="attacked")
        self.addMessage("you attack the enemy for %s damage, the enemy has %s health left"%(damage,target.health))

        if self.personality.get("autoAttackOnCombatSuccess"):
            self.runCommandString("m"*self.personality.get("autoAttackOnCombatSuccess"))
            self.addMessage("auto attack")

    def heal(self, amount, reason = None):
        if 100-self.health < amount:
            amount = 100-self.health

        self.health += amount
        self.addMessage("you heal for %s and have %s health"%(amount,self.health))

    def collidedWith(self,other):
        if not other.faction == self.faction:
            if self.personality.get("attacksEnemiesOnContact"):
                self.runCommandString("m")
        else:
            if self.personality.get("annoyenceByNpcCollisions"):
                self.frustration += self.personality.get("annoyenceByNpcCollisions")

    def getRegisterValue(self,key):
        try:
            return self.registers[key][-1]
        except KeyError:
            return None

    def setRegisterValue(self,key,value):
        if not key in self.registers:
            self.registers[key] = [0]
        self.registers[key][-1] = value

    """
    proxy render method to display attribute
    """
    @property
    def display(self):
        return self.render()

    """
    render the character
    """
    def render(self):
        if self.unconcious:
            return displayChars.unconciousBody
        else:
            return self.displayOriginal

    """
    the object the character is in. Either room or terrain
    """
    @property
    def container(self):
        if self.room:
            return self.room
        else:
            return self.terrain

    '''
    get a quest from the character (proxies room quest queue)
    '''
    def getQuest(self):
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    '''
    almost straightforward adding of events to the characters event queue
    ensures that the events are added in proper order
    '''
    def addEvent(self,event):
        # get the position for this event
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1

        # add event at proper position
        self.events.insert(index,event)

    '''
    reset the path to the current quest
    bad code: is only needed because path is contained in character instead of quest
    '''
    def recalculatePath(self):
        # log impossible state
        if not self.quests:
            debugMessages.append("reacalculate path called without quests")
            self.path = []
            return

        # reset path
        self.setPathToQuest(self.quests[0])

    '''
    straightforward removing of events from the characters event queue
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    almost straightforward getter for chat options
    # bad code: adds default chat options
    '''
    def getChatOptions(self,partner):
        # get the usual chat options
        chatOptions = self.basicChatOptions[:]

        if not self.silent:
            # add chat for recruitment
            if not self in partner.subordinates:
                chatOptions.append(src.chats.RecruitChat)
                pass
            if not partner in self.subordinates:
                chatOptions.append({"dialogName":"may i serve you?","chat":chats.RoomDutyChat,"params":{
                "superior":self
                }})
            else:
                chatOptions.append({"dialogName":"can i do something for you?","chat":chats.RoomDutyChat2,"params":{
                "superior":self
                }})
            if self.isMilitary:
                chatOptions.append({"dialogName":"I want to join the military","chat":chats.JoinMilitaryChat,"params":{
                "superior":self
                }})

        return chatOptions

    '''
    getter for the players state
    '''
    def getState(self):
        # fetch base state

        state = super().getState()

        import copy
        state["macroState"] = copy.deepcopy(self.macroState)
        if not state["macroState"]["itemMarkedLast"] == None and not isinstance(state["macroState"]["itemMarkedLast"],str):
            state["macroState"]["itemMarkedLast"] = state["macroState"]["itemMarkedLast"].id
        if "submenue" in state["macroState"] and state["macroState"]["submenue"]:
            state["macroState"]["submenue"] = state["macroState"]["submenue"].getState()

        state["registers"] = self.registers

        # add simple structures
        state.update({ 
                 "inventory": {},
                 "quests": {},
                 "path":self.path,
               })
                 
        # store inventory
        inventoryIds = []
        inventoryStates = {}
        for item in self.inventory:
            inventoryIds.append(item.id)
            inventoryStates[item.id] = item.getState()
        state["inventory"]["inventoryIds"] = inventoryIds
        state["inventory"]["states"] = inventoryStates

        # store quests
        questIds = []
        questStates = {}
        for quest in self.quests:
            questIds.append(quest.id)
            questStates[quest.id] = quest.getState()
        state["quests"]["questIds"] = questIds
        state["quests"]["states"] = questStates

        # store events
        eventIds = []
        eventStates = {}
        for event in self.events:
            eventIds.append(event.id)
            eventStates[event.id] = event.getState()
        state["eventIds"] = eventIds
        state["eventStates"] = eventStates
        
        # store serve quest
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    chatOptions.append(option)
        state["chatOptions"] = chatOptions

        state["type"] = self.charType

        # store submenue
        if self.submenue == None:
            state["submenue"] = self.submenue
        else:
            state["submenue"] = self.submenue.getState()

        jobOrderState = []
        for jobOrder in self.jobOrders:
           jobOrderState.append(jobOrder.getState()) 
        state["jobOrders"] = jobOrderState

        return state

    '''
    setter for the players state
    '''
    def setState(self,state):
        # set basic state
        super().setState(state)

        if "personality" in state:
            personality = state["personality"]
            if not "idleWaitTime" in personality:
                self.personality["idleWaitTime"] = 10
            if not "idleWaitChance" in personality:
                self.personality["idleWaitChance"] = 3
            if not "frustrationTolerance" in personality:
                self.personality["frustrationTolerance"] = 0
            if not "autoCounterAttack" in personality:
                self.personality["autoCounterAttack"] = True
            if not "autoFlee" in personality:
                self.personality["autoFlee"] = True
            if not "abortMacrosOnAttack" in personality:
                self.personality["abortMacrosOnAttack"] = True
            if not "annoyenceByNpcCollisions" in personality:
                self.personality["annoyenceByNpcCollisions"] = True
            if not "autoAttackOnCombatSuccess" in personality:
                self.personality["autoAttackOnCombatSuccess"] = 0
            if not "attacksEnemiesOnContact" in personality:
                self.personality["attacksEnemiesOnContact"] = True


        if not "loop" in state["macroState"]:
            state["macroState"]["loop"] = []

        self.macroState = state["macroState"]

        if not self.macroState["itemMarkedLast"] == None:
            def setParam(instance):
                self.macroState["itemMarkedLast"] = instance
            loadingRegistry.callWhenAvailable(self.macroState["itemMarkedLast"],setParam)
        if "submenue" in self.macroState and self.macroState["submenue"]:
            self.macroState["submenue"] =  src.interaction.getSubmenuFromState(self.macroState["submenue"])

        if "registers" in state:
            self.registers = state["registers"]

        # set unconcious state
        if "unconcious" in state:
            if self.unconcious:
                self.fallUnconcious()

        # set path
        if "path" in state:
            self.path = state["path"]
        
        # set inventory
        if "inventory" in state:
            if "inventoryIds" in state["inventory"]:
                for inventoryId in state["inventory"]["inventoryIds"]:
                    item = src.items.getItemFromState(state["inventory"]["states"][inventoryId])
                    self.inventory.append(item)
            else:
                self.loadFromList(state["inventory"],self.inventory,src.items.getItemFromState)

        # set quests
        if "quests" in state:

            # deactivate the quest that will be removed later
            if "removed" in state["quests"]:
                for quest in self.quests[:]:
                    if quest.id in state["quests"]["removed"]:
                        quest.deactivate()
                        quest.completed = True
                
            # load quests using the saving class
            self.loadFromList(state["quests"],self.quests,src.quests.getQuestFromState)

            # load a fixed set of quests
            if "questIds" in state["quests"]:

                # tear down current quests
                for quest in self.quests[:]:
                    quest.deactivate()
                    quest.completed = True
                    self.quests.remove(quest)

                # add new quests
                for questId in state["quests"]["questIds"]:
                    quest = src.quests.getQuestFromState(state["quests"]["states"][questId])
                    self.quests.append(quest)

        # set chat options
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                if not isinstance(chatType,dict):
                    chatOptions.append(chats.chatMap[chatType])
                else:
                    option = {}
                    option["chat"] = chats.chatMap[chatType["chat"]]
                    option["dialogName"] = chatType["dialogName"]
                    if "params" in chatType:
                        params = {}
                        for (key,value) in chatType["params"].items():
                            '''
                            set value
                            '''
                            def setParam(instance):
                                params[key] = instance
                            loadingRegistry.callWhenAvailable(value,setParam)
                        option["params"] = params
                    chatOptions.append(option)
            self.basicChatOptions = chatOptions

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        if "submenue" in state:
            if state["submenue"] == None:
                self.submenue = state["submenue"]
            else:
                self.submenue = src.interaction.getSubmenuFromState(state["submenue"])

        self.jobOrders = []
        if "jobOrders" in state:
            for jobOrder in state["jobOrders"]:
               self.jobOrders.append(src.items.getItemFromState(jobOrder))

        if not "frustrationTolerance" in self.personality:
            self.personality["frustrationTolerance"] = 0

        return state

    def awardReputation(self,amount=0,fraction=0, reason=None):
        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation//fraction
        self.reputation += totalAmount
        if self.watched:
            text = "you were rewarded %i reputation"%totalAmount
            if reason:
                text += " for "+reason
            self.addMessage(text)

    def revokeReputation(self,amount=0,fraction=0, reason=None):
        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation//fraction
        self.reputation -= totalAmount
        if self.watched:
            text = "you lost %i reputation"%totalAmount
            if reason:
                text += " for "+reason
            self.addMessage(text)

    '''
    starts the next quest in the quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def startNextQuest(self):
        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                debugMessages.append("setting path to quest failed")
                pass

    '''
    straightforward getting a string with detailed info about the character
    '''
    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoordinate: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubordinates: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)+"\ntick: "+str(gamestate.tick)+"\nfaction: "+str(self.faction)

    '''
    adds a quest to the characters quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def assignQuest(self,quest,active=False):
            if active:
                self.quests.insert(0,quest)
            else:
                self.quests.append(quest)
            quest.assignToCharacter(self)
            quest.activate()
            if (active or len(self.quests) == 1):
                try:
                    if self.quests[0] == quest:
                        self.setPathToQuest(quest)
                except:
                    # bad pattern: exceptions should be logged
                    pass

    '''
    set the path to a quest
    bad pattern: path should be determined by a quests solver
    bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    '''
    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY") and self.container:
            self.path = self.container.findPath((self.xPosition,self.yPosition),(quest.dstX,quest.dstY))
        else:
            self.path = []

    '''
    straightforward adding to inventory
    '''
    def addToInventory(self,item):
        self.inventory.append(item)

    '''
    this wrapper converts a character centered call to a solver centered call
    bad code: should be handled in quest
    '''
    def applysolver(self,solver):
        if not self.unconcious and not self.dead:
            solver(self)

    '''
    set state and display to unconcious
    '''
    def fallUnconcious(self):
        self.unconcious = True
        if self.watched:
            self.addMessage("*thump,snort*")
        self.changed("fallen unconcious",self)

    '''
    set state and display to not unconcious
    '''
    def wakeUp(self):
        self.unconcious = False
        if self.watched:
            self.addMessage("*grown*")
        self.changed("woke up",self)

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None,addCorpse=True):
        self.lastRoom = self.room
        self.lastTerrain = self.terrain

        # replace character with corpse
        if self.container:
            container = self.container
            container.removeCharacter(self)
            if addCorpse:
                corpse = src.items.Corpse(self.xPosition,self.yPosition,creator=self)
                container.addItems([corpse])
        # log impossible state
        else:
            debugMessages.append("this should not happen, character died without beeing somewhere ("+str(self)+")")

        self.macroState["commandKeyQueue"] = []

        # set attributes
        self.addMessage("you died.")
        self.dead = True
        if reason:
            self.deathReason = reason
            self.addMessage("cause of death: %s"%(reason,))
        self.path = []

        # notify listeners
        self.changed("died",{"character":self,"reason":reason})

        # notify listeners
        self.changed()

    '''
    walk the predetermined path
    return:
        True when done
        False when not done

    bad pattern: should be contained in quest solver
    '''
    def walkPath(self):
        # smooth over impossible state
        if self.dead:
            debugMessages.append("dead men walking")
            return
        if not self.path:
            self.setPathToQuest(self.quests[0])
            debugMessages.append("walking without path")

        # move along the predetermined path
        currentPosition = (self.xPosition,self.yPosition)
        if not (self.path and not self.path == [currentPosition]):
            return True

        # get next step
        nextPosition = self.path[0]

        item = None
        # try to move within a room
        if self.room:
            # move naively within a room
            if (nextPosition[0] == currentPosition[0] and nextPosition[1] == currentPosition[1]-1):
                item = self.room.moveCharacterDirection(self,"north")
            if (nextPosition[0] == currentPosition[0] and nextPosition[1] == currentPosition[1]+1):
                item = self.room.moveCharacterDirection(self,"south")
            elif nextPosition[0] == currentPosition[0]-1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"west")
            elif nextPosition[0] == currentPosition[0]+1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"east")
            else:
                # smooth over impossible state
                if not debug:
                    # resorting to teleport
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                    self.changed()
                else:
                    debugMessages.append("character moved on non continious path")
        # try to move within a terrain
        else:
            # check if a room was entered
            # basically checks if a walkable space/door is within a room on the coordinate the character walks on. If there is something in the way, an item it will be saved for interaction.
            # bad pattern: collision detection and room teleportation should be done in terrain

            for room in self.terrain.rooms:
                """
                helper function to move a character into a direction
                """
                def moveCharacter(localisedEntry,direction):
                    if localisedEntry in room.walkingAccess:

                        # check whether the character walked into something
                        if localisedEntry in room.itemByCoordinates:
                            for listItem in room.itemByCoordinates[localisedEntry]:
                                if not listItem.walkable:
                                    return listItem

                        # teleport the chracter into the room
                        room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                        self.terrain.characters.remove(self)
                        self.terrain = None
                        self.changed()
                        return
                    else:
                        # show message the character bumped into a wall
                        # bad pattern: why restrict the player to standard entry points?
                        self.addMessage("you cannot move there ("+direction+")")
                        return

                # handle the character moving into the rooms boundaries
                # bad code: repetitive, confusing code
                # check north
                if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        # try to move character
                        localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                        item = moveCharacter(localisedEntry,"north")
                        break
                # check south
                if room.yPosition*15+room.offsetY == nextPosition[1]:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        # try to move character
                        localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                        item = moveCharacter(localisedEntry,"south")
                        break
                # check east
                if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        # try to move character
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"east")
                        break
                # check west
                if room.xPosition*15+room.offsetX == nextPosition[0]:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        # try to move character
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"west")
                        break
            else:
                # move the char to the next position on path
                self.xPosition = nextPosition[0]
                self.yPosition = nextPosition[1]
                self.changed()
            
        # handle bumping into an item
        if item:
            # open doors
            # bad pattern: this should not happen here
            if isinstance(item,src.items.Door):
                item.apply(self)
            return False

        # smooth over impossible state
        else:
            if not debug:
                if not self.path or not nextPosition == self.path[0]:
                    return False

            # remove last step from path
            if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
                self.path = self.path[1:]
        return False

    """
    almost straightforward dropping of items
    """
    def drop(self,item,position=None):
        foundScrap = None

        if not position:
            position = (self.xPosition,self.yPosition,self.zPosition)

        itemList = self.container.getItemByPosition(position)

        if item.walkable == False and len(itemList):
            self.addMessage("you need a clear space to drop big items")
            return

        foundBig = False

        for compareItem in itemList:
            if compareItem.type == "Scrap":
                foundScrap = compareItem
            if compareItem.walkable == False and not (compareItem.type == "Scrap" and compareItem.amount < 15):
                foundBig = True
                break

        if foundBig:
            self.addMessage("there is no space to drop the item")
            return

        self.addMessage("you drop a %s"%(item.type))

        # remove item from inventory
        self.inventory.remove(item)

        if foundScrap and item.type == "Scrap":
            foundScrap.amount += item.amount
            foundScrap.setWalkable()
        else:
            # add item to floor
            item.xPosition = position[0]
            item.yPosition = position[1]
            item.zPosition = position[2]
            self.container.addItems([item])

        self.changed()

    """
    examine an item
    """
    def examine(self,item):
        registerInfo = ""
        for (key,value) in item.fetchSpecialRegisterInformation().items():
            self.setRegisterValue(key,value)
            registerInfo += "%s: %s\n"%(key,value,)

        # print info
        info = item.getLongInfo()
        if info:
            self.addMessage("go show a menu")
            info += "\n\nregisterinformation:\n\n" + registerInfo
            self.submenue = src.interaction.OneKeystrokeMenu(info)
            self.macroState["submenue"] = self.submenue

        # notify listeners
        self.changed("examine",item)


    """
    advance the character one tick
    """
    def advance(self):
        if self.stasis or self.dead:
            return

        # smooth over impossible state
        while self.events and gamestate.tick > self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)

        # handle events
        while self.events and gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            if not event in self.events:
                debugMessages.append("impossible state with events")
                continue
            self.events.remove(event)

        # handle satiation
        self.satiation -= 1
        if self.satiation < 100:
            if self.satiation < 10:
                self.frustration += 10
            self.frustration += 1
        self.changed()
        if self.satiation < 0 and not self.godMode:
            self.die(reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "+commandChars.drink+" key")
            return

        if self.satiation in (300-1,200-1,100-1,30-1):
            self.changed("thirst")
            self.macroState["commandKeyQueue"] = [("|",["norecord"]),(">",["norecord"]),("_",["norecord"]),("j",["norecord"]),("|",["norecord"]),("<",["norecord"])] + self.macroState["commandKeyQueue"]

        if self.satiation == 30-1:
            self.changed("severeThirst")

        if self == mainChar and self.satiation < 30 and self.satiation > -1:
            self.addMessage("you'll starve in "+str(mainChar.satiation)+" ticks!")

        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()

    '''
    register for notifications
    '''
    def addListener(self,listenFunction,tag="default"):
        # create container if container doesn't exist
        # bad performace: string comparison, should use enums. Is this slow in python?
        if not tag in self.listeners:
            self.listeners[tag] = []

        # added listener function
        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregister for notifications
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clear up dict
        # bad performance: probably better to not clean up and recreate
        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    '''
    def changed(self,tag="default",info=None):
        # do nothing if nobody listens
        if not tag in self.listeners:
            return

        # call each listener
        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

    def startIdling(self):
        import random
        waitString = str(random.randint(1,self.personality["idleWaitTime"]))+"."
        waitChance = self.personality["idleWaitChance"]

        if self.aggro:
            self.aggro -= 1
            command = random.choice([
                                     "ope$=aa$=ww$=ss$=ddm",
                                     "ope$=aa$=ww$=ss$=ddmk",
                                    ])
        elif self.frustration < 1000+self.personality["frustrationTolerance"] and not random.randint(1,waitChance) == 1: # real idle
            command = waitString
            self.frustration -= 1
        elif self.frustration < 4000+self.personality["frustrationTolerance"] and not random.randint(1,waitChance) == 1: # do mainly harmless stuff
            command = random.choice(["w"+waitString+"s",
                                     "a"+waitString+"d",
                                     "d"+waitString+"a",
                                     "s"+waitString+"w",
                                     "w"+waitString+"a"+waitString+"s"+waitString+"d",
                                     "d"+waitString+"s"+waitString+"a"+waitString+"w",
                                    ])
            self.frustration -= 10
        elif self.frustration < 16000+self.personality["frustrationTolerance"] and not random.randint(1,waitChance) == 1: # do not so harmless stuff
            command = random.choice(["ls"+waitString+"wk",
                                     "opf$=aa$=ww$=ss$=ddj$=da$=sw$=ws$=ad",
                                     "j","ajd","wjs","dja","sjw",
                                     "Ja","Jw","Js","Jd","J.",
                                     "opn$=aaj$=wwj$=ssj$=ddj",
                                     "opx$=aa$=ww$=ss$=dd",
                                    ])
            self.frustration -= 100
        elif self.frustration < 64000+self.personality["frustrationTolerance"] and not random.randint(1,waitChance) == 1: # bad stuff
            command = random.choice([
                                     "opf$=aa$=ww$=ss$=ddk",
                                     "opf$=aa$=ww$=ss$=ddj$=da$=sw$=ws$=ad",
                                    ])
            self.frustration -= 300
        else: #run amok
            command = random.choice([
                                     "opc$=aa$=ww$=ss$=ddm",
                                     "opc$=aa$=ww$=ss$=ddmk",
                                    ])
            self.frustration -= 1000

        parsedCommand = []
        for char in command:
            parsedCommand.append((char,["norecord"]))

        self.macroState["commandKeyQueue"] = parsedCommand

    def removeSatiation(self,amount):
        self.satiation -= amount
        if self.satiation < 0:
            self.die(reason="you starved")

    def addSatiation(self,amount):
        self.satiation += amount
        if self.satiation > 1000:
            self.satiation = 1000

"""
the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
bad code: animals should not be characters. This means it is possible to chat with a mouse 
"""
class Mouse(Character):
    charType = "Mouse"

    '''
    basic state setting
    '''
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None,characterId=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator,characterId=characterId)
        self.vanished = False
        self.attributesToStore.extend([
               "vanished",
               ])
        self.initialState = self.getState()

        self.personality["autoAttackOnCombatSuccess"] = 1
        self.personality["abortMacrosOnAttack"] = True
        self.health = 10
        self.faction = "mice"

        self.baseDamage = 1
        self.randomBonus = 0
        self.bonusMultiplier = 0
        self.staggerResistant = 0

    '''
    disapear
    '''
    def vanish(self):
        # remove self from map
        self.container.removeCharacter(self)
        self.vanished = True

"""
"""
class Monster(Character):
    charType = "Monster"

    '''
    basic state setting
    '''
    def __init__(self,display="🝆~",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None,characterId=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator,characterId=characterId)
        self.phase = 1
        self.attributesToStore.extend([
               "phase",
               ])
        self.initialState = self.getState()

    def die(self,reason=None,addCorpse=True):
        if self.phase == 1:
            if self.xPosition and self.yPosition and (not self.container.getItemByPosition((self.xPosition,self.yPosition))):
                new = src.items.itemMap["Mold"](creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition
                self.container.addItems([new])
                new.startSpawn()

            super().die(reason,addCorpse=False)
        else:
            super().die(reason,addCorpse)

    def enterPhase2(self):
        self.phase = 2
        if not "NaivePickupQuest" in self.solvers:
            self.solvers.append("NaivePickupQuest")

    def enterPhase3(self):
        self.phase = 3
        self.macroState["macros"] = {"s":["o","p","f","$","=","a","a","$","=","s","s","$","=","w","w","$","=","d","d","j"]}
        self.macroState["macros"]["m"] = []
        import random
        for i in range(0,8):
            self.macroState["macros"]["m"].extend(["_","s"])
            self.macroState["macros"]["m"].append(str(random.randint(0,9)))
            self.macroState["macros"]["m"].append(random.choice(["a","w","s","d"]))
        self.macroState["macros"]["m"].extend(["_","m"])
        self.macroState["commandKeyQueue"] = [("_",[]),("m",[])]

    def enterPhase4(self):
        self.phase = 4
        self.macroState["macros"] = {
                                      "e":["1","0","j","m"],
                                      "s":["o","p","M","$","=","a","a","$","=","w","w","$","=","d","d","$","=","s","s","_","e"],
                                      "w":[],
                                      "f":["%","c","_","s","_","w","_","f"],
                                    }
        import random
        for i in range(0,4):
            self.macroState["macros"]["w"].append(str(random.randint(0,9)))
            self.macroState["macros"]["w"].append(random.choice(["a","w","s","d"]))
        self.macroState["commandKeyQueue"] = [("_",[]),("f",[])]

    def enterPhase5(self):
        self.phase = 5
        import random
        self.faction = ""
        for i in range(0,5):
            self.faction += random.choice("abcdefghiasjlkasfhoiuoijpqwei10934009138402")
        self.macroState["macros"] = {
                                      "j":70*["J","f"]+["m"],
                                      "s":["o","p","M","$","=","a","a","$","=","w","w","$","=","d","d","$","=","s","s","k","j","j","j","k"],
                                      "w":[],
                                      "k":["o","p","e","$","=","a","a","m","$","=","w","w","m","$","=","d","d","m","$","=","s","s","m"],
                                      "f":["%","c","_","s","_","w","_","k","_","f"],
                                    }
        import random
        for i in range(0,8):
            self.macroState["macros"]["w"].append(str(random.randint(0,9)))
            self.macroState["macros"]["w"].append(random.choice(["a","w","s","d"]))
            self.macroState["macros"]["w"].append("m")
        self.macroState["commandKeyQueue"] = [("_",[]),("f",[])]

    def changed(self,tag="default",info=None):
        if self.phase == 1 and self.satiation > 900:
            self.enterPhase2()
        if len(self.inventory) == 10:
            fail = False
            for item in self.inventory:
                if not item.type == "Corpse":
                    fail = True
            if not fail:
                self.addMessage("do action")
                newChar = Monster(creator=self)

                newChar.solvers = [
                          "NaiveActivateQuest",
                          "ActivateQuestMeta",
                          "NaivePickupQuest",
                          "NaiveMurderQuest",
                        ]

                newChar.faction = self.faction
                newChar.enterPhase5()

                toDestroy = self.inventory[0:5]
                for item in toDestroy:
                    item.destroy()
                    self.inventory.remove(item)
                self.container.addCharacter(newChar,self.xPosition,self.yPosition)

        super().changed(tag,info)

    def render(self):
        if self.phase == 2:
            return displayChars.monster_feeder
        elif self.phase == 3:
            return displayChars.monster_grazer
        elif self.phase == 4:
            return displayChars.monster_corpseGrazer
        elif self.phase == 5:
            return displayChars.monster_hunter
        return displayChars.monster_spore

class Exploder(Monster):
    charType = "Exploder"

    def __init__(self,display="🝆~",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None,characterId=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator,characterId=characterId)

        self.explode = True
        self.attributesToStore.extend([
               "explode"])

    def render(self):
        return displayChars.monster_exploder

    def die(self,reason=None,addCorpse=True):
        if self.xPosition and self.container:
            new = src.items.itemMap["FireCrystals"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            if self.explode:
                new.startExploding()

        super().die(reason=reason, addCorpse=False)

characterMap = {
        "Character":Character,
        "Monster":Monster,
        "Exploder":Exploder,
        "Mouse":Mouse,
        }

'''
get item instances from dict state
'''
def getCharacterFromState(state):
    character = characterMap[state["type"]](creator=void,characterId=state["id"])
    loadingRegistry.register(character)
    character.setState(state)
    return character

