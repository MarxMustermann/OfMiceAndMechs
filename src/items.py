####################################################################################
###
##     items and item related code belongs here 
#
####################################################################################

import config
import src.logger
import src.gamestate
import src.interaction

def setup():
    import src.itemFolder.includeTest
    itemMap["TestItem"] = src.itemFolder.includeTest.TestItem
    import src.itemFolder.resources
    itemMap["Scrap"] = src.itemFolder.resources.Scrap
    itemMap["MetalBars"] = src.itemFolder.resources.MetalBars
    itemMap["Case"] = src.itemFolder.resources.Case
    itemMap["PocketFrame"] = src.itemFolder.resources.PocketFrame
    itemMap["Coal"] = src.itemFolder.resources.Coal
    import src.itemFolder.furniture
    itemMap["Wall"] = src.itemFolder.furniture.Wall
    itemMap["Door"] = src.itemFolder.furniture.Door
    import src.itemFolder.obsolete
    itemMap["Pipe"] = src.itemFolder.obsolete.Pipe
    itemMap["Pile"] = src.itemFolder.obsolete.Pile
    itemMap["Acid"] = src.itemFolder.obsolete.Acid
    itemMap["Chain"] = src.itemFolder.obsolete.Chain
    itemMap["Winch"] = src.itemFolder.obsolete.Winch
    import src.itemFolder.automation
    itemMap["JobOrder"] = src.itemFolder.automation.JobOrder
    import src.itemFolder.tradingArtwork
    itemMap["TradingArtwork"] = src.itemFolder.tradingArtwork.TradingArtwork
    import src.itemFolder.questArtwork
    itemMap["QuestArtwork"] = src.itemFolder.questArtwork.QuestArtwork
    import src.itemFolder.managers
    itemMap["RoomManager"] = src.itemFolder.managers.RoomManager
    itemMap["CityBuilder"] = src.itemFolder.managers.CityBuilder
    itemMap["ArchitectArtwork"] = src.itemFolder.managers.ArchitectArtwork
    itemMap["AchitectArtwork"] = src.itemFolder.managers.ArchitectArtwork
    itemMap["RoadManager"] = src.itemFolder.managers.RoadManager
    itemMap["MiningManager"] = src.itemFolder.managers.MiningManager
    itemMap["StockpileMetaManager"] = src.itemFolder.managers.StockpileMetaManager
    itemMap["ProductionManager"] = src.itemFolder.managers.ProductionManager

# load basic libs
import json
import random

# load basic internal libs
import src.saveing
import src.events
import config

class ItemNew(src.saveing.Saveable):
    type = "Item"

    def __init__(self,display=None,xPosition=0,yPosition=0,zPosition=0,creator=None,name="unkown",seed=0,noId=False,
                      runsJobOrders=False,hasSettings=False,runsCommands=False,canReset=False):
        super().__init__()
        
        if not display:
            self.display = src.canvas.displayChars.notImplentedYet
        else:
            try:
                self.display = display
            except:
                pass

        self.seed = seed
        self.name = name
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.zPosition = zPosition
        self.container = None
        self.walkable = False
        self.bolted = True
        self.description = "a "+self.name
        self.tasks = []
        self.blocked = False

        # flags for traits
        self.runsJobOrders = runsJobOrders
        self.hasSettings = hasSettings
        self.runsCommands = runsCommands
        self.canReset = canReset
        self.hasMaintenance = False

        # properties for traits
        self.commands = {}
        self.applyOptions = []

        # set up metadata for saving
        self.attributesToStore.extend([
               "seed","xPosition","yPosition","zPosition","name","type",
               "walkable","bolted","description",
               "isConfigurable","hasSettings","runsCommands","canReset",
               "commands",
               ])

        import uuid
        self.id = uuid.uuid4().hex

    def useJoborderRelayToLocalRoom(self,character,tasks,itemType,information={}):
        newTasks = [
                {
                    "task":"go to room manager",
                    "command":self.commands["go to room manager"]
                },]
        for task in tasks:
            newTasks.append(
                {
                    "task":"insert job order",
                    "command":"scj",
                })
            newTasks.append(
                    {
                        "task":"relay job order",
                        "command":None,
                        "type":"Item",
                        "ItemType":itemType,
                    })
            newTasks.append(task)
        newTasks.append(
            {
                "task":"return from room manager",
                "command":self.commands["return from room manager"]
            })
        newTasks.append(
            {
                "task":"insert job order",
                "command":"scj",
            })
        newTasks.append(
            {
                "task":"register result",
                "command":None,
            })

        character.addMessage("running job order local room relay")
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.tasks = list(reversed(newTasks))
        jobOrder.taskName = "relay job Order"
        jobOrder.information = information

        character.jobOrders.append(jobOrder)
        character.runCommandString("Jj.j")

    def gatherApplyActions(self,character=None):
        result = []
        if self.applyOptions:
           result.append(self.spawnApplyMenu) 
        return result

    def spawnApplyMenu(self,character):
        options = []
        for option in self.applyOptions:
            options.append(option)
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {"method":"handleApplyMenu","container":self,"params":{"character":character}}

    def handleApplyMenu(self,params):
        character = params["character"]

        selection = character.macroState["submenue"].selection

        character.addMessage("index %s"%(selection,))

        if not selection:
            return

        self.applyMap[selection](character)

    def getTerrain(self):
        if self.room:
            terrain = self.room.terrain
        if self.terrain:
            terrain = self.terrain
        return terrain

    def apply(self,character):
        actions = self.gatherApplyActions(character)

        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("i can not do anything useful with this")

    def __vanillaPickUp(self,character):
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted and not character.godMode:
            character.addMessage("you cannot pick up bolted items")
            return

        character.addMessage("you pick up a %s"%(self.type))

        self.container.removeItem(self)

        # remove position information to place item in the void
        self.xPosition = None
        self.yPosition = None

        # add item to characters inventory
        character.inventory.append(self)

    def gatherPickupActions(self,character=None):
        return [self.__vanillaPickUp]

    def pickUp(self,character):
        actions = self.gatherPickupActions()

        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("no pickup action found")

    def getLongInfo(self):
        text = "item: "+self.type+" \n\n"
        if hasattr(self,"descriptionText"):
            text += "description: \n"+self.description+"\n\n"
        if self.commands:
            text += "commands: \n"
            for (key,value,) in self.commands.items():
                text += "%s: %s\n"%(key,value,)
            text += "\n"
        return text

    def render(self):
        return self.display

    def getDetailedInfo(self):
        return self.description

    def fetchSpecialRegisterInformation(self):
        result = {}
        if hasattr(self,"type"):
            result["type"] = self.type
        if hasattr(self,"charges"):
            result["charges"] = self.charges
        if hasattr(self,"uses"):
            result["uses"] = self.uses
        if hasattr(self,"level"):
            result["level"] = self.level
        if hasattr(self,"coolDown"):
            result["coolDown"] = self.coolDown
            result["coolDownRemaining"] = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if hasattr(self,"amount"):
            result["amount"] = self.amount
        if hasattr(self,"walkable"):
            result["walkable"] = self.walkable
        if hasattr(self,"bolted"):
            result["bolted"] = self.bolted
        if hasattr(self,"blocked"):
            result["blocked"] = self.blocked
        return result

    def getConfigurationOptions(self,character):
        options = {}
        if self.runsCommands:
            options["c"] = ("commands",None)#self.setCommands)
        if self.hasSettings:
            options["s"] = ("machine settings",None)#self.setMachineSettings)
        if self.runsJobOrders:
            options["j"] = ("run job order",self.runJobOrder)
        if self.canReset:
            options["r"] = ("reset",self.reset)
        if self.hasMaintenance:
            options["m"] = ("do maintenance",self.doMaintenance)
        return options

    def reset(self,character):
        character.addMessage("nothing to reset")
        pass

    def doMaintenance(self,character):
        character.addMessage("no maintenance action set")

    def configure(self,character):

        self.lastAction = "configure"

        options = self.getConfigurationOptions(character)

        text = ""
        if not options:
            text += "this machine cannot be configured, press any key to continue"
        else:
            for (key,value) in options.items():
                text += "%s: %s\n"%(key,value[0])
            
        self.submenue = src.interaction.OneKeystrokeMenu(text)

        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"configureSwitch","params":{"character":character}}

    def addTriggerToTriggerMap(self,result,name,function):
        triggerList = result.get(name)
        if not triggerList:
           triggerList = []
           result[name] = triggerList
        triggerList.append(function)

    def getJobOrderTriggers(self):
        result = {}
        self.addTriggerToTriggerMap(result,"configure machine",self.jobOrderConfigure)
        self.addTriggerToTriggerMap(result,"register result",self.doRegisterResult)
        return result

    def doRegisterResult(self,task,context):
        pass

    def configureSwitch(self,params):
        self.lastAction = "configureSwitch"

        character = params["character"]

        options = self.getConfigurationOptions(character)
        if self.submenue.keyPressed in options:
            option = options[self.submenue.keyPressed][1](character)
        else:
            character.addMessage("no configure action found for this key")

    def runJobOrder(self,character):
        self.lastAction = "runJobOrder"

        if not character.jobOrders:
            character.addMessage("no job order")
            return

        jobOrder = character.jobOrders[-1]
        task = jobOrder.popTask()

        if not task:
            character.addMessage("no tasks left")
            return

        triggerMap = self.getJobOrderTriggers()
        triggers = triggerMap.get(task["task"])
        if not triggers:
            character.addMessage("unknown trigger: %s %s"%(self,task,))
            return

        for trigger in triggers:
            trigger(task,{"character":character,"jobOrder":jobOrder})

    def jobOrderConfigure(self,task,context):
        for (commandName,command) in task["commands"].items():
            self.commands[commandName] = command

    def runCommand(self,commandName,character):
        command = self.commands.get(commandName)
        if not command:
            return

        character.runCommandString(command)
        character.addMessage("running command for trigger: %s - %s"%(commandName,command))

'''
the base class for all items.
'''
class Item(src.saveing.Saveable):
    '''
    state initialization and id generation
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,zPosition=0,creator=None,name="item",seed=0,noId=False):
        super().__init__()

        self.seed = seed

        # set attributes
        if not hasattr(self,"type"):
            self.type = "Item"
        if not display:
            self.display = src.canvas.displayChars.notImplentedYet
        else:
            try:
                self.display = display
            except:
                pass
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.zPosition = zPosition
        self.room = None
        self.terrain = None
        self.listeners = {"default":[]}
        self.walkable = False
        self.lastMovementToken = None
        self.chainedTo = []
        self.name = name
        self.description = "a "+self.name
        self.mayContainMice = False
        self.bolted = not self.walkable
        self.container = None

        self.customDescription = None

        # set up metadata for saving
        self.attributesToStore.extend([
               "mayContainMice","name","type","walkable","xPosition","yPosition","zPosition","bolted"])

        # set id
        if not noId:
            import uuid
            self.id = uuid.uuid4().hex
        else:
            self.id = None
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

    def render(self):
        return self.display

    def upgrade(self):
        self.level += 1

    def downgrade(self):
        self.level += 1

    '''
    generate a text with a detailed description of the items state
    bad code: casting a dict to string is not really enough
    '''
    def getDetailedInfo(self):
        return str(self.getDetailedState())

    '''
    get a short description
    bad code: name and function say different things
    '''
    def getDetailedState(self):
        return self.description

    '''
    no operation when applying a base item
    '''
    def apply(self,character,silent=False):
        character.changed("activate",self)
        self.changed("activated",character)
        if not silent:
            character.addMessage("i can not do anything useful with this")

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted and not character.godMode:
            character.addMessage("you cannot pick up bolted items")
            return

        character.addMessage("you pick up a %s"%(self.type))
        """
        foundBig = False
        for item in character.inventory:
            if item.walkable == False:
                foundBig = True
                break

        if foundBig and self.walkable == False:
            character.addMessage("you cannot carry more big items")
            return

        character.addMessage("you pick up a "+self.type)
        """

        # bad code: should be a simple self.container.removeItem(self)
        if self.room:
            # remove item from room
            self.container = self.room
            self.container.removeItem(self)
        else:
            # remove item from terrain
            # bad code: should be handled by the terrain
            self.container = self.terrain
            self.container.removeItem(self)

        # remove position information to place item in the void
        self.xPosition = None
        self.yPosition = None

        # add item to characters inventory
        character.inventory.append(self)
        self.changed()

    def fetchSpecialRegisterInformation(self):
        result = {}
        if hasattr(self,"type"):
            result["type"] = self.type
        if hasattr(self,"charges"):
            result["charges"] = self.charges
        if hasattr(self,"uses"):
            result["uses"] = self.uses
        if hasattr(self,"level"):
            result["level"] = self.level
        if hasattr(self,"coolDown"):
            result["coolDown"] = self.coolDown
            result["coolDownRemaining"] = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if hasattr(self,"amount"):
            result["amount"] = self.amount
        if hasattr(self,"walkable"):
            result["walkable"] = self.walkable
        if hasattr(self,"bolted"):
            result["bolted"] = self.bolted
        if hasattr(self,"blocked"):
            result["blocked"] = self.blocked
        return result

    '''
    registering for notifications
    bad code: should be extra class
    '''
    def addListener(self,listenFunction,tag="default"):
        # create bucket if it does not exist yet
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    bad code: should be extra class
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clean up empty buckets
        # bad performance: probably better to not clear and recreate buckets
        if not self.listeners[tag] and not tag == "default":
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    bad code: should be extra class
    '''
    def changed(self,tag="default",info=None):
        if not tag in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

    '''
    get a list of items that is affected if the item would move into some direction
    '''
    def getAffectedByMovementDirection(self,direction,force=1,movementBlock=set()):
        # add self
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(direction,force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item
    '''
    def moveDirection(self,direction,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            oldPosition = (self.xPosition,self.yPosition)
            if direction == "north":
                newPosition = (self.xPosition,self.yPosition-1)
            elif direction == "south":
                newPosition = (self.xPosition,self.yPosition+1)
            elif direction == "west":
                newPosition = (self.xPosition-1,self.yPosition)
            elif direction == "east":
                newPosition = (self.xPosition+1,self.yPosition)

            # remove self from current position
            if self in self.terrain.itemByCoordinates[oldPosition]:
                self.terrain.itemByCoordinates[oldPosition].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[oldPosition]

            # destroy everything on target position
            if newPosition in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[newPosition]:
                    item.destroy()

            # place self on new position
            self.xPosition = newPosition[0]
            self.yPosition = newPosition[1]
            if newPosition in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[newPosition].append(self)
            else:
                self.terrain.itemByCoordinates[newPosition] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    '''
    get the physical resistance to beeing moved
    '''
    def getResistance(self):
        if (self.walkable):
            return 1
        else:
            return 50

    '''
    do nothing
    '''
    def recalculate(self):
        pass

    '''
    destroy the item and leave scrap
    bad code: only works on terrain
    '''
    def destroy(self,generateSrcap=True):

        if not hasattr(self,"terrain"):
            self.terrain = None
        if self.room:
            container = self.room
        elif self.terrain:
            container = self.terrain
        else:
            return

        pos = (self.xPosition,self.yPosition) 

        if pos == (None,None):
            return

        # remove item from terrain
        container.removeItem(self)

        # generatate scrap
        if generateSrcap:
            newItem = src.items.itemMap["Scrap"](pos[0],pos[1],1,creator=self)
            newItem.room = self.room
            newItem.terrain = self.terrain

            if pos in container.itemByCoordinates:
                for item in container.itemByCoordinates[pos]:
                    container.removeItem(item)
                    if not item.type == "Scrap":
                        newItem.amount += 1
                    else:
                        newItem.amount += item.amount
            newItem.setWalkable()

            # place scrap
            container.addItems([newItem])

        self.xPosition = None
        self.yPosition = None
            
    def getState(self):
        state = super().getState()
        state["id"] = self.id
        state["type"] = self.type
        state["xPosition"] = self.xPosition
        state["yPosition"] = self.yPosition
        return state

    def getLongInfo(self):
        return None

    def configure(self,character):
        character.addMessage("nothing to configure")

class MiningShaft(ItemNew):
    type = "MiningShaft"
    
    def apply(self,character):
        character.zPosition -= 1

    def configure(self,character):
        character.zPosition += 1

'''
'''
class Corpse(Item):
    type = "Corpse"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="corpse",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.corpse,xPosition,yPosition,name=name,creator=creator)
        self.charges = 1000
        self.attributesToStore.extend([
               "activated","charges"])
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        text = """
item: Corpse

description:
A corpse. Activate it to eat from it. Eating from a Corpse will gain you 15 Satiation.

can be processed in a corpse shredder

The corpse has %s charges left.

"""%(self.charges)
        return text

    def apply(self,character):
        if isinstance(character,src.characters.Monster):
            if character.phase == 3:
                character.enterPhase4()
            else:
                if self.container and character.satiation < 950:
                    character.macroState["commandKeyQueue"] = [("j",[]),("m",[])] + character.macroState["commandKeyQueue"]
            character.frustration -= 1
        else:
            character.frustration += 1

        if self.charges:
            character.satiation += 15
            if character.satiation > 1000:
                character.satiation = 1000
            self.charges -= 1
            character.addMessage("you eat from the corpse and gain 15 satiation")
        else:
            self.destroy(generateSrcap=False)

class ItemUpgrader(Item):
    type = "ItemUpgrader"

    def __init__(self,xPosition=0,yPosition=0,name="item upgrader",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.itemUpgrader,xPosition,yPosition,name=name,creator=creator)
        self.charges = 3
        self.level = 1

        self.attributesToStore.extend([
               "charges","level"])

    def apply(self,character):
        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return
        if self.xPosition == None:
            character.addMessage("this machine has to be placed to be used")
            return

        inputItem = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputItem = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)][0]

        if not inputItem:
            character.addMessage("place item to upgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.addMessage("cannot upgrade %s"%(inputItem.type))
            return

        if inputItem.level > self.level:
            character.addMessage("item upgrader needs to be upgraded to upgrade this item further")
            return

        if inputItem.level == 1:
            chance = -1
        elif inputItem.level == 2:
            chance = 0
        elif inputItem.level == 3:
            chance = 1
        elif inputItem.level == 4:
            chance = 2
        else:
            chance = 100

        success = False
        if src.gamestate.gamestate.tick % (self.charges+1) > chance:
            success = True

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if inputItem.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.room.removeItem(inputItem)

        if success:
            inputItem.upgrade()
            character.addMessage("%s upgraded"%(inputItem.type,))
            self.charges = 0
            inputItem.xPosition = self.xPosition+1
            inputItem.yPosition = self.yPosition
            self.room.addItems([inputItem])
        else:
            self.charges += 1
            character.addMessage("failed to upgrade %s - has %s charges now"%(inputItem.type,self.charges))
            inputItem.xPosition = self.xPosition
            inputItem.yPosition = self.yPosition+1
            self.room.addItems([inputItem])
            inputItem.destroy()

    def getLongInfo(self):
        text = """
item: ItemUpgrader

description:
An upgrader works from time to time. A failed upgrade will destroy the item but increase the chances of success
Place item to upgrade to the west and the upgraded item will be placed to the east.
If the upgrade fails the remains of the item will be placed to the south.

it has %s charges.

"""%(self.charges)
        return text

class ItemDowngrader(Item):
    type = "ItemDowngrader"

    def __init__(self,xPosition=0,yPosition=0,name="item downgrader",creator=None,noId=False):
        super().__init__(xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return
        if self.xPosition == None:
            character.addMessage("this machine has to be placed to be used")
            return

        inputItem = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputItem = self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)][0]

        if not inputItem:
            character.addMessage("place item to downgrade on the left")
            return

        if not hasattr(inputItem,"level"):
            character.addMessage("cannot downgrade %s"%(inputItem.type))
            return

        if inputItem.level == 1:
            character.addMessage("cannot downgrade item further")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if inputItem.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.room.removeItem(inputItem)

        inputItem.level -= 1
        character.addMessage("%s downgraded"%(inputItem.type,))
        inputItem.xPosition = self.xPosition+1
        inputItem.yPosition = self.yPosition
        self.room.addItems([inputItem])

    def getLongInfo(self):
        text = """
item: ItemDowngrader

description:

the item downgrader downgrades items

Place item to upgrade to the west and the downgraded item will be placed to the east.

"""
        return text

'''
an character spawning item
'''
class GrowthTank(Item):
    type = "GrowthTank"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="growth tank",filled=False,creator=None,noId=False):
        self.filled = filled
        if filled:
            super().__init__(src.canvas.displayChars.growthTank_filled,xPosition,yPosition,name=name,creator=creator)
        else:
            super().__init__(src.canvas.displayChars.growthTank_unfilled,xPosition,yPosition,name=name,creator=creator)

        self.commands = {}
        self.attributesToStore.extend([
               "filled","commands"])

    '''
    manually eject character
    '''
    def apply(self,character):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        super().apply(character,silent=True)
        if self.filled:
            self.eject()
        else:
            flask = None
            for item in character.inventory:
                if isinstance(item,GooFlask):
                    if item.uses == 100:
                        flask = item
            if flask:
                flask.uses = 0
                flask.changed()
                self.filled = True
                self.changed()
            else:
                character.addMessage("you need to have a full goo flask to refill the growth tank")

    def configure(self,character):
        options = [("addCommand","add command"),("reset","reset")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("born","set command for newly born npcs"))

            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = {"container":self,"method":"setCommand"}
        if self.submenue.selection == "reset":
            self.character.addMessage("you reset the machine")
            self.commands = {}

    def runCommand(self,commandName,character=None):
        if not commandName in self.commands:
            return
        command = self.commands[commandName]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        if not character:
            character = self.character
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command for trigger: %s - %s"%(commandName,command))

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the east")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    '''
    render the growth tank
    '''
    @property
    def display(self):
        if self.filled:
            return src.canvas.displayChars.growthTank_filled
        else:
            return src.canvas.displayChars.growthTank_unfilled

    '''
    ejecting a character
    '''
    def eject(self,character=None):
        # emtpy growth tank
        self.filled = False

        '''
        generate a name
        bad code: should be somewhere else
        bad code: redundant code
        '''
        def getRandomName(seed1=0,seed2=None):
            if seed2 == None:
                seed2 = seed1+(seed1//5)
            return config.names.characterFirstNames[seed1%len(config.names.characterFirstNames)]+" "+config.names.characterLastNames[seed2%len(config.names.characterLastNames)]

        # add character
        if not character:
            name = getRandomName(self.xPosition+self.room.timeIndex,self.yPosition+self.room.timeIndex)
            character = characters.Character(src.canvas.displayChars.staffCharactersByLetter[name[0].lower()],self.xPosition+1,self.yPosition,name=name,creator=self)

            character.solvers = [
                      "SurviveQuest",
                      "Serve",
                      "NaiveMoveQuest",
                      "MoveQuestMeta",
                      "NaiveActivateQuest",
                      "ActivateQuestMeta",
                      "NaivePickupQuest",
                      "PickupQuestMeta",
                      "DrinkQuest",
                      "ExamineQuest",
                      "FireFurnaceMeta",
                      "CollectQuestMeta",
                      "WaitQuest"
                      "NaiveDropQuest",
                      "DropQuestMeta",
                    ]

        # inhabit character
        #character.fallUnconcious()
        #character.hasFloorPermit = False
        self.room.addCharacter(character,self.xPosition+1,self.yPosition)
        #character.revokeReputation(amount=4,reason="beeing helpless")
        #character.macroState["commandKeyQueue"] = [("j",[])]
        character.macroState["macros"]["j"] = "Jf"
        self.runCommand("born",character=character)

        return character

    def getLongInfo(self):
        text = """
item: GrowthTank

description:
A growth tank produces NPCs. 

Fill a growth tank to prepare it for generating an npc.
You can fill it by activating it with a full goo flask in your inventory.

Activate a filled growth tank to spawn a new npc.
Wake the NPC by taking to the NPC.

You talk to NPCs by pressing h and selecting the NPC to talk to.

"""
        return text

'''
basically a bed with a activatable cover
'''
class Hutch(Item):
    type = "Hutch"

    def __init__(self,xPosition=0,yPosition=0,name="Hutch",activated=False,creator=None,noId=False):
        self.activated = activated
        super().__init__(src.canvas.displayChars.hutch_free,xPosition,yPosition,creator=creator)

        # bad code: set metadata for saving
        self.attributesToStore.extend([
               "activated"])

    '''
    render the hutch
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.hutch_occupied
        else:
            return src.canvas.displayChars.hutch_free

    '''
    open/close cover
    bad code: open close methods would be nice
    '''
    def apply(self,character):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        super().apply(character,silent=True)
        if not self.activated:
            self.activated = True
        else:
            self.activated = False

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

    def getLongInfo(self):
        text = """
item: Hutch

description:
A hutch. It is not useful.

"""
        return text

'''
item for letting characters trigger something
'''
class Lever(Item):
    type = "Lever"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="lever",activated=False,creator=None,noId=False):
        self.activated = activated
        super().__init__(src.canvas.displayChars.lever_notPulled,xPosition,yPosition,name=name,creator=creator)
        self.activateAction = None
        self.deactivateAction = None
        self.walkable = True
        self.bolted = True

        # set metadata for saving
        self.attributesToStore.extend([
               "activated"])

    '''
    pull the lever!
    bad code: activate/deactive methods would be nice
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if not self.activated:
            # activate the lever
            self.activated = True

            # run the action
            if self.activateAction:
                self.activateAction(self)
        else:
            # deactivate the lever
            self.activated = False

            # run the action
            if self.deactivateAction:
                self.activateAction(self)

        # notify listeners
        self.changed()

    '''
    render the lever
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.lever_pulled
        else:
            return src.canvas.displayChars.lever_notPulled

    def getLongInfo(self):
        text = """
item: Lever

description:
A lever. It is not useful.

"""
        return text

'''
heat source for generating steam and similar
'''
class Furnace(Item):
    type = "Furnace"

    '''
    straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Furnace",creator=None,noId=False):
        self.activated = False
        self.boilers = []
        super().__init__(src.canvas.displayChars.furnace_inactive,xPosition,yPosition,name=name,creator=creator)

        # set metadata for saving
        self.attributesToStore.extend([
               "activated"])

    '''
    fire the furnace
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return
        
        # select fuel
        # bad pattern: the player should be able to select fuel
        # bad pattern: coal should be preferred
        foundItem = None
        for item in character.inventory:
            canBurn = False
            if hasattr(item,"canBurn"):
                canBurn = item.canBurn

            if not canBurn:
                continue
            foundItem = item

        # refuse to fire the furnace without fuel
        if not foundItem:
            # bad code: return would be preferable to if/else
            if character.watched:
                character.addMessage("you need coal to fire the furnace and you have no coal in your inventory")
        else:
            # refuse to fire burning furnace
            if self.activated:
                # bad code: return would be preferable to if/else
                if character.watched:
                    character.addMessage("already burning")
            # fire the furnace
            else:
                self.activated = True

                # destroy fuel
                character.inventory.remove(foundItem)
                character.changed()

                # add fluff
                if character.watched:
                    character.addMessage("you fire the furnace")

                # get the boilers affected
                self.boilers = []
                #for boiler in self.room.boilers:
                for boiler in self.room.itemsOnFloor:
                    if isinstance(boiler, src.items.Boiler):
                        if ((boiler.xPosition in [self.xPosition,self.xPosition-1,self.xPosition+1] and boiler.yPosition == self.yPosition) or boiler.yPosition in [self.yPosition-1,self.yPosition+1] and boiler.xPosition == self.xPosition):
                            self.boilers.append(boiler)

                # heat up boilers
                for boiler in self.boilers:
                    boiler.startHeatingUp()
                
                # make the furnace stop burning after some time
                event = src.events.FurnaceBurnoutEvent(self.room.timeIndex+30,creator=self)
                event.furnace = self
                self.room.addEvent(event)

                # notify listeners
                self.changed()

    '''
    render the furnace
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.furnace_active
        else:
            return src.canvas.displayChars.furnace_inactive

    def getLongInfo(self):
        text = """
item: Furnace

description:
A furnace is used to generate heat. Heat is used to produce steam in boilers.

You can fire the furnace by activating it with coal in your inventory.

Place the furnace next to a boiler to be able to heat up the boiler with this furnace.

"""
        return text

    def getLongInfo(self):
        return str(self.id)

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class Commlink(Item):
    type = "CommLink"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Commlink",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.commLink,xPosition,yPosition,name=name,creator=creator)

        self.scrapToDeliver = 100
        self.attributesToStore.extend([
               "scrapToDeliver"])

    '''
    get tributes and trades
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return
        
        if self.scrapToDeliver > 0:
            toRemove = []
            for item in character.inventory:
                if isinstance(item,itemMap["Scrap"]):
                    toRemove.append(item)
                    self.scrapToDeliver -= 1

            character.addMessage("you need to delivered %s scraps"%(len(toRemove)))
            for item in toRemove:
                character.inventory.remove(item)

        if self.scrapToDeliver > 0:
            character.addMessage("you need to deliver %s more scraps to have payed tribute"%(self.scrapToDeliver))
            return

        character.addMessage("you have payed tribute yay")

    def getLongInfo(self):
        text = """
item: CommLink

description:
A comlink. 

"""

'''
should be a display, but is abused as vehicle control
bad code: use an actual vehicle control
'''
class RoomControls(Item):
    type = "RoomControls"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomControls",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.display,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # handle movement keystrokes
        '''
        move room to north
        '''
        def moveNorth():
            self.room.moveDirection("north",force=self.room.engineStrength)
        '''
        move room to south
        '''
        def moveSouth():
            self.room.moveDirection("south",force=self.room.engineStrength)
        '''
        move room to west
        '''
        def moveWest():
            self.room.moveDirection("west",force=self.room.engineStrength)
        '''
        move room to east
        '''
        def moveEast():
            self.room.moveDirection("east",force=self.room.engineStrength)

        if not "stealKey" in character.macroState:
            character.macroState["stealKey"] = {}

        '''
        reset key mapping
        '''
        def disapply():
            del character.macroState["stealKey"][config.commandChars.move_north]
            del character.macroState["stealKey"][config.commandChars.move_south]
            del character.macroState["stealKey"][config.commandChars.move_west]
            del character.macroState["stealKey"][config.commandChars.move_east]
            del character.macroState["stealKey"]["up"]
            del character.macroState["stealKey"]["down"]
            del character.macroState["stealKey"]["right"]
            del character.macroState["stealKey"]["left"]
            del character.macroState["stealKey"][config.commandChars.activate]

        # map the keystrokes
        character.macroState["stealKey"][config.commandChars.move_north] = moveNorth
        character.macroState["stealKey"][config.commandChars.move_south] = moveSouth
        character.macroState["stealKey"][config.commandChars.move_west] = moveWest
        character.macroState["stealKey"][config.commandChars.move_east] = moveEast
        character.macroState["stealKey"]["up"] = moveNorth
        character.macroState["stealKey"]["down"] = moveSouth
        character.macroState["stealKey"]["left"] = moveWest
        character.macroState["stealKey"]["right"] = moveEast
        character.macroState["stealKey"][config.commandChars.activate] = disapply

    def getLongInfo(self):
        text = """
item: RoomControls

description:
Room controls. Can be used to control vehicles.

Use it to take control over the vehice.

While controlling the vehicle your movement keys will be overriden. 
The movement key will move the room instead of yourself.
For example pressing w will not move you to the north, but will move the room to the north.
You need enough steam generation to move

To stop using the room controls press j again.

"""
        return text

'''
'''
class RoomBuilder(Item):
    type = "RoomBuilder"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="RoomBuilder",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.roomBuilder,xPosition,yPosition,name=name,creator=creator)

    '''
    map player controls to room movement 
    '''
    def apply(self,character):
        if self.room:
            character.addMessage("this machine can not be used within rooms")
            return

        if self.xPosition == None:
            character.addMessage("this machine can not be used within rooms")
            return

        if self.terrain == None:
            character.addMessage("this machine can not be used within rooms")
            return
        
        wallLeft = False
        for offset in range(1,15):
            pos = (self.xPosition-offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallLeft = item
                        break
            if wallLeft:
                break
        wallRight = False
        for offset in range(1,15):
            pos = (self.xPosition+offset,self.yPosition)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallRight = item
                        break
            if wallRight:
                break
        wallTop = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition-offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallTop = item
                        break
            if wallTop:
                break
        wallBottom = False
        for offset in range(1,15):
            pos = (self.xPosition,self.yPosition+offset)
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door):
                        wallBottom = item
                        break
            if wallBottom:
                break

        if not ( wallLeft and wallRight and wallTop and wallBottom) :
            character.addMessage("no boundaries found")
            return

        roomLeft = self.xPosition-wallLeft.xPosition
        roomRight = wallRight.xPosition-self.xPosition
        roomTop = self.yPosition-wallTop.yPosition
        roomBottom = wallBottom.yPosition-self.yPosition

        if roomLeft+roomRight+1 > 15:
            character.addMessage("room to big")
            return
        if roomTop+roomBottom+1 > 15:
            character.addMessage("room to big")
            return

        wallMissing = False
        items = []
        specialItems = []
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition-roomTop)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition-roomLeft,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for y in range(-roomTop,roomBottom+1):
            pos = (self.xPosition+roomRight,self.yPosition+y)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break
        for x in range(-roomLeft,roomRight+1):
            pos = (self.xPosition+x,self.yPosition+roomBottom)
            wallFound = None 
            if pos in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[pos]:
                    if isinstance(item,Wall) or isinstance(item,Door) or isinstance(item,Chute):
                        wallFound = item
                        if not item in items:
                            items.append(item)
                        if isinstance(item,Door) or isinstance(item,Chute):
                            if not item in specialItems:
                                specialItems.append(item)
                        break
            if not wallFound:
                wallMissing = True
                break

        if wallMissing:
            character.addMessage("wall missing")
            return

        for item in specialItems:
            for compareItem in specialItems:
                if item == compareItem:
                    continue
                if abs(item.xPosition-compareItem.xPosition) > 1 or (abs(item.xPosition-compareItem.xPosition) == 1 and abs(item.yPosition-compareItem.yPosition) > 0):
                    continue
                if abs(item.yPosition-compareItem.yPosition) > 1 or (abs(item.yPosition-compareItem.yPosition) == 1 and abs(item.xPosition-compareItem.xPosition) > 0):
                    continue
                character.addMessage("special items to near to each other")
                return

        import src.rooms
        oldTerrain = self.terrain
        for item in items:
            if item == self:
                continue

            oldX = item.xPosition
            oldY = item.yPosition
            item.container.removeItem(item)
            item.xPosition = roomLeft+oldX-self.xPosition
            item.yPosition = roomTop+oldY-self.yPosition
        room = src.rooms.EmptyRoom(self.xPosition//15,self.yPosition//15,self.xPosition%15-roomLeft,self.yPosition%15-roomTop,creator=self)
        room.reconfigure(roomLeft+roomRight+1,roomTop+roomBottom+1,items)

        
        xOffset = character.xPosition-self.xPosition
        yOffset = character.yPosition-self.yPosition

        oldTerrain.removeCharacter(character)
        oldTerrain.addRooms([room])
        character.xPosition = roomLeft+xOffset
        character.yPosition = roomTop+yOffset
        room.addCharacter(character,roomLeft+xOffset,roomTop+yOffset)

        self.terrain.removeItem(self)

        self.xPosition = roomLeft
        self.yPosition = roomTop
        self.room = None
        self.terrain = None
        room.addItems([self])

    def getLongInfo(self):
        text = """
item: RoomBuilder

description:
The roombuilder creates rooms from basic items.

Place Walls and and Doors around the room builder and activate the room builder to create a room.

The room has to be a rectangle.

"""
        return text

'''
produces steam from heat
bad code: sets the rooms steam generation directly without using pipes
'''
class Boiler(Item):
    type = "Boiler"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="boiler",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.boiler_inactive,xPosition,yPosition,name=name,creator=creator)
        self.isBoiling = False
        self.isHeated = False
        self.startBoilingEvent = None
        self.stopBoilingEvent = None

        # set metadata for saving
        self.attributesToStore.extend([
               "isBoiling","isHeated"])

        self.objectsToStore.append("startBoilingEvent")
        self.objectsToStore.append("stopBoilingEvent")

    '''
    start producing steam after a delay
    '''
    def startHeatingUp(self):

        # do not heat up heated items
        if self.isHeated:
            return

        # flag self as heated
        self.isHeated = True

        # abort cooling down
        if self.stopBoilingEvent:
            self.room.removeEvent(self.stopBoilingEvent)
            self.stopBoilingEvent = None

        # shedule the steam generation
        if not self.startBoilingEvent and not self.isBoiling:
            # shedule the event
            event = src.events.StartBoilingEvent(self.room.timeIndex+5,creator=self)
            event.boiler = self
            self.room.addEvent(event)

        # notify listeners
        self.changed()
        
    '''
    stop producing steam after a delay
    '''
    def stopHeatingUp(self):
        # don't do cooldown on cold boilers
        if not self.isHeated:
            return

        # flag self as heated
        self.isHeated = False

        # abort any heating up
        if self.startBoilingEvent:
            self.room.removeEvent(self.startBoilingEvent)
            self.startBoilingEvent = None
        if not self.stopBoilingEvent and self.isBoiling:

            event = src.events.StopBoilingEvent(self.room.timeIndex+5,creator=self)
            event.boiler = self
            self.room.addEvent(event)

        # notify listeners
        self.changed()

    def getLongInfo(self):
        text = """
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""+self.id
        return text
            
    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        if self.isBoiling:
            self.display = src.canvas.displayChars.boiler_active

'''
steam sprayer used as a prop in the vat
'''
class Spray(Item):
    type = "Spray"

    '''
    call superclass constructor with modified parameters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="spray",direction=None,creator=None,noId=False):
        # skin acording to spray direction
        if direction == None:
            direction = "left"

        self.direction = direction

        super().__init__(src.canvas.displayChars.spray_left_inactive,xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "direction"])

    '''
    set appearance depending on energy supply
    bad code: energy supply is directly taken from the machine room
    '''
    @property
    def display(self):
        if self.direction == "left":
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_left_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_left_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_left_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_left_stage3
        else:
            if self.terrain.tutorialMachineRoom.steamGeneration == 0:
                return src.canvas.displayChars.spray_right_inactive
            elif self.terrain.tutorialMachineRoom.steamGeneration == 1:
                return src.canvas.displayChars.spray_right_stage1
            elif self.terrain.tutorialMachineRoom.steamGeneration == 2:
                return src.canvas.displayChars.spray_right_stage2
            elif self.terrain.tutorialMachineRoom.steamGeneration == 3:
                return src.canvas.displayChars.spray_right_stage3

    def getLongInfo(self):
        text = """
item: Boiler

description:
a boiler can be heated by a furnace to produce steam. Steam is the basis for energy generation.

"""
        return text
            
'''
marker ment to be placed by characters and to control actions with
'''
class MarkerBean(Item):
    type = "MarkerBean"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="bean",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.markerBean_inactive,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated"])

    '''
    render the marker
    '''
    @property
    def display(self):
        if self.activated:
            return src.canvas.displayChars.markerBean_active
        else:
            return src.canvas.displayChars.markerBean_inactive

    '''
    activate marker
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        character.addMessage(character.name+" activates a marker bean")
        self.activated = True

    def getLongInfo(self):
        text = """
item: MarkerBean

description:
A marker been. It can be used to mark things.

"""
        return text

'''
machine for filling up goo flasks
'''
class GooDispenser(Item):
    type = "GooDispenser"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo dispenser",creator=None,noId=False):
        self.activated = False
        self.baseName = name
        self.level = 1
        super().__init__(src.canvas.displayChars.gooDispenser,xPosition,yPosition,name=name,creator=creator)

        # set up meta information for saveing
        self.attributesToStore.extend([
               "activated","charges"])

        self.charges = 0
        self.maxCharges = 100

        self.description = self.baseName + " (%s charges)"%(self.charges)

    def setDescription(self):
        self.description = self.baseName + " (%s charges)"%(self.charges)
    
    '''
    fill goo flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if not self.charges:
            character.addMessage("the dispenser has no charges")
            return

        filled = False
        fillAmount = 100+((self.level-1)*10)
        for item in character.inventory:
            if isinstance(item,GooFlask) and not item.uses >= fillAmount:
                item.uses = fillAmount
                filled = True
                self.charges -= 1 
                self.description = self.baseName + " (%s charges)"%(self.charges)
                break
        if filled:
            character.addMessage("you fill the goo flask")
        self.activated = True

    def addCharge(self):
        self.charges += 1 
        self.description = self.baseName + " (%s charges)"%(self.charges)

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
item: GooDispenser

description:
A goo dispenser can fill goo flasks.

Activate it with a goo flask in you inventory.
The goo flask will be filled by the goo dispenser.

Filling a flask will use up a charge from your goo dispenser.

This goo dispenser currently has %s charges

"""%(self.charges)
        return text

'''
'''
class BloomShredder(Item):
    type = "BloomShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bloom shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.bloomShredder,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Bloom):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 1:
            character.addMessage("not enough blooms")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        self.room.removeItem(items[0])

        # spawn the new item
        new = BioMass(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: BloomShredder

description:
A bloom shredder produces bio mass from blooms.

Place bloom to the left/west of the bloom shredder.
Activate the bloom shredder to produce biomass.

"""
        return text

'''
'''
class CorpseShredder(Item):
    type = "CorpseShredder"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="corpse shredder",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.corpseShredder,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        corpse = None
        moldSpores = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Corpse):
                    corpse = item
                if isinstance(item,MoldSpore):
                    moldSpores.append(item)

        # refuse to produce without resources
        if not corpse:
            character.addMessage("no corpse")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        self.room.removeItem(corpse)

        for i in range(0,corpse.charges//100):
            if moldSpores:
                self.room.removeItem(moldSpores.pop())
                new = SeededMoldFeed(creator=self)
            else:
                # spawn the new item
                new = MoldFeed(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: CorpseShredder

description:
A corpse shredder produces mold feed from corpses.
If corpses and MoldSpores are supplied it produces seeded mold feed

Place corpse/mold seed to the west of the bloom shredder.
Activate the corpse shredder to produce mold feed/seeded mold feed.

"""
        return text

'''
'''
class SporeExtractor(Item):
    type = "SporeExtractor"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="spore extractor",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.sporeExtractor,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):

        super().apply(character,silent=True)

        if self.xPosition == None:
            character.addMessage("this machine needs to be placed to be used")
            return

        items = []
        if (self.xPosition-1,self.yPosition) in self.container.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,Bloom):
                    items.append(item)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # refuse to produce without resources
        if len(items) < 1:
            character.addMessage("not enough blooms")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        self.room.removeItem(items[0])

        # spawn the new item
        for i in range(1,5):
            new = MoldSpore(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: SporeExtractor

description:
A Spore Extractor removes spores from mold blooms.

Place mold bloom to the west/left and activate the Spore Extractor.
The MoldSpores will be outputted to the east/right.

"""
        return text


'''
'''
class MaggotFermenter(Item):
    type = "MaggotFermenter"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="maggot fermenter",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.maggotFermenter,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.xPosition:
            character.addMessage("This has to be placed to be used")
            return

        if not self.room:
            character.addMessage("This has to be placed in a room to be used")
            return

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,VatMaggot):
                    items.append(item)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # refuse to produce without resources
        if len(items) < 10:
            character.addMessage("not enough maggots")
            return
       
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        # spawn the new item
        new = BioMass(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: MaggotFermenter

description:
A maggot fermenter produces bio mass from vat maggots.

Place 10 vat maggots to the left/west of the maggot fermenter.
Activate the maggot fermenter to produce biomass.

"""
        return text

'''
'''
class GooProducer(Item):
    type = "GooProducer"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo producer",creator=None,noId=False):
        self.activated = False
        self.level = 1
        super().__init__(src.canvas.displayChars.gooProducer,xPosition,yPosition,name=name,creator=creator)

        # bad code: repetetive and easy to forgett
        self.attributesToStore.extend([
               "level"])
    
    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input items
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,PressCake):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 10+(self.level-1):
            character.addMessage("not enough press cakes")
            return
       
        # refill goo dispenser
        dispenser = None
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if isinstance(item,GooDispenser):
                    dispenser = item
        if not dispenser:
            character.addMessage("no goo dispenser attached")
            return 

        if dispenser.level > self.level:
            character.addMessage("the goo producer has to have higher or equal the level as the goo dispenser")
            return 

        if dispenser.charges >= dispenser.maxCharges:
            character.addMessage("the goo dispenser is full")
            return 

        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        dispenser.addCharge()

    def getLongInfo(self):
        text = """
item: GooProducer

description:
A goo producer produces goo from press cakes.

Place 10 press cakes to the left/west of the goo producer and a goo dispenser to the rigth/east.
Activate the maggot fermenter to add a charge to the goo dispenser.

"""
        return text

'''
'''
class BioPress(Item):
    type = "BioPress"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="bio press",creator=None,noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.bioPress,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input scrap
        items = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,BioMass):
                    items.append(item)

        # refuse to produce without resources
        if len(items) < 10:
            character.addMessage("not enough bio mass")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return
       
        # remove resources
        counter = 0
        for item in items:
            if counter >= 10:
                break
            counter += 1
            self.room.removeItem(item)

        # spawn the new item
        new = PressCake(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: BioPress

description:
A bio press produces press cake from bio mass.

Place 10 bio mass to the left/west of the bio press.
Activate the bio press to produce biomass.

"""
        return text


'''
flask with food to carry around and drink from
'''
class GooFlask(Item):
    type = "GooFlask"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="goo flask",creator=None,noId=False):
        self.uses = 0
        super().__init__(src.canvas.displayChars.gooflask_empty,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.description = "a flask containing goo"
        self.level = 1
        self.maxUses = 100

        # set up meta information for saveing
        self.attributesToStore.extend([
               "uses","level","maxUses"])

    '''
    drink from flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.addMessage("you drink from your flask, but it is empty")
            return

        # print feedback
        if character.watched:
            if not self.uses == 1:
                character.addMessage("you drink from your flask")
            else:
                character.addMessage("you drink from your flask and empty it")

        # change state
        self.uses -= 1
        self.changed()
        character.heal(1,reason="drank from flask")
        if character.frustration > 5000:
            character.frustration -= 15
        character.satiation = 1000
        character.changed()

    '''
    render based on fill amount
    '''
    @property
    def display(self):
        displayByUses = [src.canvas.displayChars.gooflask_empty, src.canvas.displayChars.gooflask_part1, src.canvas.displayChars.gooflask_part2, src.canvas.displayChars.gooflask_part3, src.canvas.displayChars.gooflask_part4, src.canvas.displayChars.gooflask_full]
        return displayByUses[self.uses//20]

    '''
    get info including the charges on the flask
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" ("+str(self.uses)+" charges)"

    def getLongInfo(self):
        text = """
item: GooFlask

description:
A goo flask holds goo. Goo is nourishment for you.

If you do not drink from the flask every 1000 ticks you will starve.

A goo flask can be refilled at a goo dispenser and can hold a maximum of %s charges.

this is a level %s item.

"""%(self.maxUses,self.level)
        return text

    def upgrade(self):
        super().upgrade()

        self.maxUses += 10

    def downgrade(self):
        super().downgrade()

        self.maxUses -= 10

'''
Vial with health to carry around and drink from
'''
class Vial(Item):
    type = "Vial"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=None,yPosition=None,name="vial",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.gooflask_empty,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False
        self.description = "a vial containing health"
        self.maxUses = 10
        self.uses = 0
        self.level = 1

        # set up meta information for saveing
        self.attributesToStore.extend([
               "uses","level","maxUses"])

    '''
    drink from flask
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.addMessage("you drink from your flask, but it is empty")
            return

        # print feedback
        if character.watched:
            if not self.uses == 1:
                character.addMessage("you drink from your flask")
            else:
                character.addMessage("you drink from your flask and empty it")

        # change state
        self.uses -= 1
        self.changed()
        character.heal(10)
        character.changed()

    '''
    render based on fill amount
    '''
    @property
    def display(self):
        displayByUses = [src.canvas.displayChars.gooflask_empty, src.canvas.displayChars.gooflask_part1, src.canvas.displayChars.gooflask_part2, src.canvas.displayChars.gooflask_part3, src.canvas.displayChars.gooflask_part4, src.canvas.displayChars.gooflask_full]
        return displayByUses[self.uses//2]

    '''
    get info including the charges on the flask
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" ("+str(self.uses)+" charges)"

    def getLongInfo(self):
        text = """
item: Vial

description:
A vial holds health. You can heal yourself with it

A goo flask can be refilled at a health station and can hold a maximum of %s charges.

this is a level %s item.

"""%(self.maxUses,self.level)
        return text

    def upgrade(self):
        super().upgrade()

        self.maxUses += 1

    def downgrade(self):
        super().downgrade()

        self.maxUses -= 1


'''
a vending machine basically
bad code: currently only dispenses goo flasks
'''
class OjectDispenser(Item):
    type = "ObjectDispenser"

    '''
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.objectDispenser,xPosition,yPosition,name=name,creator=creator)

        self.storage = []
        counter = 0
        while counter < 5:
            self.storage.append(GooFlask(creator=self))
            counter += 1

    '''
    drop goo flask
    '''
    def dispenseObject(self):
        if len(self.storage):
            new = self.storage.pop()
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            self.room.addItems([new])
        else:
            src.logger.debugMessages.append("the object dispenser is empty")

    def getLongInfo(self):
        text = """
item: ObjectDispenser

description:
A object dispenser holds and returns objects.

You can use it to retrieve an object from the object dispenser.

"""
        return text


'''
token object ment to produce anything from metal bars
bad pattern: serves as dummy for actual production lines
'''
class ProductionArtwork(Item):
    type = "ProductionArtwork"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="production artwork",creator=None,noId=False):
        self.coolDown = 10000
        self.coolDownTimer = -self.coolDown
        self.charges = 10
        self.godMode = False

        super().__init__(src.canvas.displayChars.productionArtwork,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges","godMode"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.godMode:
            if not self.room:
                character.addMessage("this machine can only be used within rooms")
                return

            # gather a metal bar
            metalBar = None
            if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
                for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                    if isinstance(item,src.items.itemMap["MetalBars"]):
                       metalBar = item
                       break
            if not metalBar:
                character.addMessage("no metal bars on the left/west")
                return
            
            if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
                character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
                return

        self.character = character

        excludeList = ("ProductionArtwork","Machine","Tree","Scrap","xCorpse","Acid","Item","Pile","InfoScreen","CoalMine","BluePrint","GlobalMacroStorage","Note","Command",
                       "Hutch","Lever","CommLink","Display","Pipe","Chain","AutoTutor",
                       "Winch","Spray","ObjectDispenser","Token","PressCake","BioMass","VatMaggot","Moss","Mold","MossSeed","MoldSpore","Bloom","Sprout","Sprout2","SickBloom",
                       "PoisonBloom","Bush","PoisonBush","EncrustedBush","Test","EncrustedPoisonBush","Chemical","Spawner","Explosion")

        options = []
        for key,value in itemMap.items():
            if key in excludeList and not self.godMode:
                continue
            options.append((value,key))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.produceSelection
        self.targetItemType = None

    '''
    trigger production of the selected item
    '''
    def produceSelection(self):
        if not self.targetItemType:
            self.targetItemType = self.submenue.selection
            if self.targetItemType == src.items.Machine:
                options = []
                for key,value in itemMap.items():
                    options.append((key,key))
                self.submenue = src.interaction.SelectionMenu("select the item the machine should produce",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.produceSelection
                self.targetMachineItemType = None
                return
            if self.targetItemType == src.items.ResourceTerminal:
                options = []
                for key,value in itemMap.items():
                    options.append((key,key))
                self.submenue = src.interaction.SelectionMenu("select resource the terminal is for",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.produceSelection
                self.targetMachineItemType = None
                return

        if self.targetItemType == src.items.Machine:
            self.targetMachineItemType = self.submenue.selection
        if self.targetItemType == src.items.ResourceTerminal:
            self.targetResourceType = self.submenue.selection

        if self.targetItemType:
            self.produce(self.targetItemType)

    '''
    produce an item
    '''
    def produce(self,itemType,resultType=None):

        if not self.godMode:
            # gather a metal bar
            metalBar = None
            if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
                for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                    if isinstance(item,src.items.itemMap["MetalBars"]):
                       metalBar = item
                       break
            
            # refuse production without resources
            if not metalBar:
                self.character.addMessage("no metal bars available - place a metal bar to left/west")
                return

            targetFull = False
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 0:
                    targetFull = True

            if targetFull:
                self.character.addMessage("the target area is full, the machine does not produce anything")
                return

            if self.charges:
                self.charges -= 1
            else:
                self.coolDownTimer = src.gamestate.gamestate.tick

            self.character.addMessage("you produce a %s"%(itemType.type,))

            # remove resources
            self.room.removeItem(item)

        # spawn new item
        new = itemType(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if self.godMode:
            if itemType == src.items.GrowthTank:
                new.filled = True
            if itemType == src.items.GooFlask:
                new.uses = 100
            if itemType == src.items.GooDispenser:
                new.charges = 100
            if itemType == src.items.Machine:
                new.setToProduce(self.targetMachineItemType)
            if itemType == src.items.ResourceTerminal:
                new.setResource(self.targetResourceType)
            if itemType == src.items.GooFaucet:
                new.balance = 10000
            if itemType == src.items.ResourceTerminal:
                new.balance = 1000

        self.container.addItems([new])

    def getRemainingCooldown(self):
        return self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)

    def getLongInfo(self):
        text = """
item: ProductionArtwork

description:
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This machine can build almost anything, but is very slow.

Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(self.coolDown,)

        coolDownLeft = self.getRemainingCooldown()
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

"""

        return text

'''
scrap to metal bar converter
'''
class ScrapCompactor(Item):
    type = "ScrapCompactor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scrap compactor",creator=None,noId=False):
        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.commands = {}
        
        super().__init__(src.canvas.displayChars.scrapCompactor,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges","level"])

    '''
    produce a metal bar
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.container:
            character.addMessage("this machine has be somewhere to be used")
            return

        jobOrder = None
        for item in character.inventory:
            if item.type == "JobOrder" and not item.done and item.tasks[-1]["task"] == "produce" and item.tasks[-1]["toProduce"] == "MetalBars":
                jobOrder = item
                break

        # fetch input scrap
        scrap = None
        if not hasattr(self,"container"):
            if self.room:
                self.container = self.room
            else:
                self.container = self.terrain

        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition,self.zPosition)):
            if isinstance(item,itemMap["Scrap"]):
                scrap = item
                break
        if self.level > 1:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition+1,self.zPosition)):
                    if isinstance(item,itemMap["Scrap"]):
                        scrap = item
                        break
        if self.level > 2:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1,self.zPosition)):
                    if isinstance(item,itemMap["Scrap"]):
                        scrap = item
                        break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            self.runCommand("cooldown",character)
            return

        # refuse to produce without resources
        if not scrap:
            character.addMessage("no scraps available")
            self.runCommand("material Scrap",character)
            return

        targetPos = (self.xPosition+1,self.yPosition,self.zPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            self.runCommand("targetFull",character)
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        character.addMessage("you produce a metal bar")

        if jobOrder:
            if len(jobOrder.tasks) > 1:
                jobOrder.tasks.pop()
            else:
                jobOrder.done = True

        # remove resources
        if scrap.amount <= 1:
            self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.setWalkable()

        # spawn the metal bar
        new = src.items.itemMap["MetalBars"](creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.container.addItems([new])

        self.runCommand("success",character)

    def getLongInfo(self):
        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text = """
item: ScrapCompactor

description:
This machine converts scrap into metal bars. Metal bars are a form of metal that can be used to produce other things.

Place scrap to the %s of the machine and activate it 

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(directions,self.coolDown,)

        coolDownLeft = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges

"""

        text += """
thie is a level %s item

"""%(self.level)
        return text

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "runCommand":
            options = []
            for itemType in self.commands:
                options.append((itemType,itemType))
            self.submenue = src.interaction.SelectionMenu("Run command for producing item. select item to produce.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.runCommand
        elif self.submenue.selection == "addCommand":
            options = []
            options.append(("success","set success command"))
            options.append(("cooldown","set cooldown command"))
            options.append(("targetFull","set target full command"))
            options.append(("material Scrap","set Scrap fetching command"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1,self.zPosition)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character):
        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]

class PavingGenerator(Item):
    type = "PavingGenerator"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="paving generator",creator=None,noId=False):
        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.commands = {}
        
        super().__init__("PG",xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges","level"])

    '''
    produce a paving
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.container:
            character.addMessage("this machine has be somewhere to be used")
            return

        # fetch input scrap
        scrap = None
        if not hasattr(self,"container"):
            if self.room:
                self.container = self.room
            else:
                self.container = self.terrain

        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition,self.zPosition)):
            if isinstance(item,itemMap["Scrap"]):
                scrap = item
                break
        if self.level > 1:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition+1,self.zPosition)):
                    if isinstance(item,itemMap["Scrap"]):
                        scrap = item
                        break
        if self.level > 2:
            if not scrap:
                for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1,self.zPosition)):
                    if isinstance(item,itemMap["Scrap"]):
                        scrap = item
                        break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            self.runCommand("cooldown",character)
            return

        # refuse to produce without resources
        if not scrap:
            character.addMessage("no scraps available")
            self.runCommand("material Scrap",character)
            return

        targetPos = (self.xPosition+1,self.yPosition,self.zPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            self.runCommand("targetFull",character)
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        character.addMessage("you produce a paving")

        # remove resources
        if scrap.amount <= 1:
            self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.setWalkable()

        for i in range(1,4):
            # spawn the metal bar
            new = src.items.itemMap["Paving"](creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            self.container.addItems([new])

        self.runCommand("success",character)

    def getLongInfo(self):
        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text = """
item: ScrapCompactor

description:
This machine converts scrap into metal bars. Metal bars are a form of metal that can be used to produce other things.

Place scrap to the %s of the machine and activate it 

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(directions,self.coolDown,)

        coolDownLeft = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges

"""

        text += """
thie is a level %s item

"""%(self.level)
        return text

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "runCommand":
            options = []
            for itemType in self.commands:
                options.append((itemType,itemType))
            self.submenue = src.interaction.SelectionMenu("Run command for producing item. select item to produce.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.runCommand
        elif self.submenue.selection == "addCommand":
            options = []
            options.append(("success","set success command"))
            options.append(("cooldown","set cooldown command"))
            options.append(("targetFull","set target full command"))
            options.append(("material Scrap","set Scrap fetching command"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1,self.zPosition)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character):
        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]


'''
'''
class Scraper(Item):
    type = "Scraper"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="scraper",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        
        super().__init__(src.canvas.displayChars.scraper,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        # remove resources
        self.room.removeItem(item)

        # spawn scrap
        new = itemMap["Scrap"](self.xPosition,self.yPosition,1,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.room.addItems([new])

    def getLongInfo(self):
        text = """
item: Scrapper

description:
A scrapper shreds items to scrap.

Place an item to the west and activate the scrapper to shred an item.

"""
        return text

class Mover(Item):
    type = "Mover"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mover",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

    '''
    '''
    def apply(self,character,resultType=None):
        if self.xPosition == None:
            character.addMessage("this machine needs to be placed to be used")
            return

        super().apply(character,silent=True)

        # fetch input scrap
        itemFound = None
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
            itemFound = item
            break

        if not itemFound:
            character.addMessage("nothing to be moved")
            return

        # remove resources
        self.container.removeItem(itemFound)

        targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        items = self.container.getItemByPosition((self.xPosition+1,self.yPosition))
        if new.walkable:
            if len(items) > 15:
                targetFull = True
            for item in items:
                if item.walkable == False:
                    targetFull = True
        else:
            if len(items) > 1:
                targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.container.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Mover

description:
A mover moves items

Place the item or items to the west of the mover.
activate the mover to move one item to the east of the mover.

"""
        return text


'''
'''
class Sorter(Item):
    type = "Sorter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sorter",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        
        super().__init__(src.canvas.displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input scrap
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                itemFound = item
                break

        compareItemFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                compareItemFound = item
                break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return
        if not compareItemFound:
            character.addMessage("no compare items available")
            return

        # remove resources
        self.room.removeItem(itemFound)

        if itemFound.type == compareItemFound.type:
            targetPos = (self.xPosition,self.yPosition+1)
        else:
            targetPos = (self.xPosition+1,self.yPosition)

        itemFound.xPosition = targetPos[0]
        itemFound.yPosition = targetPos[1]


        targetFull = False
        new = itemFound
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: Sorter

description:
A sorter can sort items.

To sort item with a sorter place the item you want to compare against on the north.
Place the item or items to be sorted on the west of the sorter.
Activate the sorter to sort an item.
Matching items will be moved to the south and non matching items will be moved to the east.

"""
        return text

'''
'''
class AutoScribe(Item):
    type = "AutoScribe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="auto scribe",creator=None,noId=False):
        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.level = 1
        
        super().__init__(src.canvas.displayChars.sorter,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","level"])

    '''
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        # fetch input command or Note
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in ["Command","Note","JobOrder"]:
                    itemFound = item
                    break

        sheetFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type in ["Sheet"]:
                    sheetFound = item
                    break

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # refuse to produce without resources
        if not itemFound:
            character.addMessage("no items available")
            return
        if not sheetFound:
            character.addMessage("no sheet available")
            return

        # remove resources
        self.room.removeItem(sheetFound)
        self.room.removeItem(itemFound)

        # spawn new item
        if itemFound.type == "Command":
            new = Command(creator=self)
            new.command = itemFound.command
        elif itemFound.type == "Note":
            new = Note(creator=self)
            new.text = itemFound.text
        elif itemFound.type == "BluePrint":
            new = BluePrint(creator=self)
            new.setToProduce(itemFound.endProduct)
        elif itemFound.type == "JobOrder":
            new = JobOrder(creator=self)
            new.macro = itemFound.macro
            new.command = itemFound.command
            new.toProduce = itemFound.toProduce
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if itemFound.type == "Command":
            new.name = itemFound.name
            new.description = itemFound.description

        if hasattr(itemFound,"level"):
            newLevel = min(itemFound.level,sheetFound.level,self.level)
            new.level = newLevel

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if new.walkable:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 1:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        self.room.addItems([new])
        itemFound.xPosition = self.xPosition
        itemFound.yPosition = self.yPosition + 1
        self.room.addItems([itemFound])

    def getLongInfo(self):
        text = """
item: AutoScribe

description:
A AutoScribe copies commands.

The command to copy has to be placed to the west of the machine.
A sheet has to be placed to the north of the machine.
The copy of the command will be outputted to the east.
The original command will be outputted to the south.

The level of the copied command is the minimum level of the input command, sheet and the auto scribe itself.

This is a level %s item

"""%(self.level)
        return text

'''
'''
class Token(Item):
    type = "Token"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="token",creator=None,noId=False,tokenType="generic",payload=None):
        super().__init__(src.canvas.displayChars.token,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.tokenType = tokenType
        self.payload = payload

        self.attributesToStore.extend([
                "tokenType","payload"])

    def getLongInfo(self):
        text = """
A token. Only has value in the eyes of the beholder.

"""
        return text

'''
'''
class VatMaggot(Item):
    type = "VatMaggot"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="vat maggot",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.vatMaggot,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character,resultType=None):

        # remove resources
        character.addMessage("you consume the vat maggot")
        character.satiation += 1
        character.frustration -= 25
        if self.xPosition and self.yPosition:
            if self.room:
                self.room.removeItem(self)
            elif self.terrain:
                self.terrain.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)
        if (src.gamestate.gamestate.tick%5 == 0):
            character.addMessage("you wretch")
            character.satiation -= 25
            character.frustration += 75
            character.addMessage("you wretch from eating a vat magot")

        super().apply(character,silent=True)

    def getLongInfo(self):
        text = """
A vat maggot is the basis for food.

You can eat it, but it may kill you. Activate it to eat it.

Can be processed into bio mass by a maggot fermenter.

"""
        return text


'''
'''
class Sheet(Item):
    type = "Sheet"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="sheet",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sheet,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.recording = False
        self.character = None

        self.level = 1

        self.attributesToStore.extend([
                "recording","level"])

    def getLongInfo(self):
        text = """
A sheet. Simple building material and use to store information.

Can be used to create a Note or a written command directly from the sheet.
Activate the sheet to get a selection, whether to create a command or a note.

To create a note select the "create note" option and type the text of the note.
Press enter to finish entering the text.

To create a command from a sheet. select the the "create command" option.
There are two ways to enter the command.

The first option is to record a new command.
After activating this option you will start to record your actions.
Activate the sheet again to create to command and to stop recording.

The second option ist to store a command from an existing macro buffer.
Activate this option and select the macro buffer to create the command.

Sheets are also needed as resource to create a blueprint in the blueprinter machine.

Sheets can be produced from metal bars.

This is a level %s item

%s

"""%(self.level,self.type,)
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        if self.recording:
            self.createCommand()
            return

        if isinstance(character,src.characters.Monster):
            return

        self.character = character

        options = []
        options.append(("createCommand","create a written command"))
        options.append(("createNote","create a note"))
        options.append(("createMap","create a map"))
        options.append(("createJobOrder","create a job order"))
        self.submenue = src.interaction.SelectionMenu("What do you want do do?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSwitch

    def actionSwitch(self):
        if self.submenue.selection == "createNote":
            self.createNote()
        elif self.submenue.selection == "createCommand":
            self.createCommand()
        elif self.submenue.selection == "createMap":
            self.createMapItem()
        elif self.submenue.selection == "createJobOrder":
            self.createJobOrder()

    def createNote(self):
        self.submenue = src.interaction.InputMenu("type the text you want to write on the note")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createNoteItem

    def createNoteItem(self):

        note = Note(self.xPosition,self.yPosition, creator=self)
        note.setText(self.submenue.text)

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([note])
            else:
                self.container.removeItem(self)
                self.container.addItems([note])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(note)

    def createMapItem(self):

        mapItem = Map(self.xPosition,self.yPosition, creator=self)

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([mapItem])
            else:
                self.container.removeItem(self)
                self.container.addItems([mapItem])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(mapItem)

    def createJobOrder(self):

        jobOrder = JobOrder(self.xPosition,self.yPosition, creator=self)

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([jobOrder])
            else:
                self.container.removeItem(self)
                self.container.addItems([jobOrder])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(jobOrder)

    def createCommand(self):

        if not self.character:
            return

        if not len(self.character.macroState["macros"]):
            self.character.addMessage("no macro found - record a macro to be able to write a command")
        
        if self.recording:
            convertedCommand = []
            convertedCommand.append(("-",["norecord"]))
            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

            if not "a" in self.character.macroState["macros"]:
                self.character.addMessage("no macro found in buffer \"a\"")
                return

            if self.xPosition:
                self.character.macroState["macros"]["a"] = self.character.macroState["macros"]["a"][:-1]
            else:
                counter = 1
                while not self.character.macroState["macros"]["a"][-counter] == "i":
                    counter += 1
                self.character.macroState["macros"]["a"] = self.character.macroState["macros"]["a"][:-counter]
            self.storeMacro("a")
            self.recording = False
            del self.character.macroState["macros"]["a"]
            return

        options = []
        options.append(("record","start recording (records to buffer + reapply to create command)"))
        options.append(("store","store macro from memory"))
        self.submenue = src.interaction.SelectionMenu("select how to get the commands content",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeSelect

    def storeSelect(self):
        if self.submenue.selection == "record":
            self.recordAndstore()
        elif self.submenue.selection == "store":
            self.storeFromMacro()

    def recordAndstore(self):
        self.recording = True
        convertedCommand = []
        convertedCommand.append(("-",["norecord"]))
        convertedCommand.append(("a",["norecord"]))
        self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]

    def storeFromMacro(self):
        self.recording = True

        options = []
        for key,value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/"+keystroke+"/"
            options.append((key,key+" - "+compressedMacro))

        self.submenue = src.interaction.SelectionMenu("select the macro you want to store",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeMacro


    def storeMacro(self,key=None):
        if not key:
            key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return

        command = Command(self.xPosition,self.yPosition, creator=self)
        command.setPayload(self.character.macroState["macros"][key])

        self.character.addMessage("you created a written command")

        if self.xPosition:
            if self.room:
                self.room.removeItem(self)
                self.room.addItems([command])
            else:
                self.container.removeItem(self)
                self.container.addItems([command])
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(command)

'''
'''
class Note(Item):
    type = "Note"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Note",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.note,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.text = ""

        self.attributesToStore.extend([
                "text"])

    def getLongInfo(self):

        text = """
A Note. It has a text on it. You can activate it to read it.

it holds the text:

"""+self.text+"""

"""
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        submenue = src.interaction.OneKeystrokeMenu("the note has the text: \n\n\n%s"%(self.text,))
        character.macroState["submenue"] = submenue

    def setText(self,text):
        self.text = text

'''
'''
class Map(Item):
    type = "Map"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Map",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.map,xPosition,yPosition,name=name,creator=creator)

        self.routes = {
                      }
        self.nodes = []
        self.walkable = True
        self.bolted = False
        self.recording = False
        self.recordingStart = None
        self.macroBackup = None

        self.markers = {}

        self.attributesToStore.extend([
                "text","recording","nodes","routes",])

    def apply(self,character):
        super().apply(character,silent=True)

        options = []
        options.append(("walkRoute","walk route"))
        options.append(("showRoutes","show routes"))
        options.append(("showAvailableRoutes","show available routes"))
        options.append(("addMarker","add marker"))
        options.append(("addRoute","add route"))
        options.append(("addNode","add node"))
        options.append(("abort","abort"))
        self.character = character
        self.submenue = src.interaction.SelectionMenu("where do you want to do?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.selectActivity
        self.macroBackup = self.character.macroState["macros"].get("auto")

    def getReachableNodes(self,node):
        if not node in self.routes:
            return []

        nodes = []
        for exitNode in self.routes.keys():
            if exitNode == node:
                continue
            if exitNode in self.routes and node in self.routes[exitNode]:
                nodes.append(exitNode)
                pass

        return nodes

    def selectActivity(self):
        if self.submenue.selection == "walkRoute":
            self.walkRouteSelect()
        if self.submenue.selection == "showRoutes":
            text = "routes:\n"
            for (startNode,routePart) in self.routes.items():
                for (endNode,route) in routePart.items():
                    text += "%s => %s (%s)\n"%(startNode,endNode,route,)
            self.submenue = src.interaction.TextMenu(text)
            self.character.macroState["submenue"] = self.submenue
        elif self.submenue.selection == "addMarker":
            self.addMarker()
        elif self.submenue.selection == "addRoute":
            self.addRoute()
        elif self.submenue.selection == "addNode":
            self.addNode()
        else:
            self.submenue = None
            self.character = None

    def addRoute(self):
        pos = (self.character.xPosition,self.character.yPosition,self.character.zPosition)
        items = self.character.container.getItemByPosition(pos)

        node = None
        for item in items:
            if isinstance(item,src.items.PathingNode):
                node = item.nodeName

        if not self.recording:
            self.character.addMessage("walk the path to the target and activate this menu item again")
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"]),("auto",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            if node:
                self.recordingStart = node
            else:
                self.recordingStart = pos
            self.recording = True
        else:
            self.character.macroState["commandKeyQueue"] = [("-",["norecord"])]+self.character.macroState["commandKeyQueue"] 
            self.recording = None
            if not self.macroBackup:
                return
            if not self.recordingStart in self.routes:
                self.routes[self.recordingStart] = {}
            if self.xPosition:
                counter = 2
            else:
                counter = 1
                while not self.macroBackup[-counter] == "i":
                    counter += 1
            if node:
                recordingEnd = node
            else:
                recordingEnd = pos
            self.routes[self.recordingStart][recordingEnd] = self.macroBackup[:-counter]
            del self.character.macroState["macros"]["auto"]
            self.character.addMessage("added path from %s to %s"%(self.recordingStart,recordingEnd))
            self.recordingStart = None

    def addMarker(self):
        items = self.character.container.getItemByPosition((self.character.xPosition,self.character.yPosition))
        for item in items:
            if isinstance(item,src.items.FloorPlate):
                self.markers[(self.character.xPosition,self.character.yPosition)] = item.name
                break

    def walkRouteSelect(self):
        charPos = (self.character.xPosition,self.character.yPosition)

        if not charPos in self.routes:
            self.character.addMessage("no routes found for this position")
            return

        options = []
        for target in self.routes[charPos].keys():
            if target in self.markers:
                target = self.markers[target]
            options.append((target,str(target)))
        options.append(("abort","abort"))
        self.submenue = src.interaction.SelectionMenu("where do you want to go?",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.walkRoute

    def walkRoute(self):
        if self.submenue.selection == "abort":
            return
        charPos = (self.character.xPosition,self.character.yPosition)
        path = self.routes[charPos][self.submenue.selection]
        convertedPath = []
        for step in path:
            convertedPath.append((step,["norecord"]))
        self.character.macroState["commandKeyQueue"] = convertedPath + self.character.macroState["commandKeyQueue"]
        self.character.addMessage("you walk the path")

    def getLongInfo(self):

        text = """
item: Map

description:
A map is a collection of routes.

You can select the routes and run the stored route.

"""
        return text


'''
'''
class Command(Item):
    type = "Command"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Command",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.command,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.command = ""
        self.extraName = ""
        self.description = None
        self.level = 1

        self.attributesToStore.extend([
                "command","extraName","level","description"])

    def getLongInfo(self):
        compressedMacro = ""
        for keystroke in self.command:
            if len(keystroke) == 1:
                compressedMacro += keystroke
            else:
                compressedMacro += "/"+keystroke+"/"

        text = """
item: Command

description:
A command. A command is written on it. Activate it to run command.

"""
        text += """

This is a level %s item.
"""%(self.level)

        if self.name:
            text += """
name: %s"""%(self.name)
        if self.description and len(self.description) > 0:
            text += """

description:\n%s"""%(self.description)
        text += """

it holds the command:

%s

"""%(compressedMacro)
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        if isinstance(character,src.characters.Monster):
            return

        if self.level == 1:
            self.runPayload(character)
        else:
            options = [("runCommand","run command"),
                       ("setName","set name"),]
            if self.level > 2:
                options.append(("setDescription","set description"))
            if self.level > 3:
                options.append(("rememberCommand","store command in memory"))

            self.submenue = src.interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.advancedActions
            self.character = character
            pass

    def advancedActions(self):
        if self.submenue.selection == "runCommand":
            self.runPayload(self.character)
        elif self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("Enter the name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName
        elif self.submenue.selection == "setDescription":
            self.submenue = src.interaction.InputMenu("Enter the description")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setDescription
        elif self.submenue.selection == "rememberCommand":

            if not self.name or self.name == "":
                self.character.addMessage("command not loaded: command has no name")
                return

            properName = True
            for char in self.name[:-1]:
                if not (char.isupper() or char == " "):
                    properName = False
                    break
            if self.name[-1].isupper():
                properName = False
                pass

            if properName:
                self.character.macroState["macros"][self.name] = self.command
                self.character.addMessage("loaded command to macro storage")
            else:
                self.character.addMessage("command not loaded: name not in propper format. Should be capital letters except the last letter. example \"EXAMPLE NAMe\"")
        else:
            self.character.addMessage("action not found")

    def setName(self):
        self.name = self.submenue.text
        self.character.addMessage("set command name to %s"%(self.name))

    def setDescription(self):
        self.description = self.submenue.text
        self.character.addMessage("set command description")

    def runPayload(self,character):
        convertedCommand = []
        for item in self.command:
            convertedCommand.append((item,["norecord"]))
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def setPayload(self,command):
        import copy
        self.command = copy.deepcopy(command)

    def getDetailedInfo(self):
        if self.extraName == "":
            return super().getDetailedInfo()+" "
        else:
            return super().getDetailedInfo()+" - "+self.extraName

class CommandBook(Item):
    type = "CommandBook"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="command book",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.command,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        totalCommands = 0

        self.contents = []

        self.attributesToStore.extend([
                "contents"])

    def getState(self):
        state = super().getState()
        try:
            state["contents"] = self.availableChallenges
            state["knownBlueprints"] = self.knownBlueprints
        except:
            pass
        return state

class JobBoard(Item):
    type = "JobBoard"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="job board",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.jobBoard,xPosition,yPosition,name=name,creator=creator)

        self.todo = []

        self.bolted = False
        self.walkable = False

    def getLongInfo(self):
        text = """
item: JobBoard

description:
Stores a collection of job board. Serving as a todo list.

"""
        return text

    def apply(self,character):
        options = [("addJobOrder","add job order"),("getSolvableJobOrder","get solvable job order"),("getJobOrder","get job order")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "addJobOrder":
            itemFound = None
            for item in self.character.inventory:
                if item.type == "JobOrder":
                    itemFound = item
                    break

            if not itemFound:
                self.character.addMessage("no job order found")
                return

            if itemFound.done:
                self.character.inventory.remove(itemFound)
                return

            self.todo.append(itemFound)
            self.character.inventory.remove(itemFound)
            self.character.addMessage("job order added")
        elif self.submenue.selection == "getSolvableJobOrder":

            if len(self.character.inventory) > 9:
                self.character.addMessage("no space in inventory")
                return

            itemFound = None
            for jobOrder in self.todo:
                if jobOrder.macro in self.character.macroState["macros"]:
                   itemFound = jobOrder 
                   break

            if not itemFound:
                self.character.addMessage("no fitting job order found")
                return

            self.todo.remove(jobOrder)
            self.character.inventory.append(jobOrder)
            self.character.addMessage("you take a job order")

        elif self.submenue.selection == "getJobOrder":
            if not self.todo:
                self.character.addMessage("no job order on job board")
            elif len(self.character.inventory) > 9:
                self.character.addMessage("inventory not empty")
            else:
                self.character.inventory.append(self.todo.pop())
                self.character.addMessage("you take a job order from the job board")
        else:
            self.character.addMessage("noption not found")

class TransportInNode(Item):
    type = "TransportInNode"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport In Node",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        if not (character.xPosition == self.xPosition and character.yPosition == self.yPosition+1):
            character.addMessage("item has to be activated from south")
            return

        position = (self.xPosition,self.yPosition-1)
        items = self.container.getItemByPosition(position)
        if not items:
            character.addMessage("no items to fetch")
            return

        itemToMove = items[0]

        self.container.removeItem(itemToMove)
        character.inventory.append(itemToMove)
        character.addMessage("you take an item")

    def fetchSpecialRegisterInformation(self):
        result = {}

        position = (self.xPosition,self.yPosition-1)
        result["NUM ITEMs"] = len(self.container.getItemByPosition(position))
        return result

class TransportOutNode(Item):
    type = "TransportOutNode"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport Out Node",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        if not character.inventory:
            character.addMessage("no items in inventory")
            return

        toDrop = character.inventory[-1]

        if not self.xPosition:
            character.addMessage("this machine needs to be placed to be used")
            return

        position = (self.xPosition,self.yPosition+1)
        items = self.container.getItemByPosition(position)
        if len(items) > 9:
            character.addMessage("not enough space on dropoff point (south)")

        toDrop.xPosition = self.xPosition
        toDrop.yPosition = self.yPosition+1
        character.inventory.remove(toDrop)
        self.container.addItems([toDrop])
        character.addMessage("you take a item")

    def fetchSpecialRegisterInformation(self):
        result = {}

        position = (self.xPosition,self.yPosition+1)
        result["NUM ITEMs"] = len(self.container.getItemByPosition(position))
        return result

class TransportContainer(Item):
    type = "TransportContainer"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport Container",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False
        
    def apply(self,character):
        options = [("addItems","load item"),
                   ("transportItem","transport item"),
                   ("getJobOrder","set transport command")
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        # add item
        # remove item
        # transport item
        # set transport command
        pass

class UniformStockpileManager(Item):
    type = "UniformStockpileManager"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="uniform stockpile manager",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.uniformStockpileManager,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

        self.storedItemType = None
        self.storedItemWalkable = None
        self.restrictStoredItemType = True
        self.restrictStoredItemWalkable = True
        self.numItemsStored = 0
        self.lastAction = ""

        self.attributesToStore.extend([
                "numItemsStored","storedItemType","storedItemWalkable","restrictStoredItemType","restrictStoredItemWalkable"])
        self.objectsToStore.extend(["submenue","character"])

        self.commands = {}
        self.submenue = None
        self.character = None
        self.blocked = False

    def getLongInfo(self):

        text = """
item: UniformStockpileManager

description:
needs to be placed in the center of a tile. The tile should be emtpy and mold free for proper function.

lastAction: %s

commands: %s

storedItemType: %s
storedItemWalkable: %s
restrictStoredItemType: %s
restrictStoredItemWalkable: %s

"""%(self.lastAction,self.commands,self.storedItemType,self.storedItemWalkable,self.restrictStoredItemType,self.restrictStoredItemWalkable)
        return text

    def apply(self,character):
        if not (character.xPosition == self.xPosition and character.yPosition == self.yPosition-1):
            character.addMessage("this item can only be used from north")
            return

        if self.blocked:
            character.runCommandString("Js")
            character.addMessage("item blocked - auto retry")
            return
        self.blocked = True
        self.lastAction = "apply"

        options = [("storeItem","store item"),("fetchItem","fetch item")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"apply2"}
        self.character = character

    def configure(self,character):
        if self.blocked:
            character.runCommandString("sc")
            character.addMessage("item blocked - auto retry")
            return
        self.blocked = True

        self.lastAction = "configure"

        self.submenue = src.interaction.OneKeystrokeMenu("""
a: addCommand
s: machine settings
j: run job order
r: reset
""")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        self.lastAction = "configure2"

        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order")
                self.blocked = False
                return

            self.character.addMessage("do job order stuff")
            jobOrder = self.character.jobOrders[-1]
            self.character.addMessage(jobOrder.getTask())
            if jobOrder.getTask()["task"] == "generateStatusReport":
                self.character.runCommandString("se.")
                jobOrder.popTask()
            self.character.addMessage(jobOrder.getTask())
            if jobOrder.getTask()["task"] == "configure machine":
                self.character.addMessage("configured machine")
                task = jobOrder.popTask()
                self.commands.update(task["commands"])
            self.blocked = False
            return

        if self.submenue.keyPressed == "a":
            options = []
            options.append(("empty","set empty command"))
            options.append(("full","set full command"))
            options.append(("wrong","wrong item type or item"))

            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand
            return
        if self.submenue.keyPressed == "s":
            options = []
            options.append(("restrictStoredItemType","restict stored item type"))
            options.append(("storedItemType","stored item type"))
            options.append(("restrictStoredItemWalkable","restict item size"))
            options.append(("storedItemWalkable","stored item size"))

            self.submenue = src.interaction.SelectionMenu("select setting to change.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setMachineSettings
            self.settingType = None
            return
        if self.submenue.keyPressed == "r":
            self.character.addMessage("you reset the machine")
            self.storedItemType = None
            self.storedItemWalkable = False
            self.restrictStoredItemType = False
            self.restrictStoredItemWalkable = True
            self.numItemsStored = 0
            return
        self.blocked = False

    def setMachineSettings(self):
        if self.settingType == None:
            self.settingType = self.submenue.selection

            self.submenue = src.interaction.InputMenu("input the value")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setMachineSettings


        rawValue = self.submenue.text
        if self.settingType == "restrictStoredItemType":
            if rawValue == "True":
                self.restrictStoredItemType = True
            else:
                self.restrictStoredItemType = False
        if self.settingType == "storedItemType":
            self.storedItemType = rawValue
        if self.settingType == "restrictStoredItemWalkable":
            if rawValue == "True":
                self.restrictStoredItemWalkable = True
            else:
                self.restrictStoredItemWalkable = False
        if self.settingType == "restrictStoredItemType":
            self.storedItemWalkable = bool(rawValue)

        self.blocked = False

    def runCommand(self,commandName):
        if not commandName in self.commands:
            return
        command = self.commands[commandName]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
        self.character.addMessage("running command for trigger: %s - %s"%(commandName,command))

    def setCommand(self):
        self.lastAction = "setCommand"
        trigger = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            self.blocked = False
            return

        self.commands[trigger] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(trigger,commandItem.command))
        self.blocked = False
        return


    def apply2(self):
        self.lastAction = "apply2"

        if self.submenue.selection == "storeItem":
            if not self.character.inventory:
                self.character.addMessage("nothing in inventory")
                self.blocked = False
                return

            if self.restrictStoredItemType:
                if self.storedItemType == None:
                    self.storedItemType = self.character.inventory[-1].type
                else:
                    if not self.storedItemType == self.character.inventory[-1].type:
                        self.character.addMessage("wrong item type")
                        self.runCommand("wrong")
                        self.runCommand("wrongType")
                        self.blocked = False
                        return
            if self.restrictStoredItemWalkable:
                if self.storedItemWalkable == None:
                    self.storedItemWalkable = self.character.inventory[-1].walkable
                else:
                    if not (self.storedItemWalkable == self.character.inventory[-1].walkable):
                        self.character.addMessage("wrong size")
                        self.runCommand("wrong")
                        self.runCommand("wrong size")
                        self.blocked = False
                        return

            if (self.xPosition%15 == 7 and self.yPosition%15 == 7):
                if self.numItemsStored >= 140:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                sector = self.numItemsStored//35
                offsetX = 6-self.numItemsStored%35%6-1
                offsetY = 6-self.numItemsStored%35//6-1

                command = ""
                if sector == 0:
                    command += str(offsetY)+"w"
                    command += str(offsetX)+"a"
                    command += "La"
                    command += str(offsetX)+"d"
                    command += str(offsetY)+"s"
                elif sector == 1:
                    command += str(offsetY)+"w"
                    command += str(offsetX)+"d"
                    command += "Ld"
                    command += str(offsetX)+"a"
                    command += str(offsetY)+"s"
                elif sector == 2:
                    command += "assd"
                    command += str(offsetY)+"s"
                    command += str(offsetX)+"a"
                    command += "La"
                    command += str(offsetX)+"d"
                    command += str(offsetY)+"w"
                    command += "dwwa"
                elif sector == 3:
                    command += "assd"
                    command += str(offsetY)+"s"
                    command += str(offsetX)+"d"
                    command += "Ld"
                    command += str(offsetX)+"a"
                    command += str(offsetY)+"w"
                    command += "dwwa"
            elif (self.xPosition%15 in (6,8,) and self.yPosition%15 in (6,8)):
                if self.numItemsStored >= 32:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                row = self.numItemsStored//6

                if (self.xPosition%15 == 6 and self.yPosition%15 == 6):
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = ""
                    commandEnd = ""
                elif (self.xPosition%15 == 8 and self.yPosition%15 == 6):
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = ""
                    commandEnd = ""
                elif (self.xPosition%15 == 6 and self.yPosition%15 == 8):
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = "dssa"
                    commandEnd = "awwd"
                elif (self.xPosition%15 == 8 and self.yPosition%15 == 8):
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = "assd"
                    commandEnd = "dwwa"

                if row < 4:
                    command += str(3-row)+rowMovUp
                    command += str(5-self.numItemsStored%6)+colMovUp+"L"+rowMovUp
                    command += str(5-self.numItemsStored%6)+colMovDown
                    command += str(3-row)+rowMovDown
                elif self.numItemsStored >= 24 and self.numItemsStored < 28:
                    command += str(4-(self.numItemsStored-24)%4)+colMovUp+"L"+colMovUp
                    command += str(4-(self.numItemsStored-24)%4)+colMovDown
                elif self.numItemsStored >= 28 and self.numItemsStored < 32:
                    command += colMovUp+rowMovDown+str(3-(self.numItemsStored-28)%4)+colMovUp+"L"+colMovUp
                    command += str(3-(self.numItemsStored-28)%4)+colMovDown+rowMovUp+colMovDown
                command += commandEnd
            else:
                command = ""
                pass

            self.numItemsStored += 1

            self.character.runCommandString(command)
            self.character.addMessage("running command to store item %s"%(command))
            self.blocked = False
            return

        if self.submenue.selection == "fetchItem":
            if not self.numItemsStored:
                self.character.addMessage("stockpile empty")
                self.runCommand("empty")
                self.blocked = False
                return

            if len(self.character.inventory) == 10:
                self.character.addMessage("inventory full")
                self.blocked = False
                return

            self.numItemsStored -= 1

            if (self.xPosition%15 == 7 and self.yPosition%15 == 7):
                sector = self.numItemsStored//35
                offsetX = 6-self.numItemsStored%35%6-1
                offsetY = 6-self.numItemsStored%35//6-1

                command = ""
                if sector == 0:
                    command += str(offsetY)+"w"
                    command += str(offsetX)+"a"
                    command += "Ka"
                    command += str(offsetX)+"d"
                    command += str(offsetY)+"s"
                elif sector == 1:
                    command += str(offsetY)+"w"
                    command += str(offsetX)+"d"
                    command += "Kd"
                    command += str(offsetX)+"a"
                    command += str(offsetY)+"s"
                elif sector == 2:
                    command += "assd"
                    command += str(offsetY)+"s"
                    command += str(offsetX)+"a"
                    command += "Ka"
                    command += str(offsetX)+"d"
                    command += str(offsetY)+"w"
                    command += "dwwa"
                elif sector == 3:
                    command += "assd"
                    command += str(offsetY)+"s"
                    command += str(offsetX)+"d"
                    command += "Kd"
                    command += str(offsetX)+"a"
                    command += str(offsetY)+"w"
                    command += "dwwa"

            elif (self.xPosition%15 in (6,8,) and self.yPosition%15 in (6,8)):
                if self.numItemsStored >= 32:
                    self.character.addMessage("stockpile full")
                    self.runCommand("full")
                    self.blocked = False
                    return

                row = self.numItemsStored//6

                if (self.xPosition%15 == 6 and self.yPosition%15 == 6):
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = ""
                    commandEnd = ""
                elif (self.xPosition%15 == 8 and self.yPosition%15 == 6):
                    rowMovUp = "w"
                    rowMovDown = "s"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = ""
                    commandEnd = ""
                elif (self.xPosition%15 == 6 and self.yPosition%15 == 8):
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "a"
                    colMovDown = "d"
                    command = "dssa"
                    commandEnd = "dwwa"
                elif (self.xPosition%15 == 8 and self.yPosition%15 == 8):
                    rowMovUp = "s"
                    rowMovDown = "w"
                    colMovUp = "d"
                    colMovDown = "a"
                    command = "assd"
                    commandEnd = "awwd"

                if row < 4:
                    command += str(3-row)+rowMovUp
                    command += str(5-self.numItemsStored%6)+colMovUp+"K"+rowMovUp
                    command += str(5-self.numItemsStored%6)+colMovDown
                    command += str(3-row)+rowMovDown
                elif self.numItemsStored >= 24 and self.numItemsStored < 28:
                    command += str(4-(self.numItemsStored-24)%4)+colMovUp+"K"+colMovUp
                    command += str(4-(self.numItemsStored-24)%4)+colMovDown
                elif self.numItemsStored >= 28 and self.numItemsStored < 32:
                    command += colMovUp+rowMovDown+str(3-(self.numItemsStored-28)%4)+colMovUp+"K"+colMovUp
                    command += str(3-(self.numItemsStored-28)%4)+colMovDown+rowMovUp+colMovDown
                command += commandEnd
            else:
                pass

            convertedCommand = []
            for char in command:
                convertedCommand.append((char,"norecord"))

            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
            self.character.addMessage("running command to fetch item")
            self.blocked = False
            return
        self.blocked = False
        return

    def fetchSpecialRegisterInformation(self):
        result = super().fetchSpecialRegisterInformation()
        result["numItemsStored"] = self.numItemsStored
        result["storedItemType"] = self.storedItemType
        result["storedItemWalkable"] = self.storedItemWalkable
        result["restrictStoredItemType"] = self.restrictStoredItemType
        result["restrictStoredItemWalkable"] = self.restrictStoredItemWalkable
        if (self.xPosition%15 == 7 and self.yPosition%15 == 7):
            result["maxAmount"] = 6*6*4
        elif (self.xPosition%15 in (6,8,) and self.yPosition%15 in (6,8)):
            result["maxAmount"] = 4*6+2*4
        else:
            result["maxAmount"] = 0
        return result

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]

class TypedStockpileManager(Item):
    type = "TypedStockpileManager"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="typed stockpile manager",creator=None,noId=False):

        self.freeItemSlots = {}

        self.freeItemSlots[1] = []
        self.freeItemSlots[2] = []
        self.freeItemSlots[3] = []
        self.freeItemSlots[4] = []

        for x in range(1,7):
            for y in range(1,7):
                if x == 7 or y == 7:
                    continue
                if y in (2,5,9,12):
                    continue
                if x in (6,8) and y in (6,8):
                    continue
                self.freeItemSlots[1].append((x,y))

        for x in range(1,7):
            for y in range(7,14):
                if x == 7 or y == 7:
                    continue
                if y in (2,5,9,12):
                    continue
                if x in (6,8) and y in (6,8):
                    continue
                self.freeItemSlots[2].append((x,y))

        for x in range(7,14):
            for y in range(1,7):
                if x == 7 or y == 7:
                    continue
                if y in (2,5,9,12):
                    continue
                if x in (6,8) and y in (6,8):
                    continue
                self.freeItemSlots[3].append((x,y))

        for x in range(7,14):
            for y in range(7,14):
                if x == 7 or y == 7:
                    continue
                if y in (2,5,9,12):
                    continue
                if x in (6,8) and y in (6,8):
                    continue
                self.freeItemSlots[4].append((x,y))

        self.slotsByItemtype = {}
        super().__init__(src.canvas.displayChars.typedStockpileManager,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def configure(self,character):
        self.submenue = src.interaction.OneKeystrokeMenu("what do you want to do?\n\nj: use job order")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character
    
    def configure2(self):
        if not self.character.jobOrders:
            return

        jobOrder = self.character.jobOrders[-1]

        if jobOrder.getTask()["task"] == "generateStatusReport":
            self.character.runCommandString("se.")
            jobOrder.popTask()

    def getLongInfo(self):

        text = """
item: TypedStockpileManager

description:
needs to be placed in the center of a tile. The tile should be emtpy and mold free for proper function.

slotsByItemtype
%s
"""%(self.slotsByItemtype,)
        return text

    def apply(self,character):
        if not (character.xPosition == self.xPosition and character.yPosition == self.yPosition-1):
            character.addMessage("this item can only be used from north")
            return

        options = [("storeItem","store item"),("fetchItem","fetch item"),("fetchByJobOrder","fetch by job order")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "storeItem":
            if not self.freeItemSlots:
                self.character.addMessage("no free item slot")
                return

            if not self.character.inventory:
                self.character.addMessage("no item in inventory")
                return

            for (key,value) in self.freeItemSlots.items():
                if not value:
                    continue

                slot = value.pop()
                if not self.character.inventory[-1].type in self.slotsByItemtype:
                    self.slotsByItemtype[self.character.inventory[-1].type] = []
                self.slotsByItemtype[self.character.inventory[-1].type].append((slot,key))
                break

            command = ""
            if slot[1] < 7:
                if slot[1] in (6,4):
                    command += "w"
                elif slot[1] in (3,1):
                    command += "4w"
                if slot[0] < 7:
                    command += str(7-slot[0])+"a"
                else:
                    command += str(slot[0]-7)+"d"
                command += "L"
                if slot[1] in (1,4):
                    command += "w"
                elif slot[1] in (3,6):
                    command += "s"
                if slot[0] < 7:
                    command += str(7-slot[0])+"d"
                else:
                    command += str(slot[0]-7)+"a"
                if slot[1] in (6,4):
                    command += "s"
                elif slot[1] in (3,1):
                    command += "4s"
            else:
                command += "assd"
                if slot[1] in (8,10):
                    command += "s"
                elif slot[1] in (11,13):
                    command += "4s"
                if slot[0] < 7:
                    command += str(7-slot[0])+"a"
                else:
                    command += str(slot[0]-7)+"d"
                command += "L"
                if slot[1] in (8,11):
                    command += "w"
                elif slot[1] in (10,13):
                    command += "s"
                if slot[0] < 7:
                    command += str(7-slot[0])+"d"
                else:
                    command += str(slot[0]-7)+"a"
                if slot[1] in (8,10):
                    command += "w"
                elif slot[1] in (11,13):
                    command += "4w"
                command += "dwwa"

            convertedCommand = []
            for char in command:
                convertedCommand.append((char,"norecord"))

            self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
            self.character.addMessage("running command to store item %s"%(command))

        if self.submenue.selection == "fetchItem":
            options = []
            for key in self.slotsByItemtype.keys():
                options.append((key,key))
            self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.fetchItem

        if self.submenue.selection == "fetchByJobOrder":
            jobOrder = None
            for item in self.character.inventory:
                if item.type == "JobOrder" and not item.done and item.tasks[-1]["task"] == "place":
                    jobOrder = item
                    break

            if not jobOrder: 
                self.character.addMessage("no job order found")
                return

            if jobOrder.tasks[-1]["toPlace"] not in self.slotsByItemtype:
                self.character.addMessage("no "+item.type+" in storage")

                jobOrder.tasks.append(
                    {
                    "task":"produce",
                    "toProduce":item.tasks[-1]["toPlace"],
                    "macro":"PRODUCE "+item.tasks[-1]["toPlace"].upper()[:-1]+item.tasks[-1]["toPlace"][-1].lower(),
                    "command":None
                    })
                return
            self.submenue.selection = item.tasks[-1]["toPlace"]
            self.fetchItem()
            return

    def fetchItem(self):

        if self.submenue.selection == None:
            return

        if not self.slotsByItemtype[self.submenue.selection]:
            self.character.addMessage("no item to fetch")
            return

        slotTuple = self.slotsByItemtype[self.submenue.selection].pop()
        slot = slotTuple[0]
        if not self.slotsByItemtype[self.submenue.selection]:
            del self.slotsByItemtype[self.submenue.selection]
        self.freeItemSlots[slotTuple[1]].append(slot)

        if not slot:
            self.character.addMessage("no item to fetch")
            return

        command = ""
        if slot[1] < 7:
            if slot[1] in (6,4):
                command += "w"
            elif slot[1] in (3,1):
                command += "4w"
            if slot[0] < 7:
                command += str(7-slot[0])+"a"
            else:
                command += str(slot[0]-7)+"d"
            command += "K"
            if slot[1] in (1,4):
                command += "w"
            elif slot[1] in (3,6):
                command += "s"
            if slot[0] < 7:
                command += str(7-slot[0])+"d"
            else:
                command += str(slot[0]-7)+"a"
            if slot[1] in (6,4):
                command += "s"
            elif slot[1] in (3,1):
                command += "4s"
        else:
            command += "assd"
            if slot[1] in (8,10):
                command += "s"
            elif slot[1] in (11,13):
                command += "4s"
            if slot[0] < 7:
                command += str(7-slot[0])+"a"
            else:
                command += str(slot[0]-7)+"d"
            command += "K"
            if slot[1] in (8,11):
                command += "w"
            elif slot[1] in (10,13):
                command += "s"
            if slot[0] < 7:
                command += str(7-slot[0])+"d"
            else:
                command += str(slot[0]-7)+"a"
            if slot[1] in (8,10):
                command += "w"
            elif slot[1] in (11,13):
                command += "4w"
            command += "dwwa"

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        self.character.macroState["commandKeyQueue"] = convertedCommand + self.character.macroState["commandKeyQueue"]
        self.character.addMessage("running command to fetch item %s"%(command))

    def fetchSpecialRegisterInformation(self):
        result = super().fetchSpecialRegisterInformation()
        for itemType in self.slotsByItemtype.keys():
            result["num "+str(itemType)+" stored"] = len(self.slotsByItemtype[itemType])
        numFreeSlots = 0
        for (key,itemSlot) in self.freeItemSlots.items():
            numFreeSlots += len(itemSlot)
        result["num free slots"] = numFreeSlots
        maxAmount = 0
        if self.xPosition%15 in (6,8) and self.yPosition%15 in (6,8):
            maxAmount = 23
        if (self.xPosition%15,self.yPosition%15) == (7,7):
            maxAmount = 23*4
        result["max amount"] = maxAmount
        return result

    def getState(self):
        state = super().getState()
        state["slotsByItemtype"] = self.slotsByItemtype

        convertedFreeItemSlots = {}
        for (key,value) in self.freeItemSlots.items():
            convertedFreeItemSlots[key] = []
            for value2 in value:
                convertedFreeItemSlots[key].append(list(value2))
        state["freeItemSlots"] = convertedFreeItemSlots

        return state

    def setState(self,state):
        super().setState(state)
        if "slotsByItemtype" in state:
            self.slotsByItemtype = state["slotsByItemtype"]

        if "freeItemSlots" in state:
            self.freeItemSlots = {}
            for (key,value) in state["freeItemSlots"].items():
                self.freeItemSlots[key] = []
                for value2 in value:
                    self.freeItemSlots[key].append(tuple(value2))

'''
'''
class Paving(Item):
    type = "Paving"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="floor plate",creator=None,noId=False):
        super().__init__(";;",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Paving

description:
Used as building material for roads

"""
        return text


'''
'''
class FloorPlate(Item):
    type = "FloorPlate"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="floor plate",creator=None,noId=False):
        super().__init__("::",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.name = "test"

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
Used as building material and can be used to mark paths

"""
        return text

    def apply(self, character):
        self.character = character
        #self.addText()
        if not self.bolted:
            character.addMessage("you fix the floor plate int the ground")
            self.bolted = True

    def addText(self):
        self.submenue = src.interaction.InputMenu("Enter the name")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.setName

    def setName(self):
        self.name = self.character.macroState["submenue"].text

    def getLongInfo(self):
        text = """
item: FloorPlate

description:
%s

"""%(self.name)
        return text

'''
'''
class Rod(Item):
    type = "Rod"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="rod",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.rod,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.baseDamage = 6
        self.attributesToStore.extend([
               "baseDamage",
               ])

    def getLongInfo(self):
        text = """
item: Rod

description:
A rod. Simple building material.

baseDamage:
%s

"""%(self.baseDamage,)
        return text

    def apply(self,character):
        character.weapon = self
        self.container.removeItem(self)

'''
'''
class Armor(Item):
    type = "Armor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="armor",creator=None,noId=False):
        super().__init__("ar",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.armorValue = random.randint(1,5)
        self.damageType = "attacked"

    def getArmorValue(self,damageType):
        if damageType == self.damageType:
            return self.armorValue
        return 0

    def getLongInfo(self):
        text = """
item: Armor

armorvalue:
%s

description:
protects you in combat

"""%(self.armorValue,)
        return text

    def apply(self,character):
        character.armor = self
        self.container.removeItem(self)

'''
'''
class Mount(Item):
    type = "Mount"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="mount",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.nook,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A mount. Simple building material.

"""
        return text

'''
'''
class Stripe(Item):
    type = "Stripe"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stripe",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.stripe,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Stripe

description:
A Stripe. Simple building material.

"""
        return text

'''
'''
class Bolt(Item):
    type = "Bolt"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bolt",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bolt,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Bolt

description:
A Bolt. Simple building material.

"""
        return text

'''
'''
class Radiator(Item):
    type = "Radiator"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="radiator",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.coil,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Radiator

description:
A radiator. Simple building material.

"""
        return text

'''
'''
class Tank(Item):
    type = "Tank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tank",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.tank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Tank

description:
A tank. Building material.

"""
        return text

'''
'''
class Heater(Item):
    type = "Heater"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="heater",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.heater,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Heater

description:
A heater. Building material.

"""
        return text

'''
'''
class Connector(Item):
    type = "Connector"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="connector",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.connector,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Connector

description:
A connector. Building material.

"""
        return text


'''
'''
class Puller(Item):
    type = "puller"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="puller",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.puller,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
A puller. Building material.

"""
        return text

'''
'''
class Pusher(Item):
    type = "pusher"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pusher",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pusher,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Pusher

description:
A pusher. Building material.

"""
        return text

'''
'''
class Frame(Item):
    type = "Frame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Frame",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.frame,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: Frame

description:
A frame. Building material.

"""
        return text

'''
'''
class Tree(Item):
    type = "Tree"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tree",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.tree,xPosition,yPosition,name=name,creator=creator)

        import random

        self.bolted = True
        self.walkable = False
        self.maxMaggot = random.randint(75,150)
        self.numMaggots = 0

        try:
            self.lastUse = src.gamestate.gamestate.tick
        except:
            self.lastUse = -100000

        self.attributesToStore.extend([
               "maggot","maxMaggot","lastUse"])

    def regenerateMaggots(self):
        self.numMaggots += (src.gamestate.gamestate.tick-self.lastUse)//100
        self.numMaggots = min(self.numMaggots,self.maxMaggot)

    def apply(self,character):

        if not self.terrain:
            character.addMessage("The tree has to be on the outside to be used")
            return

        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        character.addMessage("you harvest a vat maggot")
        character.frustration += 1

        targetFull = False
        targetPos = (self.xPosition+1,self.yPosition)
        if targetPos in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[targetPos]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[targetPos]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not work")
            return

        if not self.numMaggots:
            character.addMessage("The tree has no maggots left")
            return

        # spawn new item
        self.numMaggots -= 1
        new = VatMaggot(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        text = """
item: Tree

numMaggots: %s

description:
A tree can be used as a source for vat maggots.

Activate the tree to harvest a vat maggot.

"""%(self.numMaggots,)
        return text

'''
'''
class BioMass(Item):
    type = "BioMass"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bio mass",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bioMass,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation += 200
        if character.satiation > 1000:
            character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the bio mass")

    def getLongInfo(self):
        text = """
item: BioMass

description:
A bio mass is basis for food production.

Can be processed into press cake by a bio press.
"""
        return text

'''
'''
class PressCake(Item):
    type = "PressCake"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="press cake",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pressCake,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def getLongInfo(self):
        text = """
item: PressCake

description:
A press cake is basis for food production.

Can be processed into goo by a goo producer.
"""
        return text

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the press cake and gain 1000 satiation")

'''
'''
class GameTestingProducer(Item):
    type = "GameTestingProducer"

    def __init__(self,xPosition=None,yPosition=None, name="testing producer",creator=None, seed=0, possibleSources=[], possibleResults=[],noId=False):
        self.coolDown = 20
        self.coolDownTimer = -self.coolDown

        super().__init__(src.canvas.displayChars.gameTestingProducer,xPosition,yPosition,name=name,creator=creator)

        self.seed = seed
        self.baseName = name
        self.possibleResults = possibleResults
        self.possibleSources = possibleSources
        #self.change_apply_2(force=True)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer"])

    def apply(self,character,resultType=None):

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        token = None
        for item in character.inventory:
            if isinstance(item,src.items.Token):
                token = item

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        if token:
            self.change_apply_1(character,token)
        else:
            self.produce_apply(character)

    def change_apply_1(self,character,token):
        options = [(("yes",character,token),"yes"),(("no",character,token),"no")]
        self.submenue = src.interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.change_apply_2

    def change_apply_2(self,force=False):
        if not force:
            if self.submenue.selection[0] == "no":
                return
            character = self.submenue.selection[1]
            token = self.submenue.selection[2]
            character.inventory.remove(token)

        seed = self.seed

        self.resource = None
        while not self.resource:
            self.product = self.possibleResults[seed%23%len(self.possibleResults)]
            self.resource = self.possibleSources[seed%len(self.possibleSources)]
            seed += 3+(seed%7)
            if self.product == self.resource:
                self.resource = None

        self.seed += self.seed%107
                    
        self.description = self.baseName + " | " + str(self.resource.type) + " -> " + str(self.product.type) 

    def produce_apply(self,character):

        # gather the resource
        itemFound = None
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if isinstance(item,self.resource):
                   itemFound = item
                   break
        
        # refuse production without resources
        if not itemFound:
            character.addMessage("no "+self.resource.type+" available")
            return

        # remove resources
        self.room.removeItem(item)

        # spawn new item
        new = self.product(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.room.addItems([new])

        super().apply(character,silent=True)

    def getLongInfo(self):
        text = """
item: GameTestingProducer

description:
A game testing producer. It produces things.

Place metalbars to left/west and activate the machine to produce.

"""
        return text

'''
'''
class MachineMachine(Item):
    type = "MachineMachine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="machine machine",creator=None,noId=False):
        self.coolDown = 1000
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1

        self.endProducts = {
        }
        self.blueprintLevels = {
        }

        super().__init__(src.canvas.displayChars.machineMachine,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","endProducts","charges","level"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character,resultType=None):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        options = []
        options.append(("blueprint","load blueprint"))
        options.append(("produce","produce machine"))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.basicSwitch
        self.character = character


    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.OneKeystrokeMenu("what do you want to do?\n\nc: add command\nj: run job order")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order found")
                return

            jobOrder = self.character.jobOrders[-1]
            task = jobOrder.popTask()

            if task["task"] == "produce machine":
                self.produce(task["type"])

    def basicSwitch(self):
        selection = self.character.macroState["submenue"].getSelection() 
        if selection == "blueprint":
            self.addBlueprint()
        elif selection == "produce":
            self.productionSwitch()

    def addBlueprint(self):
        blueprintFound = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type in ["BluePrint"]:
                    blueprintFound = item
                    break

        if not blueprintFound:
            self.character.addMessage("no blueprint found above/north")
            return

        self.endProducts[blueprintFound.endProduct] = blueprintFound.endProduct
        if not blueprintFound.endProduct in self.blueprintLevels:
            self.blueprintLevels[blueprintFound.endProduct] = 0
        if self.blueprintLevels[blueprintFound.endProduct] < blueprintFound.level:
            self.blueprintLevels[blueprintFound.endProduct] = blueprintFound.level

        self.character.addMessage("blueprint for "+blueprintFound.endProduct+" inserted")
        self.room.removeItem(blueprintFound)

    def productionSwitch(self):

        if self.endProducts == {}:
            self.character.addMessage("no blueprints available.")
            return

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            self.character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return

        options = []
        for itemType in self.endProducts:
            options.append((itemType,itemType+" machine"))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.produceSelection

    '''
    trigger production of the selected item
    '''
    def produceSelection(self):
        self.produce(self.submenue.selection)

    '''
    produce an item
    '''
    def produce(self,itemType,resultType=None):

        if not self.container:
            if self.room:
                self.container = self.room
            elif self.terrain:
                self.container = self.terrain

        # gather a metal bar
        resourcesNeeded = ["MetalBars"]

        resourcesFound = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in resourcesNeeded:
                   resourcesFound.append(item)
                   resourcesNeeded.remove(item.type)
        
        # refuse production without resources
        if resourcesNeeded:
            self.character.addMessage("missing resources: %s"%(",".join(resourcesNeeded)))
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
            if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 0:
                targetFull = True

        if targetFull:
            self.character.addMessage("the target area is full, the machine does not produce anything")
            return
        else:
            self.character.addMessage("not full")

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        self.character.addMessage("you produce a machine that produces %s"%(itemType,))

        # remove resources
        for item in resourcesFound:
            self.room.removeItem(item)

        # spawn new item
        new = Machine(creator=self)
        new.productionLevel = self.blueprintLevels[itemType]
        new.setToProduce(itemType)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if hasattr(new,"coolDown"):
            new.coolDown = random.randint(new.coolDown,int(new.coolDown*1.25))

        self.room.addItems([new])

    def getState(self):
        state = super().getState()
        state["endProducts"] = self.endProducts
        state["blueprintLevels"] = self.blueprintLevels
        return state

    def setState(self,state):
        super().setState(state)
        self.endProducts = state["endProducts"]
        self.blueprintLevels = state["blueprintLevels"]

    def getLongInfo(self):
        text = """
item: MachineMachine

description:
This machine produces machines that build machines. It needs blueprints to do that.

You can load blueprints into this machine.
Prepare by placing a blueprint to the above/north of this machine.
After activation select "load blueprint" and the blueprint will be added.

You can produce machines for blueprints that were added.
Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.

After using this machine you need to wait %s ticks till you can use this machine again.
"""%(self.coolDown,)

        coolDownLeft = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

"""

        if len(self.endProducts):
            text += """
This machine has blueprints for:

"""
            for itemType in self.endProducts:
                text += "* %s\n"%(itemType)
            text += "\n"
        else:
            text += """
This machine cannot produce anything since there were no blueprints added to the machine

"""
        return text

'''
'''
class Machine(Item):
    type = "Machine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Machine",creator=None,seed=0,noId=False):
        self.toProduce = "Wall"

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.productionLevel = 1
        self.commands = {}

        super().__init__(src.canvas.displayChars.machine,xPosition,yPosition,name=name,creator=creator,seed=seed)

        self.attributesToStore.extend([
               "toProduce","level","productionLevel"])

        self.baseName = name

        self.attributesToStore.extend([
               "coolDown","coolDownTimer","charges"])

        self.setDescription()
        self.resetDisplay()

    def setDescription(self):
        self.description = self.baseName+" MetalBar -> %s"%(self.toProduce,)

    def resetDisplay(self):
        chars = "X\\"
        display = (src.interaction.urwid.AttrSpec("#aaa","black"),chars)
        toProduce = self.toProduce
        colorMap2_1 = { 
                    "Wall":"#f88",
                    "Stripe":"#f88",
                    "Case":"#f88",
                    "Frame":"#f88",
                    "Rod":"#f88",
                    "Connector":"#8f8",
                    "Mount":"#8f8",
                    "RoomBuilder":"#8f8",
                    "MemoryCell":"#8f8",
                    "Door":"#8f8",
                    "puller":"#88f",
                    "Bolt":"#88f",
                    "pusher":"#88f",
                    "Heater": "#88f",
                    "Radiator": "#88f",
                    "GooProducer": "#8ff",
                    "AutoScribe": "#8ff",
                    }
        colorMap2_2 = { 
                    "Wall":"#a88",
                    "Stripe":"#8a8",
                    "Case":"#88a",
                    "Frame":"#8aa",
                    "Rod":"#a8a",
                    "Connector":"#a88",
                    "Mount":"#8a8",
                    "RoomBuilder":"#88a",
                    "MemoryCell":"#8aa",
                    "Door":"#a8a",
                    "puller":"#a88",
                    "Bolt":"#8a8",
                    "pusher":"#88a",
                    "Heater": "#8aa",
                    "Radiator": "#a8a",
                    "GooProducer": "#a88",
                    "AutoScribe": "#8a8",
                    }

        if toProduce in colorMap2_1:
            display = [(src.interaction.urwid.AttrSpec(colorMap2_1[toProduce],"black"),"X"),(src.interaction.urwid.AttrSpec(colorMap2_2[toProduce],"black"),"\\")]
        self.display = display

    def setToProduce(self,toProduce):
        self.toProduce = toProduce
        self.setDescription()
        self.resetDisplay()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.xPosition:
            character.addMessage("this machine has to be placed to be used")
            return

        if not self.container:
            if self.room:
                self.container = self.room
            elif self.terrain:
                self.container = self.terrain

        #if not self.room:
        #    character.addMessage("this machine can only be used within rooms")
        #    return

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown and not self.charges:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            self.runCommand("cooldown",character)
            return

        if self.toProduce in rawMaterialLookup:
            resourcesNeeded = rawMaterialLookup[self.toProduce][:]
        else:
            resourcesNeeded = ["MetalBars"]

        # gather a metal bar
        resourcesFound = []
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition,self.zPosition)):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)
        
        for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition,self.zPosition)):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)
        
        # refuse production without resources
        if resourcesNeeded:
            character.addMessage("missing resources (place left/west or up/north): %s"%(", ".join(resourcesNeeded)))
            self.runCommand("material %s"%(resourcesNeeded[0]),character)
            return

        targetFull = False
        new = itemMap[self.toProduce](creator=self)

        itemList = self.container.getItemByPosition((self.xPosition+1,self.yPosition,self.zPosition))
        if itemList:
            if new.walkable:
                if len(self.container.getItemByPosition((self.xPosition+1,self.yPosition,self.zPosition))) > 15:
                    targetFull = True
                for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition,self.zPosition)):
                    if item.walkable == False:
                        targetFull = True
            else:
                if len(self.container.getItemByPosition((self.xPosition+1,self.yPosition,self.zPosition))) > 0:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            self.runCommand("targetFull",character)
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        character.addMessage("you produce a %s"%(self.toProduce,))

        # remove resources
        for item in resourcesFound:
            self.container.removeItem(item)

        # spawn new item
        new = itemMap[self.toProduce](creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        if hasattr(new,"coolDown"):
            new.coolDown = round(new.coolDown*(1-(0.05*(self.productionLevel-1))))

            new.coolDown = random.randint(new.coolDown,int(new.coolDown*1.25))

        self.container.addItems([new])

        if hasattr(new,"level"):
            new.level = self.level

        self.runCommand("success",character)

    def getLongInfo(self):
        coolDownLeft = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)

        text = """
item: Machine

description:
This Machine produces %s.

Prepare for production by placing the input materials to the west/left/noth/top of this machine.
Activate the machine to produce.

After using this machine you need to wait %s ticks till you can use this machine again.

this is a level %s item and will produce level %s items.

"""%(self.toProduce,self.coolDown,self.level,self.level)

        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

"""%(coolDownLeft,)
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges 

"""%(self.charges)
        else:
            text += """
Currently the machine has no charges 

"""

        return text

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.OneKeystrokeMenu("what do you want to do?\n\nc: add command\nj: run job order")
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order found")
                return

            jobOrder = self.character.jobOrders[-1]
            task = jobOrder.popTask()
            if not task:
                self.character.addMessage("no task left")
                return

            if task["task"] == "configure machine":
                for (commandName,command) in task["commands"].items():
                    self.commands[commandName] = command

        elif self.submenue.keyPressed == "c":
            options = []
            options.append(("success","set success command"))
            options.append(("cooldown","set cooldown command"))
            options.append(("targetFull","set target full command"))

            if self.toProduce in rawMaterialLookup:
                resourcesNeeded = rawMaterialLookup[self.toProduce][:]
            else:
                resourcesNeeded = ["MetalBars"]

            for itemType in resourcesNeeded:
                options.append(("material %s"%(itemType,),"set %s fetching command"%(itemType,)))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1,self.zPosition)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character):
        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]
        self.setDescription()
        self.resetDisplay()

'''
'''
class Drill(Item):
    type = "Drill"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Drill",creator=None,noId=False):

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.isBroken = False
        self.isCleaned = True

        self.baseName = name

        super().__init__(src.canvas.displayChars.drill,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "coolDown","coolDownTimer",
                "isBroken","isCleaned"])

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.isBroken:
            addition = " (broken)"
        self.description = self.baseName+addition

    def setToProduce(self,toProduce):
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.xPosition:
            character.addMessage("this machine has to be placed to be used")
            return

        if self.room:
            character.addMessage("this machine can not be used in rooms")
            return

        if self.isBroken:
            if not self.isCleaned:

                targetFull = False
                scrapFound = None
                if (self.xPosition,self.yPosition+1) in self.terrain.itemByCoordinates:
                    if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]) > 15:
                        targetFull = True
                    for item in self.terrain.itemByCoordinates[(self.xPosition,self.yPosition+1)]:
                        if item.walkable == False:
                            targetFull = True
                        if item.type == "Scrap":
                            scrapFound = item

                if targetFull:
                    character.addMessage("the target area is full, the machine does not produce anything")
                    return

                character.addMessage("you remove the broken rod")

                if scrapFound:
                    item.amount += 1
                else:
                    # spawn new item
                    new = itemMap["Scrap"](self.xPosition,self.yPosition,1,creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition+1
                    new.bolted = False

                    self.terrain.addItems([new])

                self.isCleaned = True

            else:

                character.addMessage("you repair the machine")

                rod = None
                if (self.xPosition-1,self.yPosition) in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                        if isinstance(item,Rod):
                           rod = item
                           break
                
                # refuse production without resources
                if not rod:
                    character.addMessage("needs repairs Rod -> repaired")
                    character.addMessage("no rod available")
                    return

                # remove resources
                self.terrain.removeItem(item)

                self.isBroken = False

            self.setDescription()
            return

        if src.gamestate.gamestate.tick < self.coolDownTimer+self.coolDown:
            character.addMessage("cooldown not reached. Wait %s ticks"%(self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer),))
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # spawn new item
        possibleProducts = [src.items.itemMap["Scrap"],src.items.itemMap["Coal"],src.items.itemMap["Scrap"],src.items.itemMap["Radiator"],src.items.itemMap["Scrap"],src.items.itemMap["Mount"],src.items.itemMap["Scrap"],src.items.itemMap["Sheet"],src.items.itemMap["Scrap"],src.items.itemMap["Rod"],src.items.itemMap["Scrap"],src.items.itemMap["Bolt"],src.items.itemMap["Scrap"],src.items.itemMap["Stripe"],src.items.itemMap["Scrap"],]
        productIndex = src.gamestate.gamestate.tick%len(possibleProducts)
        new = possibleProducts[productIndex](self.xPosition,self.yPosition,creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        foundScrap = None
        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True
                if item.type == "Scrap":
                    foundScrap = item

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        if new.type == "Scrap" and foundScrap:
            foundScrap.amount += new.amount
        else:
            self.terrain.addItems([new])

        self.isBroken = True
        self.isCleaned = False

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
This drills items from the ground. You get different things from time to time.

Activate the drill to drill something up. Most likely you will dig up scrap.

After the every use the rod in the drill will break.
You need to replace the rod in the drill to repair it.
Use the drill to eject the broken rod from the drill.
place a rod to the left/west of the drill and activate the drill, to repair it

"""
        return text

class MemoryDump(Item):
    type = "MemoryDump"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryDump",creator=None,noId=False):

        self.macros = None

        self.baseName = name

        super().__init__(src.canvas.displayChars.memoryDump,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    def setToProduce(self,toProduce):
        self.setDescription()

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        import copy
        if not self.macros == None:
            character.addMessage("you overwrite your macros with the ones in your memory dump")
            character.macroState["macros"] = copy.deepcopy(self.macros)
            self.macros = None
        else:
            character.addMessage("you dump your macros in the memory dump")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class MemoryBank(Item):
    type = "MemoryBank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryBank",creator=None,noId=False):

        self.macros = {}

        self.baseName = name

        super().__init__(src.canvas.displayChars.memoryBank,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.macros:
            addition = " (imprinted)"
        self.description = self.baseName+addition

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        import copy
        if self.macros:
            character.addMessage("you overwrite your macros with the ones in your memory bank")
            character.macroState["macros"] = copy.deepcopy(self.macros)
        else:
            character.addMessage("you store your macros in the memory bank")
            self.macros = copy.deepcopy(character.macroState["macros"])

        self.setDescription()

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

'''
'''
class MemoryStack(Item):
    type = "MemoryStack"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryStack",creator=None,noId=False):

        self.macros = []

        super().__init__(src.canvas.displayChars.memoryStack,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        options = []

        options.append(("p","push macro on stack"))
        options.append(("l","load/pop macro from stack"))

        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

        self.character = character

    '''
    '''
    def doAction(self):

        import copy
        if self.submenue.getSelection() == "p":
            self.character.addMessage("push your macro onto the memory stack")
            self.macros.append(copy.deepcopy(self.character.macroState["macros"]))
            self.character.addMessage(self.macros)
        elif self.submenue.getSelection() == "l":
            self.character.addMessage("you load a macro from the memory stack")
            self.character.macroState["macros"] = copy.deepcopy(self.macros.pop())
            self.character.addMessage(self.character.macroState["macros"])
        else:
            self.character.addMessage("invalid option")

'''
'''
class MemoryReset(Item):
    type = "MemoryReset"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryStack",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.memoryReset,xPosition,yPosition,name=name,creator=creator)


    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        character.addMessage("you clear your macros")

        character.macroState["macros"] = {}
        character.registers = {}

'''
'''
class Engraver(Item):
    type = "Engraver"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Engraver",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.engraver,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        self.character = character

        if not self.text:
            character.addMessage("starting interaction")
            self.submenue = src.interaction.InputMenu("Set the text to engrave")
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.setText
        else:
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                 self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)][0].customDescription = self.text

    '''
    trigger production of the selected item
    '''
    def setText(self):
        self.character.addMessage("stopping interaction")
        self.text = self.submenue.text
        self.submenue = None

class AutoTutor2(Item):
    type = "AutoTutor2"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="AutoTutor",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.infoscreen,xPosition,yPosition,name=name,creator=creator)

'''
'''
class AutoTutor(Item):
    type = "AutoTutor"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="AutoTutor",creator=None,noId=False):
        self.knownBlueprints = []
        self.knownInfos = []
        self.availableChallenges = {
                                   }


        super().__init__(src.canvas.displayChars.infoscreen,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None
        self.blueprintFound = False
        self.gooChallengeDone = False
        self.metalbarChallengeDone = False
        self.sheetChallengeDone = False
        self.machineChallengeDone = False
        self.blueprintChallengeDone = False
        self.commandChallengeDone = False
        self.energyChallengeDone = False
        self.activateChallengeDone = False
        self.activateChallenge = 100
        self.metalbarChallenge = 100
        self.wallChallenge = 25
        self.autoScribeChallenge = 25
        self.challengeRun2Done = False
        self.challengeRun3Done = False
        self.challengeRun4Done = False
        self.challengeRun5Done = False
        self.initialChallengeDone = False
        self.challengeInfo = {}

        self.attributesToStore.extend([
               "gooChallengeDone","metalbarChallengeDone","sheetChallengeDone","machineChallengeDone","blueprintChallengeDone","energyChallengeDone","activateChallengeDone",
               "commandChallengeDone","challengeRun2Done","challengeRun3Done","challengeRun4Done","challengeRun5Done","initialChallengeDone",
               "activateChallenge","wallChallenge","autoScribeChallenge",
               "knownBlueprints","availableChallenges","knownInfos","challengeInfo"])

    def addScraps(self,amount=1):
        
        targetFull = False
        scrapFound = None
        itemList = self.container.getItemByPosition((self.xPosition,self.yPosition+1))
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True
            if item.type == "Scrap":
                scrapFound = item

        if targetFull:
            return False
        
        if scrapFound:
            scrapFound.amount += amount
            scrapFound.setWalkable()
        else:
            # spawn scrap
            new = src.items.itemMap["Scrap"](self.xPosition,self.yPosition,1,creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            new.amount = amount
            self.room.addItems([new])
            new.setWalkable()

        return True


    def apply(self,character):
        if not self.room:
            character.addMessage("can only be used within rooms")
            return
        super().apply(character,silent=True)

        self.character = character

        options = []

        options.append(("level1","check information"))
        options.append(("challenge","do challenge"))

        self.submenue = src.interaction.SelectionMenu("This is the automated tutor. Complete challenges and get information.\n\nwhat do you want do to?",options)

        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.step2

        self.character = character

    def step2(self):

        selection = self.submenue.getSelection()
        self.submenue = None

        if selection == "level1":
            self.basicInfo()
        elif selection == "challenge":
            self.challenge()
        elif selection == "level2":
            self.l2Info()
        elif selection == "level3":
            self.l3Info()
        elif selection == "level4":
            self.l4Info()
        else:
            self.character.addMessage("NOT ENOUGH ENERGY")

    def challenge(self):

        if not self.activateChallengeDone:
            if not self.initialChallengeDone:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: find the challenges\nstatus:challenge completed.\n\nReturn to this menu item and you will find more challenges.\nNew challenge \"pick up goo flask\"\n\n")
                self.initialChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.gooChallengeDone:
                if not self.checkInInventory(src.items.GooFlask):
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: pick up goo flask\nstatus: challenge in progress - Try again with a goo flask in your inventory.\n\ncomment:\nA goo flask is represnted by ò=. There should be some flasks in the room.\n\n")
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: pick up goo flask\nstatus: challenge completed.\n\ncomment:\nTry to always keep a goo flask with some charges in your inventory.\nIf you are hungry you will drink from it automatically.\nIf you do not drink regulary you will die.\n\nreward:\nNew information option on \"information->machines\"\nNew Information option on \"information->food\"\nNew challenge \"gather metal bars\"\n\n")
                    self.gooChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.metalbarChallengeDone:
                if not self.checkInInventory(src.items.MetalBars):
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: gather metal bars\nstatus: challenge in progress - Try again with a metal bar in your inventory.\n\ncomment: \nMetal bars are represented by ==\ncheck \"information->machines->metal bar production\" on how to produce metal bars.\n\n")
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: gather metal bars\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->simple item production\"\nNew challenge \"produce sheet\"\n\n")
                    self.metalbarChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.sheetChallengeDone:
                if not self.checkInInventoryOrInRoom(src.items.Sheet):
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce sheet\nstatus: challenge in progress - Try again with a sheet in your inventory.\n\ncomment: \ncheck \"information->machines->simple item production\" on how to produce simple items.\nA sheet machine should be within this room.\n\n")
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce sheet\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->machine production\"\nNew challenge \"produce rod machine\"\n\n")
                    self.sheetChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.machineChallengeDone:
                foundMachine = False
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if isinstance(item,src.items.Machine) and item.toProduce == "Rod":
                        foundMachine = True
                if not foundMachine:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce rod machine\nstatus: challenge in progress - Try again with a machine that produces rods in your inventory.\n\ncomment:\n\ncheck \"information->machines->machine production\" on how to produce machines.\nBlueprints for the basic materials including rods should be in this room.\nblueprints are represented by bb\n\n")
                else:
                    self.knownBlueprints.append("Frame")
                    self.knownBlueprints.append("Rod")
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce rod machine\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->machines->blueprint production\"\nNew information option on \"information->blueprint reciepes\"\nNew challenge \"produce blueprint for frame\"\n\n")
                    self.machineChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.blueprintChallengeDone:
                foundBluePrint = False
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if isinstance(item,src.items.BluePrint) and item.endProduct == "Frame":
                        foundBluePrint = True
                if not foundBluePrint:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce blueprint for frame\nstatus: challenge in progress - Try again with a blueprint for frame in your inventory.\n\ncomment: \ncheck \"information->machines->blueprint production\" on how to produce blueprints.\nThe reciepe for Frame is rod+metalbar\n\n")
                else:
                    self.knownBlueprints.append("Bolt")
                    self.knownBlueprints.append("Sheet")
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce blueprint for frame\nstatus: challenge completed.\n\nreward:\nNew information option on \"information->automation\"\nNew blueprint reciepe for bolt\nNew blueprint reciepe for sheet\nNew challenge \"create command\"\n\n")
                    self.blueprintChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.commandChallengeDone:
                if not self.checkInInventoryOrInRoom(src.items.Command):
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: create command\nstatus: challenge in progress - Try again with a command in your inventory.\n\ncomment: \ncheck \"information->automation->command creation\" on how to record commands.\n\n")
                else:
                    self.knownBlueprints.append("Stripe")
                    self.knownBlueprints.append("Mount")
                    self.knownBlueprints.append("Radiator")
                    self.submenue = src.interaction.TextMenu("\n\nchallenge completed.\n\nreward:\nNew information option on \"information->automation->multiplier\"\n\nreward:\nNew blueprint reciepe for stripe.\nNew blueprint reciepe for mount.\nNew blueprint reciepe for radiator.\nNew challenge \"repeat challenge\"\n\n")
                    self.commandChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.activateChallengeDone:
                if self.activateChallenge:
                    self.activateChallenge -= 1
                    if self.activateChallenge == 100:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: repeat challenge\n\nstatus: challenge in progress - Use this menu item a 100 times. The first step is done. Activations remaining %s\n\ncomment: use a command to activate the menu item and multipliers to do this often.\n check \"information->automation\" on how to do this."%(self.activateChallenge,))
                    else:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: challenge in progress - Use this menu item a 100 times. Activations remaining %s\n\ncomment: use a command to activate the menu item and multipliers to do this often"%(self.activateChallenge,))
                else:
                    if len(self.character.inventory):
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: in progress. Try again with empty inventory to complete.\n\n")
                    else:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: repeat challenge\nstatus: challenge completed.\n\ncomment:\nyou completed the first set of challenges\ncome back for more\n\nreward:\nNew blueprint reciepe for scrap compactor\nNew challenge \"produce scrap compactor\"\nNew challenge \"gather bloom\"\nNew challenge \"create note\"\n\n")
                        self.activateChallengeDone = True
                        self.knownBlueprints.append("ScrapCompactor")
                        self.availableChallenges = {
                                    "produceScrapCompactors":{"text":"produce scrap compactor"},
                                    "gatherBloom":{"text":"gather bloom"},
                                    "note":{"text":"create note"},
                                   }
                self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun2Done:
                if len(self.availableChallenges):
                    options = []
                    for (key,value) in self.availableChallenges.items():
                        options.append([key,value["text"]])

                    self.submenue = src.interaction.SelectionMenu("select the challenge to do:",options)
                    self.character.macroState["submenue"] = self.submenue
                    self.character.macroState["submenue"].followUp = self.challengeRun2
                else:
                    if self.metalbarChallenge:

                        metalBarFound = None
                        for item in self.character.inventory:
                            if isinstance(item,src.items.MetalBars):
                                metalBarFound = item
                                break

                        if not metalBarFound:
                            self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: no progress - Try again with metal bars in your inventory\nMetal bars remaining %s\n\n"%(self.metalbarChallenge,))
                            self.character.macroState["submenue"] = self.submenue
                            return

                        didAdd = self.addScraps(amount=1)
                        if not didAdd:
                            self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: no progress - no space to drop scrap\nMetal bars remaining %s\n\n"%(self.metalbarChallenge,))
                            self.character.macroState["submenue"] = self.submenue
                            return

                        self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress.\nMetal bars remaining %s\n\ncomment: \nscrap ejected to the south/below\nuse commands and multipliers to do this.\n\n"%(self.metalbarChallenge,))
                        self.character.inventory.remove(metalBarFound)
                        self.metalbarChallenge -= 1

                    else:
                        if len(self.character.inventory):
                            self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n")
                        else:
                            self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 100 metal bars\nstatus: challenge completed.\n\nreward:\nNew challenges added\nnew reciepes for Connector Pusher\n\n")
                            self.availableChallenges["differentBlueprints"] = {"text":"9 different blueprints"}
                            self.availableChallenges["9blooms"] = {"text":"9 blooms"}
                            self.availableChallenges["produceAdvanced"] = {"text":"produce items"}
                            self.availableChallenges["produceScraper"] = {"text":"scraper"}
                            self.challengeRun2Done = True
                            self.knownBlueprints.append("Connector")
                            self.knownBlueprints.append("Pusher")
                    self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun3Done:
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = src.interaction.SelectionMenu("select the challenge",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if self.wallChallenge:
                    wallFound = None
                    for item in self.character.inventory:
                        if isinstance(item,src.items.Wall):
                            wallFound = item
                            break

                    if not wallFound:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - try again with walls in inventory\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                        self.character.macroState["submenue"] = self.submenue
                        return

                    didAdd = self.addScraps(amount=2)
                    if not didAdd:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - no space to drop scrap\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                        self.character.macroState["submenue"] = self.submenue
                        return

                    self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"%(self.wallChallenge,))
                    self.character.inventory.remove(wallFound)
                    self.wallChallenge -= 1
                    self.character.macroState["submenue"] = self.submenue

                else:
                    if len(self.character.inventory):
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n")
                    else:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 25 walls\nstatus: challenge completed\n\n")
                        self.availableChallenges["produceBioMasses"] = {"text":"produce 9 bio mass"}
                        self.availableChallenges["createMap"] = {"text":"create map"}
                        self.availableChallenges["produceProductionManager"] = {"text":"produce production manager"}
                        self.challengeRun3Done = True
                        self.knownBlueprints.append("RoomBuilder")
                        self.knownBlueprints.append("FloorPlate")
                        self.knownBlueprints.append("ProductionManager")
                        self.knownBlueprints.append("MemoryCell")
                    self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun4Done: 
            self.character.addMessage("challenge run 4")
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = src.interaction.SelectionMenu("select the challenge",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if not self.challengeInfo:
                    self.challengeInfo = {"numSucesses":0,"type":None}

                if self.challengeInfo["numSucesses"] >= 25:
                    if self.character.inventory:
                        self.submenue = src.interaction.TextMenu("\n\nactivate with empty inventory to complete challenge.\n\n")
                        self.character.macroState["submenue"] = self.submenue
                    else:
                        self.submenue = src.interaction.TextMenu("\n\nchallenge completed.\n\n")
                        self.character.macroState["submenue"] = self.submenue
                        self.challengeRun4Done = True

                        self.challengeInfo = {"challengerGiven":[]}

                        self.availableChallenges["produceAutoScribe"] = {"text":"produce auto scribe"}
                        self.availableChallenges["produceFilledGooDispenser"] = {"text":"produce goo"}
                        self.availableChallenges["gatherSickBloom"] = {"text":"gather sick bloom"}
                else:
                    text = """challenge: run job orders\n\njob orders for Wall or Door or Floor plates will be dropped to the south. Produce the item named on the job order and return with the item.

finish 25 round (%s remaining):

"""%(25-self.challengeInfo["numSucesses"],)
                    if self.challengeInfo["type"]:
                        jobOrder = None
                        itemDelivered = None
                        for item in self.character.inventory:
                            if item.type == "GooFlask":
                                pass
                            elif item.type == "JobOrder" and item.done and item.tasks[-1]["toProduce"] == self.challengeInfo["type"] and item.tasks[-1]["task"] == "produce":
                                itemDelivered = item

                        fail = False
                        if not itemDelivered:
                            text += "you need to have the completed job order for "+self.challengeInfo["type"]+" in your inventory\n"
                            fail = True

                        if not fail:
                            self.character.inventory.remove(itemDelivered)
                            text += "you succeded this round\n"
                            self.challengeInfo["type"] = None
                            self.challengeInfo["numSucesses"] += 1
                    
                    if self.challengeInfo["type"] == None and not self.challengeInfo["numSucesses"] >= 25:
                       itemType = random.choice(["Wall","Door","FloorPlate"])
                       self.character.addMessage(itemType)

                       self.challengeInfo["type"] = itemType
                       newItem = JobOrder(creator=self)
                       newItem.xPosition = self.xPosition
                       newItem.yPosition = self.yPosition+1
                       newItem.tasks[-1]["toProduce"] = itemType
                       self.container.addItems([newItem])

                       text += "new job order outputted on the south of the machine"

                       text += """

comment:

* set the production managers commands to produce walls and doors and floor plates
* use the dropped job order with the production manager to produce the required items
* return to the auto tutor with the completed job order
* use commands and multipliers to do this multiple times"""


                    self.submenue = src.interaction.TextMenu("\n\n"+text+"\n\n")
                    self.character.macroState["submenue"] = self.submenue

        elif not self.challengeRun5Done:
            if len(self.availableChallenges):
                options = []
                for (key,value) in self.availableChallenges.items():
                    options.append([key,value["text"]])

                self.submenue = src.interaction.SelectionMenu("select the challenge to do:",options)
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                numFlasksFound = 0
                for item in self.character.inventory:
                    if item.type == "GooFlask" and item.uses == 100:
                        numFlasksFound += 1

                if not numFlasksFound > 3:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: Produce 4 filled goo flasks. \nchallenge in progress. Try again with 4 goo flasks with 100 uses left in each in your inventory.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: Produce 4 filled goo flasks. \nchallenge completed.\n\nreward: Character spawned. Talk to it by pressing h and command it.\n\n")
                    self.character.macroState["submenue"] = self.submenue
                    gooFlask1 = None
                    gooFlask2 = None
                    for item in reversed(self.character.inventory):
                        if item.type == "GooFlask" and item.uses == 100:
                            if gooFlask1 == None:
                                gooFlask1 = item
                            else:
                                gooFlask2 = item
                                break

                    self.character.inventory.remove(gooFlask2)
                    gooFlask1.uses = 0

                    # add character
                    name = "Erwin Lauterbach"
                    newCharacter = characters.Character(src.canvas.displayChars.staffCharactersByLetter[name[0].lower()],self.xPosition+1,self.yPosition,name=name,creator=self)

                    newCharacter.solvers = [
                              "SurviveQuest",
                              "Serve",
                              "NaiveMoveQuest",
                              "MoveQuestMeta",
                              "NaiveActivateQuest",
                              "ActivateQuestMeta",
                              "NaivePickupQuest",
                              "PickupQuestMeta",
                              "DrinkQuest",
                              "ExamineQuest",
                              "FireFurnaceMeta",
                              "CollectQuestMeta",
                              "WaitQuest"
                              "NaiveDropQuest",
                              "NaiveDropQuest",
                              "DropQuestMeta",
                            ]

                    self.challengeRun5Done = True

                    self.room.addCharacter(newCharacter,self.xPosition,self.yPosition+1)
                    newCharacter.macroState["macros"]["j"] = "Jf"
                    newCharacter.inventory.append(gooFlask2)

        else:
            self.submenue = src.interaction.TextMenu("\n\nTBD\n\n")
            self.character.macroState["submenue"] = self.submenue

    def checkForOtherItem(self,itemType):
        if len(self.character.inventory) > 2:
            return True
        foundOtherItem = None
        for item in self.character.inventory:
            if not item.type in ["GooFlask",itemType]:
                foundOtherItem = item
                break
        if foundOtherItem:
            return True
        return False

    def getFromInventory(self,itemType):
        foundItem = None
        for item in self.character.inventory:
            if item.type in [itemType]:
                foundItem = item
                break
        return foundItem

    def challengeRun2(self):

        selection = self.submenue.getSelection()
        self.submenue = None

        #<=
            # 
        # Note
        # gatherBloom
            #R SporeExtractor
            #R Puller
            #I food/moldfarming
            # produceSporeExtractor
        # produceScrapCompactors
            #R Tank
            #R Scraper
            # produceBasics
                #R Case
                #R Wall
                # prodCase
                    #R Heater
        # => produce 100 metal bars

        if selection == "note": # from root
            if not self.checkInInventoryOrInRoom(src.items.Note):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: write note\nstatus: challenge in progress - Try again with a note in your inventory.\n\ncomment:\n check \"information->items->notes\" on how to create notes.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: write note\nstatus: challenge completed.\n\nreward:\nnew Information option on \"Information->automation->maps\"\n\n")
                del self.availableChallenges["note"]

        elif selection == "gatherBloom": # from root
            if not self.checkInInventoryOrInRoom(src.items.Bloom):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather bloom\nstatus: challenge in progress - Try again with a bloom in your inventory.\n\ncomment: \nBlooms are represented by ** and are white.\nYou should be able to collect some outside of the wall, the exit is on the east.\n\n")
            else:
                del self.availableChallenges["gatherBloom"]
                self.availableChallenges["produceSporeExtractor"] = {"text":"produce a Spore Extractor"}
                self.knownBlueprints.append("SporeExtractor")
                self.knownBlueprints.append("Puller")
                self.knownInfos.append("food/moldfarming")
                blooms = []
                for i in range(0,4):
                    new = itemMap["MoldSpore"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition+1
                    blooms.append(new)
                self.container.addItems(blooms)
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather bloom\nstatus: challenge completed.\n\nreward:\nchallenge \"produce a Spore Extractor\" added\nmold spores added to south/below\nnew Information option on \"information->food->mold farming\"\nNew blueprint reciepes for Tank + Puller\n\n")

        elif selection == "produceSporeExtractor": # from gatherBloom
            if not self.checkInInventoryOrInRoom(src.items.SporeExtractor):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce spore extractor\nstatus: challenge in progress - try again with spore extractor in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce spore extractor\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceSporeExtractor"]

        elif selection == "produceScrapCompactors": # from root
            if not self.checkInInventory(src.items.ScrapCompactor):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce scrap compactor\nstatus: challenge in progress - try again with scrap compactor in your inventory.\n\ncomment:\n * check \"information->blueprint reciepes\" and \"information -> machines -> machine production\" on how to do this.\n\n")
            else:
                self.knownBlueprints.append("Tank")
                self.knownBlueprints.append("Scraper")
                self.availableChallenges["produceBasics"] = {"text":"produce basics"}
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce scrap compactor\nstatus: challenge completed.\n\nreward:\nchallenge \"%s\" added\nNew blueprint reciepes for Tank, Scraper\n\n"%(self.availableChallenges["produceBasics"]["text"]))
                del self.availableChallenges["produceScrapCompactors"]

        elif selection == "produceBasics": # from produceScrapCompactors
            if self.checkListAgainstInventoryOrIsRoom(["Rod","Bolt","Stripe","Mount","Radiator","Sheet"]):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce basics\nstatus: challenge in progress. Try again with rod + bolt + stripe + mount + radiator + sheet in your inventory.\n\ncomment:\nThe blueprints required should be in this room.\n\n")
            else:
                del self.availableChallenges["produceBasics"]
                self.knownBlueprints.append("Case")
                self.knownBlueprints.append("Wall")
                self.availableChallenges["prodCase"] = {"text":"produce case"}
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce basics\nstatus: challenge completed.\n\nreward:\nchallenge \"%s\" added\nNew blueprint reciepes for Case, Wall\n"%(self.availableChallenges["prodCase"]["text"]))

        elif selection == "prodCase": # from produceBasics
            if not self.checkInInventoryOrInRoom(src.items.Case):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce case\nstatus: challenge in progress - Try again with a case in your inventory.\n\ncomment:\nCases are produced from Frames\n which are produced from rods\n which are produced from metal bars\n which are produced from scrap\ncheck \"information -> blueprint reciepes\" for the reciepes\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce case\nstatus: challenge completed.\n\nreward:\nNew blueprint reciepes for Heater, Door\n\n")
                self.knownBlueprints.append("Heater")
                self.knownBlueprints.append("Door")
                del self.availableChallenges["prodCase"]


        #<=
            #R Connector
            #R Pusher
        # differentBlueprints
        # 9blooms
            #R BloomShredder
            # processedBloom
        # produceAdvanced
            # produceWall
                #R Door
                # produceDoor
                    #R FloorPlate
                    # produceFloorPlate
        # produceScraper

        #=> 25 walls

        elif selection == "differentBlueprints": # from root2
            blueprints = []
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.BluePrint) and not item.endProduct in blueprints:
                    blueprints.append(item.endProduct)
            if not len(blueprints) > 8:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 9 different blueprint\nstatus: challenge in progress - try again with 9 different blueprints in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 9 different blueprint\nstatus: challenge completed.\n\n")
                del self.availableChallenges["differentBlueprints"]

        elif selection == "9blooms": # from root2
            if self.countInInventoryOrRoom(src.items.Bloom) < 9:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather 9 blooms\nstatus: failed. Try with 9 bloom in your inventory.\n\n\n\n")
            else:
                self.availableChallenges["processedBloom"] = {"text":"process bloom"}
                self.knownBlueprints.append("BloomShredder")
                self.submenue = src.interaction.TextMenu("\n\nchallenge completed.\n\nreward:\n* new blueprint reciepe for bloom shredder\n* challenge %s added\n\n"%(self.availableChallenges["processedBloom"]["text"]))
                del self.availableChallenges["9blooms"]

        elif selection == "processedBloom": # from 9blooms
            if not self.checkInInventoryOrInRoom(src.items.BioMass):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: process bloom\nstatus: challenge in progress - try with bio mass in your inventory.\n\ncomment:\n* use a bloom shreder to produce bio mass\n* check \"information->food->mold farming\" for more information\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: process bloom\nstatus: challenge completed.\n\n")
                del self.availableChallenges["processedBloom"]

        elif selection == "produceAdvanced": # from root2
            if self.checkListAgainstInventoryOrIsRoom(["Tank","Heater","Connector","pusher","puller","Frame"]):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with tank + heater + connector + pusher + puller + frame in your inventory.\n\n")
            else:
                del self.availableChallenges["produceAdvanced"]
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceWall": # from produceAdvanced
            if not self.checkInInventoryOrInRoom(src.items.Wall):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with wall in your inventory.\n\n")
            else:
                del self.availableChallenges["produceWall"]
                self.knownBlueprints.append("Door")
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\nreward:\n* new blueprint reciepe for door\n\n")

        elif selection == "produceDoor": # from produceWall
            if not self.checkInInventoryOrInRoom(src.items.Door):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with door in your inventory.\n\nreward:\n* new blueprint reciepe for floor plate\n\n")
            else:
                del self.availableChallenges["produceDoor"]
                self.knownBlueprints.append("FloorPlate")
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceFloorPlate": # from produceDoor
            if not self.checkInInventoryOrInRoom(src.items.FloorPlate):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge in progress - try again with floor plate in your inventory.\n\n")
            else:
                del self.availableChallenges["produceFloorPlate"]
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce items\nstatus: challenge completed.\n\n")

        elif selection == "produceScraper": # from root2
            if not self.checkInInventoryOrInRoom(src.items.Scraper):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce scraper\nstatus: challenge in progress. Try with scraper in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce scraper\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceScraper"]


        #<=
            #R RoomBuilder
            #R FloorPlate
            #R Production Manager
        # produceBioMasses
            #R BioPress
            # processBioMass
                # build autofarmer
                # producePressCakes
                    #R GooDispenser
                    #R GooFlask
                # buildGooProducer
                #R GooProducer
                #R AutoFarmer
        # createMap
            # createMapWithPaths
        # build production manager 
            #R AutoScribe
            #R uniformStockpileManager
            # build uniformStockpileManager

        #=> produce random door/wall/floorplate things

        elif selection == "produceBioMasses": # from root3
            if self.countInInventoryOrRoom(src.items.BioMass) < 9:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 9 Biomass\nstatus: challenge in progress. Try with 9 BioMass in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce 9 Biomass\nstatus: challenge completed.\n\n")
                self.availableChallenges["processBioMass"] = {"text":"process bio mass"}
                self.knownBlueprints.append("BioPress")
                del self.availableChallenges["produceBioMasses"]

        elif selection == "processBioMass": # from produceBioMasses
            if not self.checkInInventoryOrInRoom(src.items.PressCake):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge in progress. Try with Press cake in your inventory.\n\ncomment:\n* use a bio press to produce press cake\n* check \"information->food->mold farming\" for more information\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge completed.\n\nreward:\n* new blueprint reciepes for GooProducer, AutoFarmer\n\n")
                self.availableChallenges["producePressCakes"] = {"text":"produce press cakes"}
                self.availableChallenges["buildGooProducer"] = {"text":"build goo producer"}
                self.availableChallenges["produceAutofarmer"] = {"text":"produce autofarmer"}
                self.knownBlueprints.append("GooProducer")
                self.knownBlueprints.append("AutoFarmer")
                del self.availableChallenges["processBioMass"]

        elif selection == "producePressCakes": # from processBioMass
            if self.countInInventoryOrRoom(src.items.PressCake) < 4:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce press cakes\nstatus: challenge in progress. Try with 4 press cake in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce press cake\nstatus: challenge completed.\n\n")
                del self.availableChallenges["producePressCakes"]

                self.knownBlueprints.append("GooDispenser")
                self.knownBlueprints.append("GooFlask")

        elif selection == "buildGooProducer": # from processBioMass
            if not self.checkInInventoryOrInRoom(src.items.GooProducer):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build goo producer\nstatus: challenge in progress. Try with goo producer in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build goo producer\nstatus: challenge completed.\n\n")
                del self.availableChallenges["buildGooProducer"]

        elif selection == "produceAutofarmer": # from processBioMass
            if not self.checkInInventoryOrInRoom(src.items.AutoFarmer):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build auto farmer\nstatus: challenge in progress. Try with auto farmer in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build auto farmer\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceAutofarmer"]

        elif selection == "createMap": # from root3
            if not self.checkInInventoryOrInRoom(src.items.Map):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: create map\nstatus: challenge in progress. Try with map in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: create map\nstatus: challenge completed.\n\n")
                self.availableChallenges["createMapWithPaths"] = {"text":"create map with routes"}
                del self.availableChallenges["createMap"]

        elif selection == "createMapWithPaths": # from createMap
            itemFound = False
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.Map) and item.routes:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: create map with paths\nstatus: challenge in progress. Try with map with paths in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: create map with paths\nstatus: challenge completed.\n\n")
                del self.availableChallenges["createMapWithPaths"]

        elif selection == "produceProductionManager": # from root 3
            if not self.checkInInventoryOrInRoom(src.items.itemMap["ProductionManager"]):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build production manager\nstatus: challenge in progress. Try with production manager in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build production manager\nstatus: challenge completed.\n\n")
                self.availableChallenges["produceUniformStockpileManager"] = {"text":"produce uniform stockpile manager"}
                self.knownBlueprints.append("AutoScribe")
                self.knownBlueprints.append("UniformStockpileManager")
                del self.availableChallenges["produceProductionManager"]

        elif selection == "produceUniformStockpileManager": # from produceProductionManager
            if not self.checkInInventoryOrInRoom(src.items.UniformStockpileManager):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build uniform stockpile manager\nstatus: challenge in progress. Try with uniform stockpile manager in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: build uniform stockpile manager\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceUniformStockpileManager"]
        #<=
        #- produceFilledGooDispenser
            #- > strengthen mold growth
            #- R Container
            #- R BloomContainer
            #- R GrowthTank
        #- autoScribe 
            #- > go to tile center
            #- copy commmand
                #- > decide inventory full
                #- > decide inventory empty
                #- > activate 4 directions
        #- gather sick bloom
            #- gather coal
                #- build fire crystals
            #- > go to food
            #- > decide food
            #- X tile completely covered in mold
                #- X tile with 9 living blooms
                    #- X tile with 3 living sick blooms
            #- X goto north west edge
                #- X goto north east edge
                    #- X goto south east edge
                        #- X goto south west edge
                        #- > go to west tile border
                        #- > go to north tile border
                        #- > go to east tile border
                        #- > go to south tile border
            #- gather 9 sick bloom

        # => proudce 3 goo flasks 

        elif selection == "produceFilledGooDispenser": # NOT ASSIGNED
            itemFound = False
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.GooDispenser) and item.charges > 0:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce goo\nstatus: challenge in progress. Try again with a goo dispenser with at least one charge in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce goo\nstatus: challenge completed.\n\nreward:\nNew Blueprint reciepe for growth tank\nCommand \"STIMULATE MOLD GROWTh\" dropped to the south\n\n")

                self.knownBlueprints.append("GrowthTank")
                self.knownBlueprints.append("Container")
                self.knownBlueprints.append("BloomContainer")

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d",
                                       "a","j","a","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "a","j","a","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "$","=","d","d",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "d","j","d","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "d","j","d","j",
                                       "w","j","w","j","w","j","w","j","o","p","x","$","=","s","s",
                                       "s","j","s","j","s","j","s","j","o","p","x","$","=","w","w",
                                       "$","=","a","a"])
                newCommand.extraName = "STIMULATE MOLD GROWTh"
                newCommand.description = "using this command will make you move around and pick mold to make it grow.\nIf there are things lying around they might be activated."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["produceFilledGooDispenser"]

        elif selection == "produceAutoScribe": # from root 4
            if not self.checkInInventoryOrInRoom(src.items.AutoScribe):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge in progress. Try with auto scribe in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge completed.\nreward: \"GO TO TILE CENTEr\" command dropped to south/below\n\n")
                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GO TO TILE CENTEr"
                newCommand.description = "using this command will make you move to the center of the tile. If the path is blocked the command will not work properly."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])
                self.availableChallenges["copyCommand"] = {"text":"copy command"}
                del self.availableChallenges["produceAutoScribe"]

        elif selection == "copyCommand": # from produceAutoScribe
            itemCount = 0
            for item in self.character.inventory + self.room.itemsOnFloor:
                if isinstance(item,src.items.Command) and item.command == ["o","p","x","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"]:
                    itemCount += 1

            if not itemCount > 2:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: copy command\nstatus: challenge in progress. Try again with 3 copies of the \"GO TO TILE CENTEr\" command\n\ncomment:\nuse the auto scribe to copy commands.\nthe \"GO TO TILE CENTEr\" command was dropped as reward for the \"produce auto scribe\" challenge.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce auto scribe\nstatus: challenge completed.\n\n")

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","i","a","d"])
                newCommand.extraName = "DECIDE INVENTORY EMPTY EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is empty and will move you east otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","I","a","d"])
                newCommand.extraName = "DECIDE INVENTORY FULL EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is completely filled and will move you east otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["w","%","b","d","s"])
                newCommand.extraName = "DECIDE NORTH BLOCKED EAST STAy"
                newCommand.description = "using this command will make you move east in case the field to the north is not walkable and will make you stay in place otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])
        
                newCommand = Command(creator=self)
                newCommand.setPayload(["w","j"])
                newCommand.extraName = "ACTIVATE NORTh"
                newCommand.description = "using this command will make you activate to the north."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["s","j"])
                newCommand.extraName = "ACTIVATE SOUTh"
                newCommand.description = "using this command will make you activate to the south."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["d","j"])
                newCommand.extraName = "ACTIVATE EASt"
                newCommand.description = "using this command will make you activate to the east."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["a","j"])
                newCommand.extraName = "ACTIVATE WESt"
                newCommand.description = "using this command will make you activate to the west."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["copyCommand"]
        
        # copy command
        elif selection == "gatherSickBloom": # from root 4
            if not self.checkInInventoryOrInRoom(src.items.SickBloom):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather sick bloom\nstatus: challenge in progress. Try with sick bloom in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather sick bloom\nstatus: challenge completed.\n\n")
                self.availableChallenges["gatherCoal"] = {"text":"gather coal"}
                self.availableChallenges["challengerExplore1"] = {"text":"explore mold"}
                self.availableChallenges["challengerGoTo1"] = {"text":"explore terrain"}
                self.availableChallenges["gatherSickBlooms"] = {"text":"gather sick blooms"}

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","f","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = "using this command will make you go to a food source nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","F","a","d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["gatherSickBloom"]

        elif selection == "gatherCoal": # from gatherSickBloom
            if not self.checkInInventoryOrInRoom(src.items.Coal):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather coal\nstatus: challenge in progress. Try with coal in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather coal\nstatus: challenge completed.\n\n")
                self.availableChallenges["produceFireCrystals"] = {"text":"produce fire crystals"}
                self.knownBlueprints.append("FireCrystals")

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","C","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = "using this command will make you go to a food source nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","F","a","d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["gatherCoal"]

        elif selection == "produceFireCrystals": # from gatherCoal
            if not self.checkInInventoryOrInRoom(src.items.FireCrystals):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce fire crystals\nstatus: challenge in progress. Try with fire crystals in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce fire crystals\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceFireCrystals"]

        elif selection == "gatherSickBlooms": # from gatherSickBloom
            if self.countInInventoryOrRoom(src.items.SickBloom) < 9:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge in progress. Try with 9 sick blooms in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather sick blooms\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherSickBlooms"]

        elif selection == "challengerExplore1": # from gatherSickBloom
            secret = "epxplore1:-)"
            if not "explore" in self.challengeInfo["challengerGiven"]:
                new = PortableChallenger(creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition+1
                new.secret = secret
                new.challenges = ["3livingSickBlooms","9livingBlooms","fullMoldCover"]
                self.submenue = src.interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\ncomment: do not loose or destroy the challenger\n\n")
                self.challengeInfo["challengerGiven"].append("explore")
                self.container.addItems([new])
            else:
                itemFound = None
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if item.type == "PortableChallenger" and item.done and item.secret == secret:
                        itemFound = item

                if not itemFound:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n")
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: explore mold\nstatus: challenge completed.\n\n")
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerExplore1"]
        elif selection == "challengerGoTo1": # from gatherSickBloom
            secret = "goto1:-)"
            if not "goto" in self.challengeInfo["challengerGiven"]:
                new = PortableChallenger(creator=self)
                new.xPosition = self.xPosition
                new.yPosition = self.yPosition+1
                new.secret = secret
                new.challenges = ["gotoWestSouthTile","gotoEastSouthTile","gotoEastNorthTile","gotoWestNorthTile"]
                self.container.addItems([new])

                self.submenue = src.interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\n")
                self.challengeInfo["challengerGiven"].append("goto")
            else:
                itemFound = None
                for item in self.character.inventory + self.room.itemsOnFloor:
                    if item.type == "PortableChallenger" and item.done and item.secret == secret:
                        itemFound = item

                if not itemFound:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n")
                else:
                    self.submenue = src.interaction.TextMenu("\n\nchallenge: explore terrain\nstatus: challenge completed.\n\n")
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerGoTo1"]

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["@","$","=","S","E","L","F","x","a"])
                    newCommand.extraName = "GOTO WEST BORDEr"
                    newCommand.description = "using this command will make you go the west tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1
                    self.container.addItems([newCommand])

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["$",">","x","$","x","=","1","4","@","$","x","-","S","E","L","F","x","$","=","x","a","<","x"])
                    newCommand.extraName = "GOTO EAST BORDEr"
                    newCommand.description = "using this command will make you go the east tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1
                    self.container.addItems([newCommand])

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["@","$","=","S","E","L","F","y","w"])
                    newCommand.extraName = "GOTO NORTH BORDEr"
                    newCommand.description = "using this command will make you go the north tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1
                    self.container.addItems([newCommand])

                    newCommand = Command(creator=self)
                    newCommand.setPayload(["$",">","y","$","y","=","1","4","@","$","y","-","S","E","L","F","y","$","=","y","s","<","y"])
                    newCommand.extraName = "GOTO SOUTH BORDEr"
                    newCommand.description = "using this command will make you go the south tile edge."
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition+1
                    self.container.addItems([newCommand])

        #- build growth tank
            #- build NPC
                #- > go to scrap
                #- > go to character
                #- gather corpse
                    #- > go to corpse
                    #- > decide corpse
        #- build item upgrader
            #- upgrade Command to 4
            #- upgrade BloomContainer 3
            #- upgrade Sheet to 4
            #- upgrade Machine
        #- memory cell
            # learn command
        # => learn 25 commands 

        elif selection == "produceGrowthTank": # from root 5
            if not self.checkInInventoryOrInRoom(src.items.GrowthTank):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce growth tank\nstatus: challenge in progress. Try with growth tank in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce growth tank\nstatus: challenge completed.\n\n")
                self.availableChallenges["spawnNPC"] = {"text":"spawn NPC"}
                del self.availableChallenges["produceGrowthTank"]

        elif selection == "spawnNPC": # from produceGrowthTank
            if len(self.room.characters) < 2:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: spawn NPC\nstatus: challenge in progress. Try with a NPC in the room.\n\n")
                
                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","s","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO SCRAp"
                newCommand.description = "using this command will make you go to scrap nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","c","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO CHARACTEr"
                newCommand.description = "using this command will make you go to a character nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: spawn NPC\nstatus: challenge completed.\n\n")

        elif selection == "gatherCorpse": # from spawnNPC
            if not self.checkInInventoryOrInRoom(src.items.Corpse):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather corpse\nstatus: challenge in progress. Try with corpse in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather corpse\nstatus: challenge completed.\n\n")
                
                newCommand = Command(creator=self)
                newCommand.setPayload(["o","p","M","$","=","a","a","$","=","w","w","$","=","s","s","$","=","d","d"])
                newCommand.extraName = "GOTO CORPSe"
                newCommand.description = "using this command will make you go to a corpse nearby."
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                newCommand = Command(creator=self)
                newCommand.setPayload(["%","M","a","d"])
                newCommand.extraName = "DECIDE CORPSE EAST WESt"
                newCommand.description = "using this command will make you move west in case a corpse is nearby and will move you east otherwise"
                newCommand.xPosition = self.xPosition
                newCommand.yPosition = self.yPosition+1
                self.container.addItems([newCommand])

                del self.availableChallenges["gatherCorpse"]

        elif selection == "produceItemUpgrader": # from root 5
            if not self.checkInInventoryOrInRoom(src.items.ItemUpgrader):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce item upgrader\nstatus: challenge in progress. Try with item upgrader in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce item upgrader\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceItemUpgrader"]

        elif selection == "upgradeCommand4": # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.room.itemsOnFloor:
                if item.type == "Command" and item.level >= 4:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade command to level 4\nstatus: challenge in progress. Try with a command with level 4 in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade command to level 4\nstatus: challenge completed.\n\n")
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeBloomContainer3": # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.room.itemsOnFloor:
                if item.type == "BloomContainer" and item.level >= 3:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade bloom container to level 3\nstatus: challenge in progress. Try with a bloom container with level 3 in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade bloom container to level 3\nstatus: challenge completed.\n\n")
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeSheet4": # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.room.itemsOnFloor:
                if item.type == "Sheet" and item.level >= 4:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade sheet to level 4\nstatus: challenge in progress. Try with a sheet with level 4 in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade sheet to level 4\nstatus: challenge completed.\n\n")
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeMachine2": # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.room.itemsOnFloor:
                if item.type == "Machine" and item.level >= 2:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade machine to level 2\nstatus: challenge in progress. Try with a machine with level 2 in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: upgrade machine to level 2\nstatus: challenge completed.\n\n")
                del self.availableChallenges["upgradeCommand4"]

        #- gather posion bloom
        #- produce room builder
            #- build floor plate
        #X clear tile x/y
            #> floor right empty
            # build room
        #X goto map center
        # tile with 9 living sick blooms
        # produce goo flask with >100 charges
        # 
        #=> build mini mech

        elif selection == "gatherPoisonBloom": # from root 6
            if self.countInInventoryOrRoom(src.items.PoisonBloom) < 9:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with poison bloom in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherPoisonBloom"]

        elif selection == "produceRoomBuilder": # from root 6
            if not self.checkInInventoryOrInRoom(src.items.RoomBuilder):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce room builder\nstatus: challenge in progress. Try with room builder in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce room builder\nstatus: challenge completed.\n\n")
                self.availableChallenges["produceFloorPlate"] = {"text":"produce floor plate"}
                del self.availableChallenges["produceRoomBuilder"]

        elif selection == "produceFloorPlate": # from produceRoomBuilder
            if self.checkInInventoryOrRoom(src.items.FloorPlate):
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce floor plates\nstatus: challenge in progress. Try with 9 floor plates in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: produce floor plates\nstatus: challenge completed.\n\n")
                del self.availableChallenges["produceFloorPlate"]

        # build map to room
        # build working map (drop marker in 5 rooms with requirement, make random star movement)
        # gather poision blooms





        elif selection == "gatherPoisonBlooms": # from gatherPoisonBloom
            if self.countInInventoryOrRoom(src.items.PoisonBloom) < 5:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with 5 poison blooms in your inventory.\n\n")
            else:
                self.submenue = src.interaction.TextMenu("\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n")
                del self.availableChallenges["gatherPoisonBlooms"]



        self.character.macroState["submenue"] = self.submenue


    def countInInventory(self,itemType):
        num = 0 
        for item in self.character.inventory:
            if isinstance(item,itemType):
                num += 1
        return num

    def countInInventoryOrRoom(self,itemType):
        num = self.countInInventory(itemType)
        for item in self.room.itemsOnFloor:
            if isinstance(item,itemType):
                num += 1
        return num

    def basicInfo(self):
        itemsLeft = ["Tank","Heater","Connector","pusher","puller","Frame"]

    def checkListAgainstInventory(self,itemTypes):
        for item in self.character.inventory:
            if item.type in itemTypes:
                itemTypes.remove(item.type)
        return itemTypes

    def checkListAgainstInventoryOrIsRoom(self,itemTypes):
        itemTypes = self.checkListAgainstInventory(itemTypes)
        if itemTypes:
            for item in self.room.itemsOnFloor:
                if item.type in itemTypes:
                    itemTypes.remove(item.type)
        return itemTypes

    def checkInInventory(self,itemType):
        for item in self.character.inventory:
            if isinstance(item,itemType):
                return True
        return False

    def checkInInventoryOrInRoom(self,itemType):
        if self.checkInInventory(itemType):
            return True
        for item in self.room.itemsOnFloor:
            if isinstance(item,itemType):
                return True

        return False

    def basicInfo(self):

        options = []

        options.append(("movement","movement"))
        options.append(("interaction","interaction"))

        if self.gooChallengeDone: 
            options.append(("machines","machines"))

        if self.gooChallengeDone: 
            options.append(("food","food"))

        if self.blueprintChallengeDone: 
            options.append(("automation","automation"))

        if self.machineChallengeDone: 
            options.append(("blueprints","blueprint reciepes"))

        self.submenue = src.interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level1_selection

    def level1_selection(self):

        selection = self.submenue.getSelection()

        if selection == "movement":
            self.submenue = src.interaction.TextMenu("\n\n * press ? for help\n\n * press a to move left/west\n * press w to move up/north\n * press s to move down/south\n * press d to move right/east\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "interaction":
            self.submenue = src.interaction.TextMenu("\n\n * press k to pick up\n * press l to pick up\n * press i to view inventory\n * press @ to view your stats\n * press j to activate \n * press e to examine\n * press ? for help\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with it\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "machines":
            options = []

            options.append(("level1_machines_bars","metal bar production"))
            if self.metalbarChallengeDone:
                options.append(("level1_machines_simpleItem","simple item production"))
            if self.sheetChallengeDone:
                options.append(("level1_machines_machines","machine production"))
            if self.machineChallengeDone:
                options.append(("level1_machines_machineMachines","machine machine production"))
                options.append(("level1_machines_blueprints","blueprint production"))
                #options.append(("level1_machines_food","food production"))
                #options.append(("level1_machines_energy","energy production"))

            self.submenue = src.interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Machines
        elif selection == "food":
            options = []

            options.append(("food_basics","food basics"))
            if "food/moldfarming" in self.knownInfos:
                options.append(("food_moldfarming","mold farming"))

            self.submenue = src.interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Food
        elif selection == "automation":
            options = []

            options.append(("commands","creating commands"))
            if self.commandChallengeDone: 
                options.append(("multiplier","multiplier"))
            if self.activateChallengeDone:
                options.append(("notes","notes"))
            if self.blueprintChallengeDone:
                options.append(("maps","maps"))

            self.submenue = src.interaction.SelectionMenu("select the information you need",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Automation
        elif selection == "blueprints":
            text = "\n\nknown blueprint recieps:\n\n"

            shownText = False
            if "Rod" in self.knownBlueprints:
                text += " * rod             <= rod\n"
                shownText = True
            if "Radiator" in self.knownBlueprints:
                text += " * radiator        <= radiator\n"
                shownText = True
            if "Mount" in self.knownBlueprints:
                text += " * mount           <= mount\n"
                shownText = True
            if "Stripe" in self.knownBlueprints:
                text += " * stripe          <= stripe\n"
                shownText = True
            if "Bolt" in self.knownBlueprints:
                text += " * bolt            <= bolt\n"
                shownText = True
            if "Sheet" in self.knownBlueprints:
                text += " * sheet           <= sheet\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Frame" in self.knownBlueprints:
                text += " * frame           <= rod + metal bars\n"
                shownText = True
            if "Heater" in self.knownBlueprints:
                text += " * heater          <= radiator + metal bars\n"
                shownText = True
            if "Connector" in self.knownBlueprints:
                text += " * connector       <= mount + metal bars\n"
                shownText = True
            if "Pusher" in self.knownBlueprints:
                text += " * pusher          <= stripe + metal bars\n"
                shownText = True
            if "Puller" in self.knownBlueprints:
                text += " * puller          <= bolt + metal bars\n"
                shownText = True
            if "Tank" in self.knownBlueprints:
                text += " * tank            <= sheet + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"
            
            shownText = False
            if "Case" in self.knownBlueprints:
                text += " * case            <= frame + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Wall" in self.knownBlueprints:
                text += " * wall            <= metal bars\n"
                shownText = True
            if "Door" in self.knownBlueprints:
                text += " * door            <= connector\n"
                shownText = True
            if "FloorPlate" in self.knownBlueprints:
                text += " * floor plate     <= sheet + rod + bolt\n"
                shownText = True
            if "RoomBuilder" in self.knownBlueprints:
                text += " * room builder    <= puller\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "BloomShredder" in self.knownBlueprints:
                text += " * bloom shredder  <= bloom\n"
                shownText = True
            if "BioPress" in self.knownBlueprints:
                text += " * bio press       <= bio mass\n"
                shownText = True
            if "GooFlask" in self.knownBlueprints:
                text += " * goo flask       <= tank\n"
                shownText = True
            if "GooDispenser" in self.knownBlueprints:
                text += " * goo dispenser   <= flask\n"
                shownText = True
            if "SporeExtractor" in self.knownBlueprints:
                text += " * spore extractor <= bloom + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "GooProducer" in self.knownBlueprints:
                text += " * goo producer    <= press cake\n"
                shownText = True
            if "GrowthTank" in self.knownBlueprints:
                text += " * growth tank     <= goo flask + tank\n"
                shownText = True
            if "FireCrystals" in self.knownBlueprints:
                text += " * fire crystals   <= coal + sick bloom\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "ProductionManager" in self.knownBlueprints:
                text += " * production manager <= memory cell + connector + command\n"
                shownText = True
            if "AutoFarmer" in self.knownBlueprints:
                text += " * auto farmer     <= memory cell + bloom + sick bloom\n"
                shownText = True
            if "UniformStockpileManager" in self.knownBlueprints:
                text += " * uniform stockpile manager <= memory cell + connector + floor plate\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "ScrapCompactor" in self.knownBlueprints:
                text += " * scrap compactor <= scrap\n"
                shownText = True
            if "Scraper" in self.knownBlueprints:
                text += " * scraper         <= scrap + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Container" in self.knownBlueprints:
                text += " * container       <= case + sheet\n"
                shownText = True
            if "BloomContainer" in self.knownBlueprints:
                text += " * bloom container <= case + sheet + bloom\n"
                shownText = True
            if "AutoScribe" in self.knownBlueprints:
                text += " * auto scribe     <= command\n"
                shownText = True
            if "MemoryCell" in self.knownBlueprints:
                text += " * memory cell     <= connector + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            text += "\n\n"
            self.submenue = src.interaction.TextMenu(text)
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Food(self):

        selection = self.submenue.getSelection()

        if selection == "food_basics":
            self.submenue = src.interaction.TextMenu("\n\nYou need to eat/drink regulary to not starve\nIf you do not drink for 1000 ticks you will starve,\n\nMost actions will take a tick. So you will need to drink every 1000 steps or you will starve.\n\nDrinking/Eating usually happens automatically as long as you have something eatable in you inventory.\n\nYou check your satiation in your character screen or on the lower right edge of the screen\n\nThe most common food is goo stored in a goo flask. Every sip from a goo flask gains you 1000 satiation.\nWith a maximum or 100 charges a full goo flask can hold enough food for up to 100000 moves.\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "food_moldfarming":
            self.submenue = src.interaction.TextMenu("\n\nMold is a basis for goo production and can be eaten directly.\nMold grows in patches and develop blooms.\nMold blooms can be collected and give 100 satiation when eaten or be processed into goo.\n\ngoo production:\n * Blooms can be processed into bio mass using the bloom shredder.\n * Bio mass can be processed into press cakes using the bio press.\n * press cake can be used to produce goo\n * The goo producer needs a goo dispenser to store the goo in.\n * The goodispenser allows you fill your flask.\n\nNew Mold patches can be started using mold spores. Growth in stagnant mold patches can be restarted by picking some sprouts or blooms\n\n")
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Automation(self):

        selection = self.submenue.getSelection()

        if selection == "commands":
            self.submenue = src.interaction.TextMenu("\n\nCommands are a way of automating actions. A character will run a command after activating it.\n\nThe easiest way of creating a command is:\n * drop a sheet on the floor\n * activate the sheet on the floor\n * select \"create a written command\"\n * select \"start recording\"\n * do the action\n * return to the sheet on the ground\n * activate the sheet again\n\nTo do the recorded action activate the command on the floor.\nWhile running the command you are not able the control your character and the game will speed up the longer the command runs.\n\nYou can press ctrl-d to abort running a commmand.")
            self.character.macroState["submenue"] = self.submenue
        if selection == "multiplier":
            self.submenue = src.interaction.TextMenu("\n\nThe multiplier allow to do something x times. For example walking 5 steps to the right, waiting 100 turns, activating commands 3 times\n\nTo use multiplier type in the number of times you want to do something and the action.\n\nexamples:\n\n5d => 5 steps to the right\n100. => wait a hundred turns\n3j => activating a command you are standing on 3 times\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "notes":
            self.submenue = src.interaction.TextMenu("\n\nNotes do not do anything except holding a text.\n\nYou can use this to place reminder on how things work and similar\n\nnotes can be created from sheets\n\n")
            self.character.macroState["submenue"] = self.submenue
        if selection == "maps":
            self.submenue = src.interaction.TextMenu("\n\nMaps allow for easier movement on a wider scale. Maps store routes between points.\n\nIf you are at the starting point of a route you can use the map to walk to the routes end point\nFor example if a map holds the route between point a and b you can use the map to travel to point b if you are at point a.\nMarking the startpoints of your routes is recomended, since you have stand at the exact coordinate to walk a route,\n\nYou create a route by: \n * moving to the start location of the route.\n * using the map\n * select the \"add route\" option\n * move to your target location\n * use the map again\n * select the \"add route\" option again.\n\nSince recording routes behaves like recording commands you can include actions like opening/closing doors or getting equipment.\nThe routes are not adapting to change and a closed door might disrupt your route.\n\n")
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Machines(self):

        selection = self.submenue.getSelection()

        if selection == "level1_machines_bars":
            self.submenue = src.interaction.TextMenu("\n\nMetal bars are used to produce most things. You can produce metal bars by using a scrap compactor.\nA scrap compactor is represented by RC. Place the scrap to the left/west of the scrap compactor.\nActivate it to produce a metal bar. The metal bar will be outputted to the right/east of the scrap compactor.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_simpleItem":
            self.submenue = src.interaction.TextMenu("\n\nMost items are produced in machines. A machine usually produces only one type of item.\nThese machines are shown as X\\. Place raw materials to the west/left/north/above of the machine and activate it to produce the item.\n\nYou can examine machines to get a more detailed descripton.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = src.interaction.TextMenu("\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n")
        elif selection == "level1_machines_machines":
            self.submenue = src.interaction.TextMenu("\n\nThe machines are produced by a machine-machine. The machine machines are shown as M\\\nMachine-machines require blueprints to produce machines.\n\nTo produce a machine for producing rods for example a blueprint for rods is required.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_blueprints":
            self.submenue = src.interaction.TextMenu("\n\nBlueprints are produced by a blueprinter.\nThe blueprinter takes items and a sheet as input and produces blueprints.\n\nDifferent items or combinations of items produce blueprints for different things.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_machineMachines":
            self.submenue = src.interaction.TextMenu("\n\nMachine-machines can only be produced by the production artwork. The production artwork is represented by ßß.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = src.interaction.TextMenu("\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_energy":
            self.submenue = src.interaction.TextMenu("\n\nEnergy production is steam based. Steam is generated heating a boiler.\nA boiler is represented by OO or 00.\n\nA boiler is heated by placing a furnace next to it and fireing it. A furnace is fired by activating it while having coal in you inventory.\nA furnace is represented by oo or öö.\n\nCoal can be harvested from coal mines. Coal mines are represented by &c.\nActivate it and a piece of coal will be outputted to the right/east.\ncoal is represented by sc.\n\n")
            self.character.macroState["submenue"] = self.submenue

    def l2Info(self):

        options = []

        options.append(("level2_multiplier","action multipliers"))
        options.append(("level2_rooms","room creation"))

        self.submenue = src.interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level2_selection

    def level2_selection(self):

        selection = self.submenue.getSelection()

        if selection == "level2_multiplier":
            self.submenue = src.interaction.TextMenu("\n\nyou can use multiplicators with commands. Typing a number followed by a command will result in the command to to be run multiple times\n\nTyping 10l is the same as typing llllllllll.\nThis will result in you dropping 10 items from your inventory\n\nThe multiplicator only applies to the following command.\nTyping 3aj will be expanded to aaaj.\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level2_rooms":
            self.submenue = src.interaction.TextMenu("\n\nmany machines only work within rooms. You can build new rooms.\nRooms are rectangular and have one door.\n\nYou can build new rooms. Prepare by placing walls and a door in the form of a rectangle on the ground.\n\nPlace a room builder within the walls and activate it to create a room from the basic items.\n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: "+selection)

    def l3Info(self):

        options = []

        options.append(("level3_macrosBasic","macro basics"))
        options.append(("level3_macrosExtra","macro extra"))
        options.append(("level3_macrosShortcuts","macro shortCuts"))

        self.submenue = src.interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level3_selection

    def level3_selection(self):

        selection = self.submenue.getSelection()

        if selection == "level3_macrosBasic":
            self.submenue = src.interaction.TextMenu("\n\nyou can use macros to automate task. This means you can record and replay keystrokes.\n\nTo record a macro press - to start recording and press the key to record to.\nAfterwards do your movement and press - to stop recording.\nTo replay the recorded macro press _ and the key the macro was recorded to.\n\nFor example typing -kasdw- will record asdw to the buffer k\nPressing _k afterwards will be the same as pressing asdw\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosExtra":
            self.submenue = src.interaction.TextMenu("\n\nMacros can be combined with each other. You can do this by replaying a macro while recording a macro\nFor example -qaaa- will record aaa to the buffer q.\nPressing -wddd_q- will record ddd_q to the buffer w. Pressing _w will be the same as dddaaa\nThe macro are referenced not copied. This means overwriting a macro will change alle macros referencing it. \n\nYou also can use multipliers within and with macros.\nPressing 5_q for example is the same as _q_q_q_q_q\n\n")
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosShortcuts":
            self.submenue = src.interaction.TextMenu("\n\nThere are some shortcuts that are usefull in combination with macros.\n\nctrl-d - aborts running the current macro\nctrl-p - pauses/unpauses running the current macro\nctrl-k writes macros fo disk\nctrl-o loads macros from disk\nctrl-x - saves and exits the game without interrupting running macros\n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: "+selection)


    def l4Info(self):

        options = []

        options.append(("level4_npcCreation","npc creation"))
        options.append(("level4_npcControl","npc control"))
        options.append(("level4_npcCreation","npc creation"))

        self.submenue = src.interaction.SelectionMenu("select the information you need",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level4_selection

    def level4_selection(self):

        if selection == "level4_npcCreation":
            self.submenue = src.interaction.TextMenu("\n\nYou can spawn new npcs. Npcs work just like your main character\nNpcs are generated from growth tanks. You need to activate the growth tank with a full flask in your inventory\nActivate the filled growth tank to spwan the npc. \n\n")
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: "+selection)

    def getState(self):
        state = super().getState()
        state["availableChallenges"] = self.availableChallenges
        state["knownBlueprints"] = self.knownBlueprints
        state["knownInfos"] = self.knownInfos
        return state

    def setState(self,state):
        super().setState(state)
        self.availableChallenges = state["availableChallenges"]
        self.knownBlueprints = state["knownBlueprints"]
        self.knownInfos = state["knownInfos"]

    def getLongInfo(self):
        text = """

This machine hold the information and practices needed to build a base.

Activate/Apply it to complete challenges and gain more information.

"""
        return text

class PortableChallenger(Item):
    type = "PortableChallenger"

    def __init__(self,xPosition=None,yPosition=None, name="PortableChallenger",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.portableChallenger,xPosition,yPosition,name=name,creator=creator)
        self.challenges = []
        self.done = False
        self.walkable = True
        self.bolted = False
        self.secret = ""

        self.attributesToStore.extend([
                "challenges","done","secret"])

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.challenges:
            self.done = True

        if self.done:
            self.submenue = src.interaction.TextMenu("all challenges completed return to auto tutor")
        else:
            if self.challenges[-1] == "gotoEastNorthTile":
                if not (character.room == None and character.xPosition//15 == 13 and character.yPosition//15 == 1):
                    text = "challenge: go to the most east north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 < 13:
                        text += "go futher east\n"
                    if character.yPosition//15 > 1:
                        text += "go futher north\n"

                    self.submenue = src.interaction.TextMenu(text)
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestNorthTile":
                if not (character.room == None and character.xPosition//15 == 1 and character.yPosition//15 == 1):
                    text = "challenge: go to the most west north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 > 1:
                        text += "go futher west\n"
                    if character.yPosition//15 > 1:
                        text += "go futher north\n"

                    self.submenue = src.interaction.TextMenu(text)
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestSouthTile":
                if not (character.room == None and character.xPosition//15 == 1 and character.yPosition//15 == 13):
                    text = "challenge: go to the most west south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 > 1:
                        text += "go futher west\n"
                    if character.yPosition//15 < 13:
                        text += "go futher south\n"

                    self.submenue = src.interaction.TextMenu(text)
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoEastSouthTile":
                if not (character.room == None and character.xPosition//15 == 13 and character.yPosition//15 == 13):
                    text = "challenge: go to the most east south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition//15 < 13:
                        text += "go futher east\n"
                    if character.yPosition//15 < 13:
                        text += "go futher south\n"

                    self.submenue = src.interaction.TextMenu(text)
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "9livingBlooms":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                numFound = 0
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type == "Bloom" and item.dead == False:
                                numFound += 1

                if not numFound >= 9:
                    self.submenue = src.interaction.TextMenu("challenge: find 9 living blooms\n\nchallenge in progress:\ngo to tile with 9 living blooms on it and activate challenger")
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "3livingSickBlooms":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                numFound = 0
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type == "SickBloom" and item.dead == False:
                                numFound += 1

                if not numFound >= 3:
                    self.submenue = src.interaction.TextMenu("challenge: find 3 living sick blooms\n\nchallenge in progress:\ngo to tile with 3 living sick blooms on it and activate challenger")
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "fullMoldCover":
                baseCoordinateX = character.xPosition-(character.xPosition%15)
                baseCoordinateY = character.yPosition-(character.yPosition%15)

                emptyFound = False
                for extraX in range(1,14):
                    for extraY in range(1,14):
                        hasMold = False
                        for item in character.container.getItemByPosition((baseCoordinateX+extraX,baseCoordinateY+extraY)):
                            if item.type in ["Mold","Sprout","Sprout2","Bloom","SickBloom","PoisonBloom","Bush","EncrustedBush","PoisonBush","EncrustedPoisonBush"]:
                                hasMold = True
                        if not hasMold:
                            emptyFound = True

                if emptyFound:
                    self.submenue = src.interaction.TextMenu("challenge: find tile completely covered in mold\n\nchallenge in progress:\ngo to a tile completed covered in mold and activate challenger")
                else:
                    self.submenue = src.interaction.TextMenu("challenge done")
                    self.challenges.pop()
            else:
                self.submenue = src.interaction.TextMenu("unkown challenge")

        character.macroState["submenue"] = self.submenue

        if not len(self.challenges):
            self.done = True

    def getLongInfo(self):
        text = """
item:

description:
TBD

%s
        """%(str(self.challenges))


class SimpleRunner(Item):
    type = "SimpleRunner"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="SimpleRunner",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.simpleRunner,xPosition,yPosition,name=name,creator=creator)
        self.command = None

        self.attributesToStore.extend([
                "command"])

    def apply(self,character):
        super().apply(character,silent=True)

        if self.command == None:
            if not len(character.macroState["macros"]):
                character.addMessage("no macro found - record a macro to store it in this machine")

            options = []
            for key,value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                options.append((key,compressedMacro))

            self.submenue = src.interaction.SelectionMenu("select the macro you want to store",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def storeMacro(self):
        key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return
            
        import copy
        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.addMessage("you store the command into the machine")

class MacroRunner(Item):
    type = "MacroRunner"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MacroRunner",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.macroRunner,xPosition,yPosition,name=name,creator=creator)
        self.command = None

        self.attributesToStore.extend([
                "command"])

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if self.command == None:
            if not len(character.macroState["macros"]):
                character.addMessage("no macro found - record a macro to store it in this machine")

            options = []
            for key,value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                options.append((key,compressedMacro))

            self.submenue = src.interaction.SelectionMenu("select the macro you want to store",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            import copy
            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def storeMacro(self):
        key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return
            
        import copy
        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.addMessage("you store the command into the machine")


'''
'''
class BluePrinter(Item):
    type = "BluePrinter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrinter",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.blueprinter,xPosition,yPosition,name=name,creator=creator)
        self.submenue = None
        self.text = None

        self.reciepes = [
                [["MemoryCell","Connector","FloorPlate"],"UniformStockpileManager"],
                [["MemoryCell","Connector","Command"],"ProductionManager"],
                [["MemoryCell","Bloom","SickBloom"],"AutoFarmer"],

                [["MemoryCell","Tank"],"MemoryBank"],
                [["MemoryCell","Puller"],"MemoryDump"],
                [["MemoryCell","Heater"],"SimpleRunner"],
                [["MemoryCell","Pusher"],"MemoryStack"],
                [["MemoryCell","Connector"],"MemoryReset"],

                [["Case","Sheet","Bloom"],"BloomContainer"],
                [["Case","Sheet"],"Container"],

                [["Sheet","pusher"],"Sorter"],
                [["Sheet","puller"],"Mover"],
                [["Stripe","Connector"],"RoomControls"],
                [["GooFlask","Tank"],"GrowthTank"],
                [["Radiator","Heater"],"StasisTank"],
                [["Mount","Tank"],"MarkerBean"],
                [["Bolt","Tank"],"PositioningDevice"],
                [["Bolt","puller"],"Watch"],
                [["Bolt","Heater"],"BackTracker"],
                [["Bolt","pusher"],"Tumbler"],
                [["Sheet","Heater"],"ItemUpgrader"],
                [["Sheet","Connector"],"ItemDowngrader"],
                [["Scrap","MetalBars"],"Scraper"],
                [["Tank","Connector"],"ReactionChamber"],

                [["Frame","MetalBars"],"Case"],
                [["Frame"],"PocketFrame"],
                [["Connector","MetalBars"],"MemoryCell"],

                [["Sheet","MetalBars"],"Tank"],
                [["Radiator","MetalBars"],"Heater"],
                [["Mount","MetalBars"],"Connector"],
                [["Stripe","MetalBars"],"pusher"],
                [["Bolt","MetalBars"],"puller"],
                [["Rod","MetalBars"],"Frame"],

                [["Bloom","MetalBars"],"SporeExtractor"],
                [["Sheet","Rod","Bolt"],"FloorPlate"],
                [["Coal","SickBloom"],"FireCrystals"],

                [["Command"],"AutoScribe"],
                [["Corpse"],"CorpseShredder"],

                [["Tank"],"GooFlask"],
                [["Heater"],"Boiler"],
                [["Connector"],"Door"],
                [["pusher"],"Drill"],
                [["puller"],"RoomBuilder"],

                [["Explosive"],"Bomb"],
                [["Bomb"],"Mortar"],

                [["Sheet"],"Sheet"],
                [["Radiator"],"Radiator"],
                [["Mount"],"Mount"],
                [["Stripe"],"Stripe"],
                [["Bolt"],"Bolt"],
                [["Rod"],"Rod"],

                [["Scrap"],"ScrapCompactor"],
                [["Coal"],"Furnace"],
                [["BluePrint"],"BluePrinter"],
                [["MetalBars"],"Wall"],

                [["GooFlask"],"GooDispenser"],
                [["Bloom"],"BloomShredder"],
                [["VatMaggot"],"MaggotFermenter"],
                [["BioMass"],"BioPress"],
                [["PressCake"],"GooProducer"],
            ]

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        sheet = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type == "Sheet":
                    sheet = item
                    break

        if not sheet:
            character.addMessage("no sheet - place sheet to the top/north")
            return

        inputThings = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)])
        if (self.xPosition,self.yPosition+1) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition,self.yPosition+1)])

        if not inputThings:
            character.addMessage("no items - place items to the left/west")
            return

        abstractedInputThings = {}
        for item in inputThings:
            abstractedInputThings[item.type] = {"item":item}

        reciepeFound = None
        for reciepe in self.reciepes:
            hasMaterials = True
            for requirement in reciepe[0]:
                if not requirement in abstractedInputThings:
                    hasMaterials = False

            if hasMaterials:
                reciepeFound = reciepe
                break

        if reciepeFound:
            # spawn new item
            new = BluePrint(creator=self)
            new.setToProduce(reciepeFound[1])
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            new.bolted = False

            targetFull = False
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True

            if targetFull:
                character.addMessage("the target area is full, the machine does not produce anything")
                return

            self.room.addItems([new])

            for itemType in reciepeFound[0]:
                self.room.removeItem(abstractedInputThings[itemType]["item"])
            self.room.removeItem(sheet)
            character.addMessage("you create a blueprint for "+reciepe[1])
            character.addMessage("items used: "+", ".join(reciepeFound[0]))
        else:
            character.addMessage("unable to produce blueprint from given items")
            return

    def getLongInfo(self):
        text = """

This machine creates Blueprints.

The Blueprinter has two inputs
It needs a sheet on the north to print the blueprint onto.
The items from the blueprint reciepe need to be added to the west or south.

"""
        return text

'''
'''
class BluePrint(Item):
    type = "BluePrint"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="BluePrint",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.blueprint,xPosition,yPosition,name=name,creator=creator)

        self.endProduct = None
        self.walkable = True
        self.baseName = name
        self.level = 1

        self.attributesToStore.extend([
                "endProduct","level"])

        self.setDescription()

    def setDescription(self):
        if not self.endProduct:
            self.description = self.baseName
        else:
            self.description = self.baseName+" for %s"%(self.endProduct,)

    def setToProduce(self, toProduce):
        self.endProduct = toProduce

        self.setDescription()

    def apply(self,character):
        super().apply(character,silent=True)

        character.addMessage("a blueprint for "+str(self.endProduct))

    '''
    set state from dict
    '''
    def setState(self,state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
item: Blueprint

decription:
This Blueprint holds the information on how to produce an item in machine readable form.

It needs to be loaded into a machine machine.
After loading the blueprint the machine machine is able to produce a machine that produces the the item the blue

this blueprint is for %s

This is a level %s item

"""%(self.endProduct,self.level)
        return text


'''
'''
class CoalMine(Item):
    type = "CoalMine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="coal mine",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.coalMine,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False

    def apply(self,character):
        if self.room:
            character.addMessage("this item cannot be used within rooms")
            return

        if not self.xPosition:
            character.addMessage("this machine has to be placed to be used")
            return

        targetFull = False
        if (self.xPosition+1,self.yPosition) in self.terrain.itemByCoordinates:
            if len(self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                targetFull = True
            for item in self.terrain.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                if item.walkable == False:
                    targetFull = True

        if targetFull:
            character.addMessage("the target area is full, the machine does not produce anything")
            return

        character.addMessage("you mine a piece of coal")

        # spawn new item
        new = Coal(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False
        self.terrain.addItems([new])

    def getLongInfo(self):
        text = """
item: CoalMine

description:
Use it to mine coal. The coal will be dropped to the east/rigth.

"""
        return text


'''
'''
class StasisTank(Item):
    type = "StasisTank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stasis tank",creator=None,noId=False):
        self.character = None
        super().__init__(src.canvas.displayChars.stasisTank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False
        self.character = None
        self.characterTimeEntered = None

    def eject(self):
        if self.character:
            self.room.addCharacter(self.character,self.xPosition,self.yPosition+1)
            self.character.stasis = False
            self.character = None
            self.characterTimeEntered = None

    def apply(self,character):
        if not self.room:
            character.addMessage("you can not use item outside of rooms")
            return

        if self.character and self.character.stasis:
            self.eject()
        else:
            options = []
            options.append(("enter","yes"))
            options.append(("noEnter","no"))
            self.submenue = src.interaction.SelectionMenu("The stasis tank is empty. You will not be able to leave it on your on.\nDo you want to enter it?",options)
            self.character = character
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.enterSelection

    def enterSelection(self):
        if self.submenue.selection == "enter":
            self.character.stasis = True
            self.room.removeCharacter(self.character)
            self.character.addMessage("you entered the stasis tank. You will not be able to move until somebody activates it")
            self.characterTimeEntered = src.gamestate.gamestate.tick
        else:
            self.character.addMessage("you do not enter the stasis tank")

    def configure(self,character):
        character.addMessage(src.gamestate.gamestate.tick)
        character.addMessage(self.characterTimeEntered)
        if src.gamestate.gamestate.tick > self.characterTimeEntered+100:
            self.eject()
        """
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character
        """

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("empty","no items left"))
            options.append(("fullInventory","inventory full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def getState(self):
        state = super().getState()

        if self.character:
            state["character"] = self.character.getState()
        else:
            state["character"] = None

        return state

    def setState(self,state):
        super().setState(state)

        if "character" in state and state["character"]:
            char = characters.Character()
            char.setState(state["character"])
            src.saveing.loadingRegistry.register(char)

            self.character = char
        else:
            state["character"] = None

    def getLongInfo(self):
        text = """

This machine allow to enter stasis. In stasis you do not need food and can not do anything.

You cannot leave the stasis tank on your own.

If the stasis tank is empty you can activate it to enter the stasis tank.

If the stasis tank is occupied, you can activate it to eject the character from the tank.
The ejected character will be placed to the south of the stasis tank and will start to act again.

"""
        return text
        

'''
'''
class PositioningDevice(Item):
    type = "PositioningDevice"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="positioning device",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.positioningDevice,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def apply(self,character):

        if not "x" in character.registers:
            character.registers["x"] = [0]
        character.registers["x"][-1] = character.xPosition
        if not "y" in character.registers:
            character.registers["y"] = [0]
        character.registers["y"][-1] = character.yPosition

        character.addMessage("your position is %s/%s"%(character.xPosition,character.yPosition,))

    def getLongInfo(self):
        text = """

this device allows you to determine your postion. Use it to get your position.

use it to determine your position. Your position will be shown as a message.

Also the position will be written to your registers.
The x-position will be written to the register x.
The y-position will be written to the register y.

"""
        return text

'''
'''
class Watch(Item):
    type = "Watch"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="watch",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.watch,xPosition,yPosition,name=name,creator=creator)

        self.creationTime = 0
        self.maxSize = 100

        self.attributesToStore.extend([
               "creationTime"])

        self.bolted = False
        self.walkable = True
        try:
            self.creationTime = src.gamestate.gamestate.tick
        except:
            pass

    def apply(self,character):

        time = src.gamestate.gamestate.tick-self.creationTime
        while time > self.maxSize:
            self.creationTime += self.maxSize
            time -= self.maxSize

        if not "t" in character.registers:
            character.registers["t"] = [0]
        character.registers["t"][-1] = src.gamestate.gamestate.tick-self.creationTime

        character.addMessage("it shows %s ticks"%(character.registers["t"][-1]))

    def getLongInfo(self):
        text = """
This device tracks ticks since creation. You can use it to measure time.
Activate it to get a message with the number of ticks passed.
Also the number of ticks will be written to the register t.
"""
        return text

'''
'''
class BackTracker(Item):
    type = "BackTracker"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="back tracker",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.backTracker,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
               "command"])

        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

        self.addListener(self.registerDrop,"dropped")
        self.addListener(self.registerPickUp,"pickUp")

    def apply(self,character):

        if self.tracking:
            self.tracked.delListener(self.registerMovement,"moved")
            character.addMessage("backtracking")
            self.tracking = False

            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))

            character.addMessage("runs the stored path")
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
            self.command = []
        else:
            self.tracked = character
            self.tracked.addListener(self.registerMovement,"moved")

            character.addMessage("it starts to track")
            self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

    def registerPickUp(self,param):
        if self.tracked:
            self.tracked.addMessage("pickUp")
            self.tracked.addMessage(param)

    def registerDrop(self,param):
        if self.tracked:
            self.tracked.addMessage("drop")
            self.tracked.addMessage(param)

    def registerMovement(self,param):
        if self.tracked:
            self.tracked.addMessage("mov")
            self.tracked.addMessage(param)

        mov = ""
        if param == "north":
            mov = "s"
        elif param == "south":
            mov = "w"
        elif param == "west":
            mov = "d"
        elif param == "east":
            mov = "a"
        self.command.insert(0,mov)

'''
'''
class Tumbler(Item):
    type = "Tumbler"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="tumbler",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.tumbler,xPosition,yPosition,name=name,creator=creator)

        self.strength = 7
        self.tracking = False
        self.tracked = None
        self.walkable = True
        self.command = []

    def apply(self,character):

        direction = src.gamestate.gamestate.tick%33%4
        strength = src.gamestate.gamestate.tick%self.strength+1

        direction = ["w","a","s","d"][direction]
        convertedCommands = [(direction,["norecord"])] * strength
        character.macroState["commandKeyQueue"] = convertedCommands + character.macroState["commandKeyQueue"]

        character.addMessage("tumbling %s %s "%(direction,strength))
        self.tracking = True

    def getLongInfo(self):
        text = """

This device tracks ticks since creation. You can use it to measure time.

Activate it to get a message with the number of ticks passed.

Also the number of ticks will be written to the register t.

"""
        return text

'''
'''
class GlobalMacroStorage(Item):
    type = "GlobalMacroStorage"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="global macro storage",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.globalMacroStorage,xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):

        self.character = character

        options = []
        options.append(("load","load macro from global storage"))
        options.append(("store","add macro to the global storage"))
        self.submenue = src.interaction.SelectionMenu("what do you want to do",options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSelection

    def actionSelection(self):
        selection =  self.submenue.getSelection()
        if selection == "load":
            try:
                with open("globalStorage.json","r") as globalStorageFile:
                    globalStorage = json.loads(globalStorageFile.read())
            except:
                globalStorage = []

            counter = 1

            options = []
            for entry in globalStorage:
                options.append((counter,entry["name"]))
                counter += 1
            self.submenue = src.interaction.SelectionMenu("what macro do you want to load?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.load

        if selection == "store":
            self.submenue = src.interaction.InputMenu("supply a name/description for the macro")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.store

    def load(self):
        try:
            with open("globalStorage.json","r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        rawMacros = globalStorage[self.submenue.getSelection()-1]["macro"]
        parsedMacros = {}

        state = "normal"
        for key,value in rawMacros.items():
            parsedMacro = []
            for char in value:
                if state == "normal":
                    if char == "/":
                        state = "multi"
                        combinedKey = ""
                        continue
                    parsedMacro.append(char)
                if state == "multi":
                    if char == "/":
                        state = "normal"
                        parsedMacro.append(combinedKey)
                    else:
                        combinedKey += char
            parsedMacros[key] = parsedMacro

        self.character.macroState["macros"] = parsedMacros
        self.character.addMessage("you load the macro %s from the macro storage"%(globalStorage[self.submenue.getSelection()-1]["name"]))

    def store(self):
        try:
            with open("globalStorage.json","r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        compressedMacros = {}
        for key,value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/"+keystroke+"/"
            compressedMacros[key] = compressedMacro

        globalStorage.append({"name":self.submenue.text,"macro":compressedMacros})

        with open("globalStorage.json","w") as globalStorageFile:
            globalStorageFile.write(json.dumps(globalStorage, indent = 10, sort_keys = True))

        self.character.addMessage("you store the macro in the global macro storage")

    def getLongInfo(self):
        text = """

This device is a one of a kind machine. It allows to store and load marcos between gamestates.

"""
        return text

'''
'''
class MemoryCell(Item):
    type = "MemoryCell"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="memory cell",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.memoryCell,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True

    def getLongInfo(self):
        text = """

A memory cell. Is complex building item. It is used to build logic items.

"""
        return text

class Bomb(Item):
    type = "Bomb"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="bomb",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.bomb,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.walkable = True

    def getLongInfo(self):

        text = """

A simple Bomb. It explodes when destroyed.

The explosion will damage/destroy everything on the current tile or the container.

Activate it to trigger a exlosion.

"""
        return text

    def apply(self,character):
        self.destroy()

    def destroy(self, generateSrcap=True):
        xPosition = self.xPosition
        yPosition = self.yPosition

        if xPosition:
            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition-1
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition-1
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

            new = Explosion(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            new.bolted = False
            self.container.addItems([new])
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
            event.setCallback({"container":new,"method":"explode"})
            self.container.addEvent(event)

        super().destroy()

        """
        if xPosition and yPosition:
            for item in self.container.itemByCoordinates[(xPosition,yPosition)]:
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()
        """


class Explosive(Item):
    type = "Explosive"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="explosive",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.bomb,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.walkable = True

    def getLongInfo(self):

        text = """

A Explosive. Simple building material. Used to build bombs.

"""
        return text

class Mortar(Item):
    type = "Mortar"
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="mortar",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.mortar,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.loaded = False
        self.loadedWith = None
        self.precision = 5

        self.attributesToStore.extend([
               "loaded","precision"])

    def apply(self,character):
        if not self.loaded:
            itemFound = None
            for item in character.inventory:
                if item.type == "Bomb":
                    itemFound = item
                    continue

            if not itemFound:
                character.addMessage("could not load mortar. no bomb in inventory")
                return

            character.addMessage("you load the mortar")

            character.inventory.remove(itemFound)
            self.loadedWith = itemFound
            self.loaded = True
        else:
            if not self.loadedWith:
                self.loaded = False
                return
            character.addMessage("you fire the mortar")
            bomb = self.loadedWith
            self.loadedWith = None
            self.loaded = False

            bomb.yPosition = self.yPosition
            bomb.xPosition = self.xPosition
            bomb.bolted = False

            distance = 10
            if (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision == 0:
                character.addMessage("you missfire (0)")
                self.precision += 10
                distance -= src.gamestate.gamestate.tick%10-10//2
                character.addMessage((distance,src.gamestate.gamestate.tick%10,10//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision == 1:
                character.addMessage("you missfire (1)")
                self.precision += 5
                distance -= src.gamestate.gamestate.tick%7-7//2
                character.addMessage((distance,src.gamestate.gamestate.tick%7,7//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision < 10:
                character.addMessage("you missfire (10)")
                self.precision += 2
                distance -= src.gamestate.gamestate.tick%3-3//2
                character.addMessage((distance,src.gamestate.gamestate.tick%3,3//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision < 100:
                character.addMessage("you missfire (100)")
                self.precision += 1
                distance -= src.gamestate.gamestate.tick%2-2//2
                character.addMessage((distance,src.gamestate.gamestate.tick%2,2//2))

            bomb.yPosition += distance

            self.container.addItems([bomb])

            bomb.destroy()

    def getLongInfo(self):

        text = """

A mortar. Load it with bombs and activate it to fire.

It fires 10 steps to the south. Its current precision is """+str(self.precision)+""".

"""
        return text

class Chute(Item):
    type = "Chute"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="chute",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.fireCrystals,xPosition,yPosition,creator=creator,name=name)

    def apply(self,character):
        if self.xPosition == None or not self.container:
            character.addMessage("This has to be placed in order to be used")
            return

        if character.inventory:
            item = character.inventory[-1]
            character.inventory.remove(item)
            item.xPosition = self.xPosition+1
            item.yPosition = self.yPosition

            self.container.addItems([item])

class FireCrystals(Item):
    type = "FireCrystals"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="fireCrystals",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.fireCrystals,xPosition,yPosition,creator=creator,name=name)
        self.walkable = True

    def apply(self,character):
        character.addMessage("The fire crystals start sparkling")
        self.startExploding()

    def startExploding(self):
        if not self.xPosition:
            return
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+2+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"explode"})
        self.container.addEvent(event)

    def explode(self):
        self.destroy()

    def destroy(self, generateSrcap=False):
        if not self.xPosition or not self.yPosition:
            return

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition-1
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition-1
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        new = Explosion(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition+1
        self.container.addItems([new])
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1,creator=self)
        event.setCallback({"container":new,"method":"explode"})
        self.container.addEvent(event)

        super().destroy(generateSrcap=False)

class ReactionChamber(Item):
    type = "ReactionChamber"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="reactionChamber",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.reactionChamber,xPosition,yPosition,creator=creator,name=name)
        self.contains = ""
        
    def apply(self,character):

        options = []
        options.append(("add","add"))
        options.append(("boil","boil"))
        options.append(("mix","mix"))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

    def doAction(self):
        selection = self.submenue.selection
        if (selection == "add"):
            #self.add()
            pass
        if (selection == "mix"):
            self.mix()
        if (selection == "boil"):
            self.boil()

    def add(self,chemical):
        if len(self.contains) >= 10:
            self.character.addMessage("the reaction chamber is full")
            return

        self.character.addMessage("you add a "+chemical.type+" to the reaction chamber")

    def mix(self,granularity=9):
        if len(self.contains) < 10:
            self.character.addMessage("the reaction chamber is not full")
            return
            
        self.character.addMessage("the reaction chambers contents are mixed with granularity %s"%(granularity))

    def boil(self):

        self.character.addMessage("the reaction chambers contents are boiled")
        self.contents = self.contents[19]+self.contents[0:19]
    
    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

contains:

"""+self.contains

        return text


class ReactionChamber_2(Item):
    type = "ReactionChamber_2"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="reactionChamber_2",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.reactionChamber,xPosition,yPosition,creator=creator,name=name)
        
    def apply(self,character):

        coalFound = None
        flaskFound = None

        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)]:
                if item.type in "Coal":
                    coalFound = item
                if item.type in "GooFlask" and item.uses == 100:
                    flaskFound = item

        if not coalFound or not flaskFound:
            character.addMessage("reagents not found. place coal and a full goo flask to the left/west")
            return

        self.room.removeItem(coalFound)
        self.room.removeItem(flaskFound)
        
        explosive = Explosive(creator=self)
        explosive.xPosition = self.xPosition+1
        explosive.yPosition = self.yPosition
        explosive.bolted = False

        byProduct = FireCrystals(creator=self)
        byProduct.xPosition = self.xPosition
        byProduct.yPosition = self.yPosition+1
        byProduct.bolted = False

        self.room.addItems([byProduct,explosive])
    
    def getLongInfo(self):

        text = """

A raction chamber. It is used to mix chemicals together.

"""
        return text

class Explosion(Item):
    type = "Explosion"

    def __init__(self,xPosition=0,yPosition=0,amount=1,name="explosion",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.explosion,xPosition,yPosition,creator=creator,name=name)

    def pickUp(self,character):
        pass
    def apply(self,character):
        self.explode()
        pass
    def drop(self,character):
        pass
    def explode(self):

        if self.room:
            self.room.damage()
        elif self.terrain:
            for room in self.terrain.getRoomsOnFineCoordinate((self.xPosition,self.yPosition)):
                room.damage()

        if self.xPosition and self.yPosition:
            for character in self.container.characters:
                if (character.xPosition == self.xPosition and character.yPosition == self.yPosition):
                    character.die()

            for item in self.container.getItemByPosition((self.xPosition,self.yPosition,self.zPosition)):
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()

        if self.container:
            self.container.removeItem(self)

class Chemical(Item):
    type = "Chemical"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.fireCrystals,xPosition,yPosition,creator=creator,name="chemical")
        self.composition = b"cccccggggg"

    def apply(self,character):
        import hashlib

        results = []
        counter = 0

        while 1:

            tmp = random.choice(["mix","shift"])

            if tmp == "mix":
                self.mix(character)
            elif tmp == "switch":
                self.mix(character)
            elif tmp == "shift":
                self.shift()

            test = hashlib.sha256(self.composition[0:9])
            character.addMessage(counter)

            result = int(test.digest()[-1])
            result2 = int(test.digest()[-2])
            if result < 15:
                character.addMessage(test.digest())
                character.addMessage(result)
                character.addMessage(result2)
                break

            counter += 1

        #character.addMessage(results)

    def shift(self):
        self.composition = self.composition[1:]+self.composition[0:1]

    def mix(self,character):
        part1 = self.composition[0:5]
        part2 = self.composition[5:10]

        self.composition = part1[0:1]+part2[0:1]+part1[1:2]+part2[1:2]+part1[2:3]+part2[2:3]+part1[3:4]+part2[3:4]+part1[4:5]+part2[4:5]

class Spawner(Item):
    type = "Spawner"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.fireCrystals,xPosition,yPosition,creator=creator,name="spawner")
        self.charges = 1

    def apply(self,character):

        if not self.terrain:
            character.addMessage("this has to be placed outside to be used")
            return
        corpses = []
        for item in character.inventory:
            if item.type == "Corpse":
                corpses.append(item)

        for corpse in corpses:
            self.charges += 1
            character.inventory.remove(corpse)

        if self.charges:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+100,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        character = characters.Character(src.canvas.displayChars.staffCharactersByLetter["a".lower()],self.xPosition+1,self.yPosition,name="a",creator=self)

        character.solvers = [
                  "SurviveQuest",
                  "Serve",
                  "NaiveMoveQuest",
                  "MoveQuestMeta",
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "NaiveDropQuest",
                  "PickupQuestMeta",
                  "DrinkQuest",
                  "ExamineQuest",
                  "FireFurnaceMeta",
                  "CollectQuestMeta",
                  "WaitQuest"
                  "NaiveDropQuest",
                  "DropQuestMeta",
                  "NaiveMurderQuest",
                ]

        character.inventory.append(Tumbler(None,None,creator=self))
        character.inventory.append(BackTracker(None,None,creator=self))
        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["WALKTo"] = splitCommand("$=aa$=ww$=ss$=dd")
        """
        character.macroState["macros"]["MURDEr"] = splitCommand("ope_WALKTomijj_u")
        character.macroState["macros"]["u"] = splitCommand("%E_i_o")
        character.macroState["macros"]["i"] = splitCommand("_MURDEr")
        character.macroState["macros"]["o"] = splitCommand("%c_p_a")
        character.macroState["macros"]["p"] = splitCommand("_GETBODYs")
        character.macroState["macros"]["a"] = splitCommand("ijj_u")
        character.macroState["macros"]["s"] = splitCommand("_u")
        character.macroState["macros"]["GETBODYs"] = splitCommand("opM_WALKTokijsjajijsjijj_u")
        character.macroState["macros"]["STARt"] = splitCommand("ijsj_a")
        character.macroState["macros"]["m"] = splitCommand("_STARt")
        """
        character.macroState["macros"]["_GOTOTREe"] = splitCommand("opt_WALKTo")
        character.macroState["macros"]["_RANDOMWALk"] = splitCommand("ijj")
        character.macroState["macros"]["_a"] = splitCommand("_RANDOMWALk")
        character.macroState["macros"]["m"] = splitCommand("ijj_GOTOTREe")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100000
        self.container.addCharacter(character,self.xPosition+1,self.yPosition)

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+100,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

        self.charges -= 1

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
"""%(self.charges)

class MoldSpore(Item):
    type = "MoldSpore"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.moldSpore,xPosition,yPosition,creator=creator,name="mold spore")
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return
        self.startSpawn()
        character.addMessage("you activate the mold spore")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: MoldSpore

description:
This is a mold spore 

put it on the ground and activate it to plant it
"""

class Mold(Item):
    type = "Mold"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.moss,xPosition,yPosition,creator=creator,name="mold")
        self.charges = 2
        self.walkable = True
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        character.satiation += 2
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the mold and gain 2 satiation")

    def startSpawn(self):
        if self.charges and self.container:
            if not (self.xPosition and self.yPosition and self.terrain):
                return
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%1000,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if self.charges and self.container:
            if not (self.xPosition and self.yPosition):
                return
            direction = (2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%4
            direction = random.choice([0,1,2,3])
            if direction == 0:
                newPos = (self.xPosition,self.yPosition+1,self.zPosition)
            if direction == 1:
                newPos = (self.xPosition+1,self.yPosition,self.zPosition)
            if direction == 2:
                newPos = (self.xPosition,self.yPosition-1,self.zPosition)
            if direction == 3:
                newPos = (self.xPosition-1,self.yPosition,self.zPosition)

            #if (((newPos[0]%15 == 0 or newPos[0]%15 == 14) and not (newPos[1]%15 in (8,))) or
            #    ((newPos[1]%15 == 0 or newPos[1]%15 == 14) and not (newPos[0]%15 in (8,)))):
            #    return

            itemList = self.container.getItemByPosition(newPos)
            if not len(itemList):
                new = itemMap["Mold"](creator=self)
                new.xPosition = newPos[0]
                new.yPosition = newPos[1]
                self.container.addItems([new])
                new.startSpawn()
            elif len(itemList) > 0:
                if itemList[-1].type == "Mold":
                    self.charges += itemList[-1].charges//2
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Sprout"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Sprout":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Sprout2"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                elif itemList[-1].type == "Sprout2":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    if (newPos[0]%15,newPos[1]%15) in ((7,7,0),):
                        new = itemMap["CommandBloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                    elif (newPos[0]%15,newPos[1]%15) in ((1,7,0),(7,1,0),(13,7,0),(7,13,0)) and self.container.getItemByPosition((newPos[0]-newPos[0]%15+7,newPos[1]-newPos[1]%15+7,0)) and self.container.getItemByPosition((newPos[0]-newPos[0]%15+7,newPos[1]-newPos[1]%15+7,0))[-1].type == "CommandBloom":
                        new = itemMap["CommandBloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                    else:
                        new = itemMap["Bloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                        new.startSpawn()
                elif itemList[-1].type == "Bloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["SickBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                    new.startSpawn()
                elif itemList[-1].type == "Corpse":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["PoisonBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "SickBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "PoisonBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["PoisonBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Bush":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = itemMap["EncrustedBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type == "EncrustedBush":
                    new = itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                    itemList[-1].tryToGrowRoom(new)

                elif itemList[-1].type in ["PoisonBush","EncrustedPoisonBush"]:
                    new = itemMap["PoisonBloom"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type in ["Coal"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type in ["MoldFeed"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = itemMap["Bloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type in ["CommandBloom"]:
                    itemList[-1].charges += 1

        self.charges -= 1
        if self.charges:
            self.startSpawn()

    def getLongInfo(self):
        return """
item: Mold

description:
This is a patch of mold

you can eat it to gain 2 satiation.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class Sprout(Item):
    type = "Sprout"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sprout,xPosition,yPosition,creator=creator,name="sprout")
        self.walkable = True

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return

        character.satiation += 10
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the sprout and gain 10 satiation")

    def getLongInfo(self):
        return """
item: Sprout

description:
This is a mold patch that shows the first sign of a bloom.

you can eat it to gain 10 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

class Sprout2(Item):
    type = "Sprout2"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sprout2,xPosition,yPosition,creator=creator,name="sprout2")
        self.walkable = True

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return

        character.satiation += 25
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the sprout and gain 25 satiation")

    def getLongInfo(self):
        return """
item: Sprout2

description:
This is a mold patch that developed a bloom sprout.

you can eat it to gain 25 satiation.
"""

    def destroy(self, generateSrcap=True):

        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()

        super().destroy(generateSrcap=False)

class Bloom(Item):
    type = "Bloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bloom,xPosition,yPosition,creator=creator,name="bloom")
        self.bolted = False
        self.walkable = True
        self.dead = False
        self.attributesToStore.extend([
               "dead"])

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return

        if self.dead:
            character.satiation += 100
            self.destroy(generateSrcap=False)
            character.addMessage("you eat the dead bloom and gain 100 satiation")
        else:
            character.satiation += 115
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
            character.addMessage("you eat the bloom and gain 115 satiation")

    def startSpawn(self):
        if not self.dead:
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%10000,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def pickUp(self,character):
        self.bolted = False
        self.localSpawn()
        self.dead = True
        super().pickUp(character)

    def spawn(self):
        if self.dead:
            return
        if not (self.xPosition and self.yPosition):
            return
        if not self.container:
            return
        direction = (2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%4
        direction = (random.randint(1,13),random.randint(1,13))
        newPos = (self.xPosition-self.xPosition%15+direction[0],self.yPosition-self.yPosition%15+direction[1],self.zPosition)

        if self.container.getItemByPosition(newPos):
            new = itemMap["Mold"](creator=self)
            new.xPosition = newPos[0]
            new.yPosition = newPos[1]
            self.container.addItems([new])
            new.startSpawn()

    def localSpawn(self):
        if not self.dead:
            new = itemMap["Mold"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            new.charges = 4
            self.container.addItems([new])
            new.startSpawn()

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: Bloom

description:
This is a mold bloom. 

you can eat it to gain %s satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):
        self.localSpawn()

        super().destroy(generateSrcap=False)

class SickBloom(Item):
    type = "SickBloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sickBloom,xPosition,yPosition,creator=creator,name="sick bloom")
        self.walkable = True
        self.charges = 1
        self.dead = False
        self.attributesToStore.extend([
               "charges","dead"])

    def apply(self,character):
        if self.charges and not self.dead:
            if isinstance(character,src.characters.Monster):
                if character.phase == 1:
                    character.satiation += 300
                    if character.satiation > 1000:
                        character.satiation = 1000
                    self.spawn()
                    self.charges -= 1
                    self.dead = True
                elif character.phase == 2:
                    character.enterPhase3()
                    self.charges -= 1
                    self.destroy(generateSrcap=False)
                else:
                    character.satiation += 400
                    self.charges -= 1
            else:
                self.spawn()
                character.satiation += 100
                if character.satiation > 1000:
                    character.satiation = 1000
        else:
            character.satiation += 100
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
        character.addMessage("you eat the sick bloom and gain 100 satiation")

    def pickUp(self,character):
        self.bolted = False
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def startSpawn(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%2500,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        if self.dead:
            return

        character = src.characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "NaivePickupQuest",
                  "PickupQuestMeta",
                  "NaiveMurderQuest",
                  "NaiveDropQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["w"] = splitCommand("wj")
        character.macroState["macros"]["a"] = splitCommand("aj")
        character.macroState["macros"]["s"] = splitCommand("sj")
        character.macroState["macros"]["d"] = splitCommand("dj")

        counter = 1
        command = ""
        directions =["w","a","s","d"]
        while counter < 8:
            command += "j%s_%sk"%(random.randint(1,counter*4),directions[random.randint(0,3)])
            counter += 1
        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 10
        if self.container:
            self.container.addCharacter(character,self.xPosition,self.yPosition)

        self.charges -= 1

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: SickBloom

description:
This is a mold bloom. Its spore sacks are swollen and developed a protective shell

you can eat it to gain %s satiation.
"""%(satiation)

    def destroy(self, generateSrcap=True):

        if not self.dead:
            new = itemMap["Mold"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            new.startSpawn()

        super().destroy(generateSrcap=False)

class PoisonBloom(Item):
    type = "PoisonBloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.poisonBloom,xPosition,yPosition,creator=creator,name="poison bloom")
        self.walkable = True
        self.dead = False
        self.bolted = False
        self.attributesToStore.extend([
               "dead"])

    def apply(self,character):

        if not self.terrain:
            self.dead = True

        character.die()

        if not self.dead:
            new = itemMap["PoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

        character.addMessage("you eat the poison bloom and die")

        self.destroy(generateSrcap=False)

    def pickUp(self,character):
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def getLongInfo(self):
        return """
name: poison bloom

description:
This is a mold bloom. Its spore sacks shriveled and are covered in green slime.

You can eat it to die.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class PoisonBush(Item):
    type = "PoisonBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.poisonBush,xPosition,yPosition,creator=creator,name="poison bush")
        self.walkable = False
        self.charges = 0
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        self.charges += 1
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        if self.charges > 10:
            
            new = itemMap["EncrustedPoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            
            self.container.removeItem(self)

        character.addMessage("you give your blood to the poison bush")

    def spawn(self,distance=1):
        if not (self.xPosition and self.yPosition):
            return
        direction = (2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%4
        direction = (random.randint(1,distance+1),random.randint(1,distance+1))
        newPos = (self.xPosition+direction[0]-5,self.yPosition+direction[1]-5)

        if newPos[0] < 1 or newPos[1] < 1 or newPos[0] > 15*15-2 or newPos[1] > 15*15-2:
            return

        if not (newPos in self.container.itemByCoordinates and len(self.container.itemByCoordinates[newPos])):
            new = itemMap["PoisonBloom"](creator=self)
            new.xPosition = newPos[0]
            new.yPosition = newPos[1]
            self.container.addItems([new])

    def getLongInfo(self):
        return "poison charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Poison Bush

description:
This a cluster of blooms with a network veins connecting them. Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""

    def destroy(self, generateSrcap=True):
        new = itemMap["FireCrystals"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])

        character = characters.Exploder(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                  "DrinkQuest",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        command = ""
        if src.gamestate.gamestate.tick%4 == 0:
            command += "A"
        if src.gamestate.gamestate.tick%4 == 1:
            command += "W"
        if src.gamestate.gamestate.tick%4 == 2:
            command += "S"
        if src.gamestate.gamestate.tick%4 == 3:
            command += "D"

        if self.xPosition%4 == 0:
            command += "A"
        if self.xPosition%4 == 1:
            command += "W"
        if self.xPosition%4 == 2:
            command += "S"
        if self.xPosition%4 == 3:
            command += "D"

        if self.yPosition%4 == 0:
            command += "A"
        if self.yPosition%4 == 1:
            command += "W"
        if self.yPosition%4 == 2:
            command += "S"
        if self.yPosition%4 == 3:
            command += "D"

        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

class EncrustedPoisonBush(Item):
    type = "EncrustedPoisonBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.encrustedPoisonBush,xPosition,yPosition,creator=creator,name="test")
        self.walkable = False

    def apply(self,character):
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        character.addMessage("you give your blood to the encrusted poison bush and loose 100 satiation")

    def getLongInfo(self):
        return """
item: EncrustedPoisonBush

description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.
Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""

    def destroy(self, generateSrcap=True):
        new = itemMap["FireCrystals"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        #new.startExploding()

        character = src.characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "NaivePickupQuest",
                  "PickupQuestMeta",
                  "NaiveMurderQuest",
                  "NaiveDropQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        command = "opc"
        if src.gamestate.gamestate.tick%2:
            command += "$=aam$=ddm"
            command += "$=wwm$=ssm"
        else:
            command += "$=wwm$=ssm"
            command += "$=aam$=ddm"

        command += "_m"
        character.macroState["macros"]["m"] = splitCommand(command)

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

class Bush(Item):
    type = "Bush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bush,xPosition,yPosition,creator=creator,name="bush")
        self.walkable = False
        self.charges = 10
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        if self.charges > 10:
            new = itemMap["EncrustedBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

            self.container.removeItem(self)

            character.addMessage("the bush encrusts")

        if self.charges:
            character.satiation += 5
            self.charges -= 1
            character.addMessage("you eat from the bush and gain 5 satiation")
        else:
            self.destroy()

    def getLongInfo(self):
        return "charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Bush

description:
This a patch of mold with multiple blooms and a network vains connecting them.

actions:
If you can eat it to gain 5 satiation.
"""

    def destroy(self, generateSrcap=True):
        new = itemMap["Coal"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        super().destroy(generateSrcap=False)

class EncrustedBush(Item):
    type = "EncrustedBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.encrustedBush,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False

    def getLongInfo(self):
        return """
item: EncrustedBush

description:
This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall.

"""

    def destroy(self, generateSrcap=True):
        new = itemMap["Coal"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])

        character = src.characters.Monster(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "NaivePickupQuest",
                  "PickupQuestMeta",
                  "NaiveMurderQuest",
                  "NaiveDropQuest",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["w"] = splitCommand("wj")
        character.macroState["macros"]["a"] = splitCommand("aj")
        character.macroState["macros"]["s"] = splitCommand("sj")
        character.macroState["macros"]["d"] = splitCommand("dj")

        counter = 1
        command = ""
        directions =["w","a","s","d"]
        while counter < 8:
            command += "j%s_%sk"%(random.randint(1,counter*4),directions[random.randint(0,3)])
            counter += 1
        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 10
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

    def tryToGrowRoom(self, spawnPoint, character=None):
        if not self.terrain:
            return
        if not self.container:
            return

        upperLeftEdge = [self.xPosition,self.yPosition]
        sizeX = 1
        sizeY = 1

        growBlock = None

        continueExpanding = True
        while continueExpanding:
            continueExpanding = False

            #expand west
            if upperLeftEdge[0]%15 > 0:
                rowOk = True
                for y in range(0,sizeY):
                    items = self.container.getItemByPosition((upperLeftEdge[0]-1,upperLeftEdge[1]+y))
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeX += 1
                    upperLeftEdge[0] -= 1
                    continueExpanding = True

            #expand north
            if upperLeftEdge[1]%15 > 0:
                rowOk = True
                for x in range(0,sizeX):
                    items = self.container.getItemByPosition((upperLeftEdge[0]+x,upperLeftEdge[1]-1))
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeY += 1
                    upperLeftEdge[1] -= 1
                    continueExpanding = True

            #expand south
            if upperLeftEdge[1]%15+sizeY < 14:
                rowOk = True
                for x in range(0,sizeX):
                    items = self.container.getItemByPosition((upperLeftEdge[0]+x,upperLeftEdge[1]+sizeY))
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeY += 1
                    continueExpanding = True

            #expand east
            if upperLeftEdge[0]%15+sizeX < 14:
                rowOk = True
                for y in range(0,sizeY):
                    items = self.container.getItemByPosition((upperLeftEdge[0]+sizeX,upperLeftEdge[1]+y))
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeX += 1
                    continueExpanding = True

        if sizeX < 3 or sizeY < 3:
            if growBlock:
                new = itemMap["EncrustedBush"](creator=self)
                new.xPosition = growBlock.xPosition
                new.yPosition = growBlock.yPosition
                self.container.addItems([new])
                growBlock.container.removeItem(growBlock)
            return

        keepItems = []
        doorPos = ()
        for x in range(0,sizeX):
            for y in range(0,sizeY):
                if x == 0 or y == 0 or x == sizeX-1 or y == sizeY-1:
                    if x == 0 and y == 1:
                        item = Door(creator=self,bio=True)
                    else:
                        items = self.container.getItemByPosition((upperLeftEdge[0]+x,upperLeftEdge[1]+y))
                        if not items:
                            return
                        item = items[0]
                        item.container.removeItem(item)
                    item.xPosition = x
                    item.yPosition = y
                    keepItems.append(item)

        room = src.rooms.EmptyRoom(upperLeftEdge[0]//15,upperLeftEdge[1]//15,upperLeftEdge[0]%15,upperLeftEdge[1]%15,creator=self,bio=True)
        self.terrain.addRooms([room])
        room.reconfigure(sizeX,sizeY,keepItems)

class MoldFeed(Item):
    type = "MoldFeed"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.moldFeed,xPosition,yPosition,creator=creator,name="mold feed")
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        return """
item: MoldFeed

description:

This is a good base for mold growth. If mold grows onto it, it will grow into a bloom.

can be eaten
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

    def apply(self, character):
        character.satiation += 1000
        if character.satiation > 1000:
            character.satiation = 1000
        character.addMessage("you eat the mold feed and gain satiation")
        self.destroy()

class SeededMoldFeed(Item):
    type = "SeededMoldFeed"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.seededMoldFeed,xPosition,yPosition,creator=creator,name="seeded mold feed")
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return

        self.startSpawn()
        character.addMessage("you activate the seeded mold feed")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.charges = 8
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: SeededMoldFeed

description:

This is mold feed mixed with mold spores. 
Place it on the ground and activate it to start mold growth.
The seeded mold feed grows stronger then a mold spore on its own.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

class BloomContainer(Item):
    type = "BloomContainer"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bloomContainer,xPosition,yPosition,creator=creator,name="bloom container")

        self.charges = 0
        self.maxCharges = 15
        self.level = 1

        self.attributesToStore.extend([
               "charges","maxCharges","level"])

    def getLongInfo(self):
        return """
item: BloomContainer

description:
The bloom container is used to carry an store blooms.

it has %s blooms (charges) in it. It can hold a maximum of %s blooms.

This is a level %s item.

actions:

= loading blooms =
prepare by placing the bloom container on the ground and placing blooms around the container.
Activate the bloom container and select the option "load bloom" to load the blooms into the container.

= unload blooms =
prepare by placing the bloom container on the ground.
Activate the bloom container and select the option "unload bloom" to unload the blooms to the east.
"""%(self.charges,self.maxCharges,self.level)

    def apply(self,character):
        options = []
        options.append(("load","load blooms"))
        options.append(("unload","unload blooms"))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    def doSelection(self):
        selection = self.submenue.selection
        if selection == "load":
            if self.charges >= self.maxCharges:
                self.character.addMessage("bloom container full. no blooms loaded")
                return

            blooms = []
            positions = [(self.xPosition+1,self.yPosition),(self.xPosition-1,self.yPosition),(self.xPosition,self.yPosition+1),(self.xPosition,self.yPosition-1),]
            for position in positions:
                for item in self.container.getItemByPosition(position):
                    if item.type == "Bloom":
                        blooms.append(item)

            if not blooms:
                self.character.addMessage("no blooms to load")
                return

            for bloom in blooms:
                if self.charges >= self.maxCharges:
                    self.character.addMessage("bloom container full. not all blooms loaded")
                    return

                self.container.removeItem(bloom)
                self.charges += 1

            self.character.addMessage("blooms loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.addMessage("no blooms to unload")
                return
            
            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition)):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1
            
            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.addMessage("target area full. no blooms unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.charges:
                new = Bloom(creator=self)
                new.xPosition = self.xPosition+1
                new.yPosition = self.yPosition
                new.dead = True

                toAdd.append(new)
                self.charges -= 1
            self.container.addItems(toAdd)

class Container(Item):
    type = "Container"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        self.contained = []
        super().__init__(src.canvas.displayChars.container,xPosition,yPosition,creator=creator,name="container")

        self.charges = 0
        self.maxItems = 10
        self.level = 1

        self.attributesToStore.extend([
               "charges","maxCharges","level"])

    def getLongInfo(self):
        text = """
item: Container

description:
The container is used to carry and store small items.

it holds the items. It can hold a maximum of %s items.

This is a level %s item.

"""%(self.maxItems,self.level)

        if self.contained:
            for item in self.contained:
                text += """
* %s
%s"""%(item.name,item.description)
        else:
            text += """
the container is empty
"""

        text += """ 

actions:

= load items =
prepare by placing the bloom container on the ground and placing the items to the east of the container.
Activate the bloom container and select the option "load items" to load the blooms into the container.

= unload items =
prepare by placing the container on the ground.
Activate the container and select the option "unload items" to unload the items.
"""
        return text
            
    def getState(self):
        state = super().getState()
        state["contained"] = []
        for item in self.contained:
            state["contained"].append(item.getState())
        return state

    def setState(self,state):
        super().setState(state)
        
        if "contained" in state:
            for item in state["contained"]:
                self.contained.append(getItemFromState(item))

    def apply(self,character):
        options = []
        options.append(("load","load items"))
        options.append(("unload","unload items"))
        self.submenue = src.interaction.SelectionMenu("select the item to produce",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    def doSelection(self):
        selection = self.submenue.selection
        if selection == "load":
            if len(self.contained) >= self.maxItems:
                self.character.addMessage("container full. no items loaded")
                return

            items = []
            for item in self.container.getItemByPosition((self.xPosition-1,self.yPosition)):
                if item.walkable:
                    items.append(item)


            if not items:
                self.character.addMessage("no small items to load")
                return

            for item in items:
                if len(self.contained) >= self.maxItems:
                    self.character.addMessage("container full. not all items loaded")
                    return

                self.contained.append(item)

                self.container.removeItem(item)
                self.charges += 1

            self.character.addMessage("items loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.addMessage("no items to unload")
                return
            
            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition((self.xPosition+1,self.yPosition)):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1
            
            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.addMessage("target area full. no items unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.contained:
                new = self.contained.pop()
                new.xPosition = self.xPosition+1
                new.yPosition = self.yPosition

                toAdd.append(new)
            self.container.addItems(toAdd)


class TrailHead(Item):
    type = "TrailHead"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.floor_node,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False
        targets = []

    def getLongInfo(self):
        return """
item: TrailHead

description:
You can use it to create paths
"""

class SwarmIntegrator(Item):
    type = "SwarmIntegrator"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.floor_node,xPosition,yPosition,creator=creator,name="encrusted bush")
        self.walkable = False
        self.faction = "swarm"

    def getLongInfo(self):
        return """
item: SwarmIntegrator

description:
You can use it to create paths
"""

    def apply(self,character):
        command = "aopR.$a*13.$w*13.$s*13.$d*13.$=aa$=ww$=ss$=dd"
        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

class AutoFarmer(Item):
    type = "AutoFarmer"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.autoFarmer,xPosition,yPosition,creator=creator,name="auto farmer")
        self.walkable = True
        self.bolted = True

    def apply(self,character):
        if not self.terrain:
            character.addMessage("the auto farmer cannot be used within rooms")
            return

        if not (self.xPosition%15 == 7 and self.yPosition%15 == 7):
            character.addMessage("the auto farmer needs to be placed in the middle of a tile")
            return
        
        if not self.bolted:
            character.addMessage("the auto farmer digs into the ground and is now ready for use")
            self.bolted = True

        if isinstance(character,src.characters.Monster):
            character.die()
            return

        if len(character.inventory) > 9:
            character.addMessage("inventory full")
            return

        command = ""
        length = 1
        pos = [self.xPosition,self.yPosition]
        path = []
        path.append((pos[0],pos[1]))
        while length < 13:
            if length%2 == 1:
                for i in range(0,length):
                    pos[1] -= 1
                    path.append((pos[0],pos[1]))
                for i in range(0,length):
                    pos[0] += 1
                    path.append((pos[0],pos[1]))
            else:
                for i in range(0,length):
                    pos[1] += 1
                    path.append((pos[0],pos[1]))
                for i in range(0,length):
                    pos[0] -= 1
                    path.append((pos[0],pos[1]))
            length += 1
        for i in range(0,length-1):
            pos[1] -= 1
            path.append((pos[0],pos[1]))

        foundSomething = False
        lastCharacterPosition = path[0]
        for pos in path[1:]:
            items = self.container.getItemByPosition(pos)
            if not items:
                continue
            item = items[0]
            if item.type in ("Bloom","SickBloom","Coal"):
                if lastCharacterPosition[0] > pos[0]:
                    command += str(lastCharacterPosition[0]-pos[0])+"a"
                if lastCharacterPosition[0] < pos[0]:
                    command += str(pos[0]-lastCharacterPosition[0])+"d"
                if lastCharacterPosition[1] > pos[1]:
                    command += str(lastCharacterPosition[1]-pos[1])+"w"
                if lastCharacterPosition[1] < pos[1]:
                    command += str(pos[1]-lastCharacterPosition[1])+"s"

                if items[0].type in ("Sprout","Sprout2","Mold"):
                    command += "j"
                if items[0].type == "Bloom":
                    command += "k"
                if items[0].type == "SickBloom":
                    command += "k"
                if items[0].type == "Coal":
                    command += "k"
                foundSomething = True

                lastCharacterPosition = pos

            if items[0].type in ("Bush"):
                if lastCharacterPosition[0] > pos[0]:
                    command += str(lastCharacterPosition[0]-pos[0])+"a"
                    lastDirection = "a"
                if lastCharacterPosition[0] < pos[0]:
                    command += str(pos[0]-lastCharacterPosition[0])+"d"
                    lastDirection = "d"
                if lastCharacterPosition[1] > pos[1]:
                    command += str(lastCharacterPosition[1]-pos[1])+"w"
                    lastDirection = "w"
                if lastCharacterPosition[1] < pos[1]:
                    command += str(pos[1]-lastCharacterPosition[1])+"s"
                    lastDirection = "s"
                command += "j"
                for i in range(0,11):
                    command += "J"+lastDirection
                command += lastDirection+"k"

            if items[0].type in ("EncrustedBush"):
                break

        found = False

        pos = (self.xPosition,self.yPosition)
        if lastCharacterPosition[0] > pos[0]:
            command += str(lastCharacterPosition[0]-pos[0])+"a"
        if lastCharacterPosition[0] < pos[0]:
            command += str(pos[0]-lastCharacterPosition[0])+"d"
        if lastCharacterPosition[1] > pos[1]:
            command += str(lastCharacterPosition[1]-pos[1])+"w"
        if lastCharacterPosition[1] < pos[1]:
            command += str(pos[1]-lastCharacterPosition[1])+"s"

        if not foundSomething:
            command += "100."
        command += "opx$=ww$=aa$=ss$=dd"
        command += "opx$=ss$=aa$=ww$=dd"
        command += "opx$=ww$=dd$=ss$=aa"
        command += "opx$=ss$=dd$=ww$=aa"

        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

class HiveMind(Item):
    type = "HiveMind"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        self.territory = []
        self.paths = {}
        super().__init__(src.canvas.displayChars.floor_node,xPosition,yPosition,creator=creator,name="command bloom")
        self.createdAt = 0
        self.walkable = True
        self.bolted = True
        self.lastMoldClear = 0
        self.charges = 0
        self.toCheck = []
        self.cluttered = []
        self.blocked = []
        self.needSick = []
        self.needCoal = []
        self.lastBlocked = (7,7)
        self.lastCluttered = (7,7)
        self.lastExpansion = None
        self.colonizeIndex = 0

        self.faction = ""
        for i in range(0,5):
            char = random.choice("abcdefghijklmopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.faction += char

        self.attributesToStore.extend([
               "lastMoldClear","charges","lastExpansion","createdAt","faction"])

    def apply(self,character):
        if not self.xPosition:
            character.addMessage("this needs to be placed to be used")
            return
        command = None
        done = False
        selfDestroy = False

        if not ((self.xPosition%15,self.yPosition%15) == (7,7)):
            selfDestroy = True

        # get the path from the creature
        path = []
        pos = None
        while "PATHx" in character.registers:
            if not character.registers["PATHx"]:
                del character.registers["PATHx"]
                del character.registers["PATHy"]
                del character.registers["CLUTTERED"]
                del character.registers["BLOCKED"]
                del character.registers["NUM SICK"]
                del character.registers["NUM COAL"]
                break

            pos = (character.registers["PATHx"].pop(),character.registers["PATHy"].pop())

            if character.registers["CLUTTERED"].pop():
                if not pos in self.cluttered:
                    self.cluttered.append(pos)
            if character.registers["BLOCKED"].pop():
                if not pos in self.blocked:
                    self.blocked.append(pos)
            if character.registers["NUM SICK"].pop() < 4:
                if not pos in self.needSick:
                    self.needSick.append(pos)
            if character.registers["NUM COAL"].pop() < 4:
                if not pos in self.needCoal:
                    self.needCoal.append(pos)

            path.append(pos)
            if not pos in self.territory:
                self.territory.append(pos)
                self.toCheck.append(pos)
                self.lastExpansion = src.gamestate.gamestate.tick
        if pos:
            self.paths[pos] = path

        if not self.bolted:
            self.bolted = True
            self.paths = {(self.xPosition//15,self.yPosition//15):[]}
            self.lastExpansion = None
            if not (self.xPosition//15,self.yPosition//15) in self.territory:
                self.territory.append((self.xPosition//15,self.yPosition//15))

        broughtBloom = False
        for item in character.inventory[:]:
            if item.type == "CommandBloom":
                self.charges += 1
                character.inventory.remove(item)
                broughtBloom = True
            if item.type == "HiveMind":
                self.charges += item.charges
                character.inventory.remove(item)

        if character.inventory and character.inventory[-1].type == "Scrap":
            character.inventory.pop()
            character.inventory.append(Coal(creator=self))

        numItems = 0
        for item in reversed(character.inventory):
            if not item.walkable and item.type in ("SickBloom","Bloom","Coal","CommandBloom","Corpse"):
                break

        if self.lastExpansion == None:
            self.lastExpansion = src.gamestate.gamestate.tick
        selfReplace = False
        if (src.gamestate.gamestate.tick - self.lastExpansion) > len(self.territory)*1000:
            if (self.xPosition//15 == 7 and self.yPosition//15 == 7):
                self.lastExpansion = None
            else:
                selfReplace = True

        if selfReplace:
            new = CommandBloom(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            new.faction = self.faction

            directions = []
            if self.xPosition//15 > 7:
                directions.append("a")
            if self.yPosition//15 > 7:
                directions.append("w")
            if self.xPosition//15 < 7:
                directions.append("d")
            if self.yPosition//15 < 7:
                directions.append("s")
            direction = random.choice(directions)
            new.masterCommand = "13"+direction+"9kkj"

            character.inventory.append(new)

            self.bolted = False
            command = "kilwwj.13"+direction+"lj"

        elif hasattr(character,"phase") and character.phase == 1 and character.inventory and character.inventory[-1].type == "Coal":
            command = "l20j"
        elif hasattr(character,"phase") and character.phase == 2 and character.inventory and character.inventory[-1].type == "SickBloom":
            command = "ljj"
        elif isinstance(character, src.characters.Exploder):

            if self.territory:
                command = ""

                if self.blocked:
                    target = self.blocked.pop()
                    self.lastBlocked = target
                    if not target in self.toCheck:
                        self.toCheck.append(target)
                elif random.randint(1,2) == 1:
                    target = self.lastBlocked
                else:
                    target = random.choice(self.territory)

                (movementCommand,lastNode) = self.calculateMovementUsingPaths(target)
                if movementCommand:
                    command += movementCommand
               
                command += 13*(random.choice(["w","a","s","d"])+"k")+"kkj"
            else:
                command = random.choice(["W","A","S","D"])

        elif src.gamestate.gamestate.tick-self.lastMoldClear > 1000: # clear tile from mold
            command = 6*"wjjkkk"+"opx$=ss"+ 6*"sjjkkk"+"opx$=ww"+6*"ajjkkk"+"opx$=dd"+ 6*"djjkkk"+"opx$=aaj"
            self.lastMoldClear = src.gamestate.gamestate.tick
            done = True
        elif not self.charges and self.territory: # send creature somewhere
            command = ""

            supplyRun = False
            if character.inventory and self.needCoal and character.inventory[-1].type == "Coal":
                target = self.needCoal.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
                supplyRun = True
            elif character.inventory and self.needSick and character.inventory[-1].type == "SickBloom":
                target = self.needSick.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
                supplyRun = True
            elif self.cluttered:
                target = self.cluttered.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
                self.lastCluttered = target
                supplyRun = True
            elif random.randint(1,2) == 1:
                target = self.lastCluttered
            else:
                target = random.choice(self.territory)

            (movementCommand,lastNode) = self.calculateMovementUsingPaths(target)
            if movementCommand:
                command += movementCommand

            if command == "":
                command = random.choice(["W","A","S","D"])
                
            choice = random.randint(1,2)
            if choice == 1 or supplyRun:
                command += "kkj"
            else:
                extraCommand = ""
                for i in range(0,2):
                    direction = random.choice(["w","a","s","d"])
                    extraCommand += 13*(direction+"k")

                command += "kk"+20*extraCommand
                
        elif self.territory and (len(self.territory) < 10 or (broughtBloom and random.randint(0,1) == 1)): # expand the territory
            command = ""
            anchor = random.choice(self.territory)

            if len(self.territory) < 10:
                targetPos = random.choice([self.territory[0],[7,7]])
                while targetPos in self.territory:
                    targetPos = [random.randint(1,12),random.randint(1,12)]
            elif random.randint(1,2) and not ((self.xPosition//15,self.yPosition//15) == (7,7)):
                targetPos = [7,7]
                anchor = (self.xPosition//15,self.yPosition//15)
            else:
                length = 1
                pos = [7,7]
                index = 0
                while length < 13:
                    if length%2 == 1:
                        for i in range(0,length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[1] -= 1
                        for i in range(0,length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[0] += 1
                    else:
                        for i in range(0,length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[1] += 1
                        for i in range(0,length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[0] -= 1
                    length += 1
                for i in range(0,length-1):
                    if index == self.colonizeIndex:
                        break
                    index += 1
                    pos[1] -= 1

                self.colonizeIndex += 1
                if self.colonizeIndex == 169:
                    self.colonizeIndex = 0
                targetPos = pos

            if (self.xPosition//15,self.yPosition//15) == (7,7):
                anchor = (7,7)

            if not anchor in self.territory or not anchor in self.paths:
                anchor = (self.xPosition//15,self.yPosition//15)

                if not anchor in self.territory or not anchor in self.paths:
                    return

            character.addMessage(str(anchor)+" -> "+str(targetPos))

            neighbourPos = targetPos[:]
            while not (tuple(neighbourPos) in self.territory and tuple(neighbourPos) in self.paths):
                index = random.randint(0,1)
                targetPos = neighbourPos[:]
                if neighbourPos[index]-anchor[index] > 0:
                    neighbourPos[index] -= 1
                elif neighbourPos[index]-anchor[index] < 0:
                    neighbourPos[index] += 1
            character.addMessage("%s => %s"%(neighbourPos,targetPos))

            (movementCommand,lastNode) = self.calculateMovementUsingPaths(tuple(neighbourPos))
            if movementCommand:
                command += movementCommand

            new = CommandBloom(creator=self)
            self.charges -= 1
            new.faction = self.faction

            character.inventory.insert(0,new)
            character.registers["PATHx"] = []
            character.registers["PATHy"] = []
            character.registers["NUM COAL"] = []
            character.registers["NUM SICK"] = []
            character.registers["BLOCKED"] = []
            character.registers["CLUTTERED"] = []
            if targetPos[0] > neighbourPos[0]:
                command += 13*"dk"
                new.masterCommand = 13*"a"+"9kj"
            if targetPos[0] < neighbourPos[0]:
                command += 13*"ak"
                new.masterCommand = 13*"d"+"9kj"
            if targetPos[1] > neighbourPos[1]:
                command += 13*"sk"
                new.masterCommand = 13*"w"+"9kj"
            if targetPos[1] < neighbourPos[1]:
                command += 13*"wk"
                new.masterCommand = 13*"s"+"9kj"
            command += "9kjjjilj.j"
            
            if self.charges > 10:
                new2 = CommandBloom(creator=self)
                new2.masterCommand = new.masterCommand
                new2.faction = self.faction
                character.inventory.append(new2)
                self.charges -= 1
            character.addMessage(command)
        elif ((not broughtBloom and self.charges < 20) or random.randint(0,1) == 1) and self.territory: # move the character somewhere to help/supply
            command = ""

            if character.inventory and self.needCoal and character.inventory[-1].type == "Coal":
                target = self.needCoal.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
            elif character.inventory and self.needSick and character.inventory[-1].type == "SickBloom":
                target = self.needSick.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
            elif self.cluttered:
                target = self.cluttered.pop()
                if not target in self.toCheck:
                    self.toCheck.append(target)
                self.lastCluttered = target
            elif random.randint(1,2) == 1:
                target = self.lastCluttered
            else:
                target = random.choice(self.territory)

            (movementCommand,lastNode) = self.calculateMovementUsingPaths(target)
            command += movementCommand
            
            if command == "":
                command = random.choice(["W","A","S","D"])
            command += "kkj"
        elif self.territory: 
            command = self.doHealthCheckLazy(character)

        else: # stand around, look confused
            command = "wwaassdd100.j"
            
        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        if selfDestroy:
            new = FireCrystals(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            self.container.removeItem(self)
            direction = random.choice(["w","a","s","d"])
            reverseDirection = {"a":"d","w":"s","d":"a","s":"w"}
            command = "j"+3*direction+"40."+3*reverseDirection[direction]+"KaKwKsKd"
            for i in range(1,10):
                direction = random.choice(["w","a","s","d"])
                command += direction+"k"

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def doHealthCheckLazy(self,character):
        if not self.toCheck:
            self.toCheck = self.territory[:]

        target = (self.xPosition//15,self.yPosition//15)
        while self.toCheck and (target == (self.xPosition//15,self.yPosition//15) or not target in self.paths):
            target = self.toCheck.pop()

        if target == (self.xPosition//15,self.yPosition//15):
            command = "wwaassdd100.j"
        else:
            command = self.doHealthCheck(character,target)
        return command

    def doHealthCheck(self,character,target):
        character.addMessage(target)
        (movementCommand,secondToLastNode) = self.calculateMovementUsingPaths(target)
        command = movementCommand

        new = CommandBloom(creator=self)
        character.inventory.insert(0,new)
        self.charges -= 1
        command += "9kjjjilj.lj"
        new.faction = self.faction

        direction = ""
        if not secondToLastNode:
            command = random.choice(["A","W","S","D"])
        else:
            if target[1] == secondToLastNode[1]:
                if target[0] == secondToLastNode[0]-1:
                    direction = "d"
                if target[0] == secondToLastNode[0]+1:
                    direction = "a"
            elif target[0] == secondToLastNode[0]:
                if target[1] == secondToLastNode[1]-1:
                    direction = "s"
                if target[1] == secondToLastNode[1]+1:
                    direction = "w"

        character.addMessage(command)
        new.masterCommand = 13*direction+"9kj"
        return command

    def calculateMovementUsingPaths(self,target):
        if not target in self.paths:
            return ("",None)

        command = ""
        path = self.paths[target]

        lastNode = (self.xPosition//15,self.yPosition//15)
        secondToLastNode = None
        targetNodeDone = False
        for node in path+[target]:
            if (node[0]-lastNode[0] > 0):
                command += str(13*(node[0]-lastNode[0]))+"d"
            if (lastNode[0]-node[0] > 0):
                command += str(13*(lastNode[0]-node[0]))+"a"
            if (node[1]-lastNode[1] > 0):
                command += str(13*(node[1]-lastNode[1]))+"s"
            if (lastNode[1]-node[1] > 0):
                command += str(13*(lastNode[1]-node[1]))+"w"
            secondToLastNode = lastNode
            lastNode = node
            if targetNodeDone:
                break
            if node == target:
                targetNodeDone = True

        return (command,secondToLastNode)

    def configure(self,character):
        self.charges += 1

    def getLongInfo(self):
        text = """
item: 

description:

charges: %s
createdAt: %s
territory: %s
len(territory): %s
lastMoldClear: %s
blocked: %s
lastBlocked: %s
lastCluttered: %s
lastExpansion: %s
cluttered: %s
needCoal: %s
needSick: %s
len(needSick): %s
toCheck: %s
len(toCheck): %s
colonizeIndex: %s
faction: %s
paths: 
"""%(self.charges,self.createdAt,self.territory,len(self.territory),self.lastMoldClear,self.blocked,self.lastBlocked,self.lastCluttered,self.lastExpansion,self.cluttered,self.needCoal,self.needSick,len(self.needSick),self.toCheck,len(self.toCheck),self.colonizeIndex,self.faction)

        for path,value in self.paths.items():
            text += " * %s - %s\n"%(path,value)
        return text

    def getState(self):
        state = super().getState()
        state["paths"] = []
        for (key,value) in self.paths.items():
            step = {}
            step["key"] = key
            step["value"] = value
            state["paths"].append(step)
        state["territory"] = self.territory

        state["toCheck"] = self.toCheck
        state["cluttered"] = self.cluttered
        state["blocked"] = self.blocked
        state["needSick"] = self.needSick
        state["needCoal"] = self.needCoal
        state["lastCluttered"] = self.lastCluttered
        state["lastBlocked"] = self.lastBlocked

        return state

    def setState(self,state):
        super().setState(state)
        if "paths" in state:
            self.paths = {}
            for path in state["paths"]:
                self.paths[tuple(path["key"])] = []
                for value in path["value"]:
                    self.paths[tuple(path["key"])].append(tuple(value))
        if "territory" in state:
            self.territory = []
            for item in state["territory"]:
                self.territory.append(tuple(item))
        if "toCheck" in state:
            self.toCheck = []
            for item in state["toCheck"]:
                self.toCheck.append(tuple(item))
        if "cluttered" in state:
            self.cluttered = []
            for item in state["cluttered"]:
                self.cluttered.append(tuple(item))
        if "blocked" in state:
            self.blocked = []
            for item in state["blocked"]:
                self.blocked.append(tuple(item))
        if "needSick" in state:
            self.needSick = []
            for item in state["needSick"]:
                self.needSick.append(tuple(item))
        if "needCoal" in state:
            self.needCoal = []
            for item in state["needCoal"]:
                self.needCoal.append(tuple(item))
        if "lastCluttered" in state:
            self.lastCluttered = tuple(state["lastCluttered"])
        if "lastBlocked" in state:
            self.lastBlocked = tuple(state["lastBlocked"])

class CommandBloom(Item):
    type = "CommandBloom"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.commandBloom,xPosition,yPosition,creator=creator,name="command bloom")
        self.walkable = True
        self.bolted = True
        self.charges = 0
        self.numCoal = 0
        self.numSick = 0
        self.numCommandBlooms = 0
        self.lastFeeding = 0
        self.masterCommand = None
        self.expectedNext = 0
        self.blocked = False
        self.cluttered = False
        self.lastExplosion = 0
        
        self.faction = ""
        for i in range(0,5):
            char = random.choice("abcdefghijklmopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.faction += char

        self.attributesToStore.extend([
               "charges","numCoal","numSick","lastFeeding","faction","numCommandBlooms","masterCommand","expectedNext","blocked","cluttered","lastExplosion"])

    def apply(self,character):
        selfDestroy = False

        if not hasattr(self,"terrain") or not self.terrain:
            if not self.room:
                return
            selfDestroy = True
        if not self.xPosition:
            return

        items = self.container.getItemByPosition((self.xPosition-self.xPosition%15+7,self.yPosition-self.yPosition%15+7,self.zPosition))
        centralBloom = None
        if items and (items[0].type == "CommandBloom" or items[-1].type == "CommandBloom"):
            centralBloom = items[0]

        if len(self.container.getItemByPosition((self.xPosition,self.yPosition,self.zPosition))) > 1:
            selfDestroy = True

        if self.xPosition%15 == 1 and self.yPosition%15 == 7:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6d9kj"
        elif self.xPosition%15 == 13 and self.yPosition%15 == 7:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6a9kj"
        elif self.xPosition%15 == 7 and self.yPosition%15 == 13:
            if not centralBloom or self. masterCommand:
                selfDestroy = True
            command = "6w9kj"
        elif self.xPosition%15 == 7 and self.yPosition%15 == 1:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6s9kj"
        elif self.xPosition%15 == 7 and self.yPosition%15 == 7:
            command = None

            removeItems = []
            index = 0
            for item in character.inventory:
                if item.type == "Bloom":
                    removeItems.append(item)
                    self.charges += 1
                elif self.numSick < 5 and item.type == "SickBloom":
                    removeItems.append(item)
                    self.numSick += 1
                elif self.numCoal < 5 and item.type == "Coal":
                    removeItems.append(item)
                    self.numCoal += 1
                elif item.type == "HiveMind":
                    while self.charges and character.satiation < 900:
                        character.satiation += 100
                        self.charges -= 1

                    if self.xPosition//15 == 7 or self.yPosition//15 == 7: # place hive mind
                        self.bolted = False
                        command = "kil"+index*"s"+"jj"
                    elif self.masterCommand: # follow network
                        command = self.masterCommand
                    else: # wait for hive mind to develop
                        command = "1000."

                elif item.type == "CommandBloom":
                    if "PATHx" in character.registers and len(character.registers["PATHx"]) > 10 and random.randint(1,10) == 1:
                        numIncluded = 0
                        for i in range(1,len(character.registers["PATHx"])):
                            if character.registers["PATHx"][i] == self.xPosition//15 and character.registers["PATHy"][i] == self.yPosition//15:
                                numIncluded += 1
                                if numIncluded > 2:
                                    break
                        if numIncluded > 2:
                            self.masterCommand = None
                    if self.masterCommand:
                        command = self.masterCommand
                        if "PATHx" in character.registers:
                            character.registers["PATHx"].append(self.xPosition//15)
                            character.registers["PATHy"].append(self.yPosition//15)
                            character.registers["NUM COAL"].append(self.numCoal)
                            character.registers["NUM SICK"].append(self.numSick)
                            character.registers["BLOCKED"].append(self.blocked)
                            character.registers["CLUTTERED"].append(self.cluttered)
                    else:
                        removeItems.append(item)
                        self.numCommandBlooms += 1
                        command = "j"

                    if self.numCommandBlooms > 2:
                        new = HiveMind(creator=self)
                        new.createdAt = src.gamestate.gamestate.tick
                        new.xPosition = self.xPosition
                        new.yPosition = self.yPosition
                        new.territory.append((new.xPosition//15,new.yPosition//15))
                        new.paths[(new.xPosition//15,new.yPosition//15)] = []
                        new.faction = self.faction
                        self.container.removeItem(self)
                        self.container.addItems([new])
                index += 1
            for item in removeItems:
                character.inventory.remove(item)

            self.beganCluttered = True
            if len(character.inventory) > 7 and not command:
                if not self.numSick:
                    self.cluttered = True
                if self.masterCommand and self.numSick:
                    command = self.masterCommand
                    if self.numSick:
                        items = []
                        for i in range(0,2):
                            items.append(character.inventory.pop())
                        crawler = self.runCommandOnNewCrawler("j")
                        crawler.inventory.extend(items)
                else:
                    command = random.choice(["W","A","S","D"])

            if character.inventory and character.inventory[-1].type == "Coal" and hasattr(character,"phase") and character.phase == 1:
                if self.numSick > 4:
                    command = "wal20jsdj"
                    self.runCommandOnNewCrawler("j")

            if isinstance(character,src.characters.Exploder):
                if self.blocked:
                    foundItem = None
                    length = 1
                    pos = [self.xPosition,self.yPosition]
                    path = []
                    path.append((pos[0],pos[1]))
                    while length < 13:
                        if length%2 == 1:
                            for i in range(0,length):
                                pos[1] -= 1
                                path.append((pos[0],pos[1]))
                            for i in range(0,length):
                                pos[0] -= 1
                                path.append((pos[0],pos[1]))
                        else:
                            for i in range(0,length):
                                pos[1] += 1
                                path.append((pos[0],pos[1]))
                            for i in range(0,length):
                                pos[0] += 1
                                path.append((pos[0],pos[1]))
                        length += 1
                    for i in range(0,length-1):
                        pos[1] -= 1
                        path.append((pos[0],pos[1]))

                    targets = []
                    for pos in path:
                        items = self.container.getItemByPosition(pos)
                        if items and (items[0].bolted or not items[0].walkable) and not items[0].type in ("Scrap","Mold","Bush","Sprout","Sprout2","CommandBloom","PoisonBloom","Corpse",):
                            if items[0].xPosition%15 == 7 and items[0].yPosition%15 == 7:
                                continue
                            targets.append(items[0])

                    if targets:
                        if random.random() < 0.5:
                            foundItem = random.choice(targets)
                        else:
                            foundItem = targets[0]

                    if not foundItem:
                        directions = []
                        if not self.xPosition//15 == 0:
                            directions.append("a")
                            if self.xPosition//15 > 7:
                                directions.append("a")
                        if not self.xPosition//15 == 14:
                            directions.append("d")
                            if self.xPosition//15 < 7:
                                directions.append("d")
                        if not self.yPosition//15 == 0:
                            directions.append("w")
                            if self.yPosition//15 > 7:
                                directions.append("w")
                        if not self.yPosition//15 == 14:
                            directions.append("s")
                            if self.yPosition//15 > 7:
                                directions.append("s")
                        command = "13"+random.choice(directions)+"9kkj"
                        self.blocked = False
                    else:
                        command = ""
                        if foundItem.yPosition and self.yPosition > foundItem.yPosition:
                            command += str(self.yPosition-foundItem.yPosition)+"w"
                        if self.xPosition > foundItem.xPosition:
                            command += str(self.xPosition-foundItem.xPosition)+"a"
                        if self.yPosition < foundItem.yPosition:
                            command += str(foundItem.yPosition-self.yPosition)+"s"
                        if self.xPosition < foundItem.xPosition:
                            command += str(foundItem.xPosition-self.xPosition)+"d"
                        character.explode = True
                        command += "2000."
                else:
                    while self.charges and character.satiation < 900:
                        self.charges -= 1
                        character.satiation += 100

                    if self.masterCommand and random.randint(1,3) == 1:
                        command = self.masterCommand
                    else:
                        directions = []
                        if not self.xPosition//15 == 0:
                            directions.append("a")
                            if self.xPosition//15 > 7:
                                directions.append("a")
                        if not self.xPosition//15 == 14:
                            directions.append("d")
                            if self.xPosition//15 < 7:
                                directions.append("d")
                        if not self.yPosition//15 == 0:
                            directions.append("w")
                            if self.yPosition//15 > 7:
                                directions.append("w")
                        if not self.yPosition//15 == 14:
                            directions.append("s")
                            if self.yPosition//15 > 7:
                                directions.append("s")
                        command = "13"+random.choice(directions)+"9kkj"

            if not command and self.expectedNext and self.expectedNext > src.gamestate.gamestate.tick and not self.cluttered:
                if self.masterCommand and not random.randint(1,3) == 1:
                    command = self.masterCommand
                else:
                    command = 13*random.choice(["w","a","s","d"])+"9kkj"

            if self.charges < 5 and not command:
                command = ""
                length = 1
                pos = [self.xPosition,self.yPosition]
                path = []
                path.append((pos[0],pos[1]))

                bloomsSkipped = 0

                while length < 13:
                    if length%2 == 1:
                        for i in range(0,length):
                            pos[1] -= 1
                            path.append((pos[0],pos[1],0))
                        for i in range(0,length):
                            pos[0] -= 1
                            path.append((pos[0],pos[1],0))
                    else:
                        for i in range(0,length):
                            pos[1] += 1
                            path.append((pos[0],pos[1],0))
                        for i in range(0,length):
                            pos[0] += 1
                            path.append((pos[0],pos[1],0))
                    length += 1
                for i in range(0,length-1):
                    pos[1] -= 1
                    path.append((pos[0],pos[1],0))

                if character.satiation < 300 and self.charges:
                    if src.gamestate.gamestate.tick-self.lastFeeding < 60:
                        if self.charges < 15:
                            direction = random.choice(["w","a","s","d"])
                            command += 10*(13*direction+"j")
                        else:
                            command = ""
                            direction = random.choice(["w","a","s","d"])
                            command += 10*(13*direction+"opx$=aa$=ww$=ss$=ddwjajsjsjdjdjwjwjas")
                    else:
                        while character.satiation < 500 and self.charges:
                            character.satiation += 100
                            self.charges -= 1
                        self.lastFeeding = src.gamestate.gamestate.tick

                foundSomething = False
                lastCharacterPosition = path[0]
                explode = False
                lastpos = None
                count = 0
                for pos in path[1:]:
                    count += 1
                    items = self.container.getItemByPosition(pos)
                    if not items:
                        continue
                    elif items[0].type in ("CommandBloom",):
                        continue
                    elif items[0].type in ("Mold","Sprout2") and not (items[0].xPosition%15 == 7 or items[0].yPosition%15 == 7 or (items[0].xPosition%15,items[0].yPosition%15) in ((6,6),(6,8),(8,6),(8,8))):
                        continue
                    elif items[0].type in ("Sprout","SickBloom","Bloom","FireCrystals","Coal","Mold","Sprout2"):
                        if items[0].type == "Mold" and (pos[0]%15,pos[1]%15) in ((1,7),(7,1),(7,13),(13,7)):
                            continue
                        if items[0].type == "Sprout" and (pos[0]%15,pos[1]%15) in ((1,7),(7,1),(7,13),(13,7)):
                            continue
                        if not bloomsSkipped > 1 and (not pos[0]%15 == 7 and not pos[1]%15 == 7) and items[0].type == "Bloom" and self.masterCommand and self.charges > 5:
                            bloomsSkipped += 1
                            continue
                        if not bloomsSkipped > 1 and (not pos[0]%15 == 7 and not pos[1]%15 == 7) and items[0].type == "SickBloom" and self.masterCommand and self.numSick > 4:
                            bloomsSkipped += 1
                            continue
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1]-pos[1])+"w"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0]-pos[0])+"a"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1]-lastCharacterPosition[1])+"s"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0]-lastCharacterPosition[0])+"d"

                        foundSomething = True

                        if items[0].type in ("Coal"):
                            east = self.container.getItemByPosition((pos[0]+1,pos[1],0))
                            west = self.container.getItemByPosition((pos[0]-1,pos[1],0))
                            south = self.container.getItemByPosition((pos[0],pos[1]+1,0))
                            north = self.container.getItemByPosition((pos[0],pos[1]-1,0))
                            if ((west and west[0].type in ("EncrustedBush","PoisonBush","EncrustedPoisonBush")) or 
                                (east and east[0].type in ("EncrustedBush","PoisonBush","EncrustedPoisonBush")) or
                                (north and north[0].type in ("EncrustedBush","PoisonBush","EncrustedPoisonBush")) or
                                (south and south[0].type in ("EncrustedBush","PoisonBush","EncrustedPoisonBush")) or
                                (west and (not west[0].walkable or west[0].bolted) and not west[0].type in ("Scrap","PoisonBloom","Mold","Sprout","Sprout2","Bloom","SickBloom")) or
                                (east and (not east[0].walkable or east[0].bolted) and not east[0].type in ("Scrap","PoisonBloom","Mold","Sprout","Sprout2","Bloom","SickBloom")) or
                                (north and (not north[0].walkable or north[0].bolted) and not north[0].type in ("Scrap","PoisonBloom","Mold","Sprout","Sprout2","Bloom","SickBloom")) or
                                (south and (not south[0].walkable or south[0].bolted) and not south[0].type in ("Scrap","PoisonBloom","Mold","Sprout","Sprout2","Bloom","SickBloom"))):
                                if not self.numSick:
                                    self.lastExplosion = src.gamestate.gamestate.tick
                                    if hasattr(character,"phase") and character.phase == 1:
                                        if lastCharacterPosition[1] > pos[1]:
                                            command += "JwJwJwJwJw"
                                        if lastCharacterPosition[0] > pos[0]:
                                            command += "JaJaJaJaJa"
                                        if lastCharacterPosition[1] < pos[1]:
                                            command += "JsJsJsJsJs"
                                        if lastCharacterPosition[0] < pos[0]:
                                            command += "JdJdJdJdJd"
                                        command += "20j2000."
                                        explode = True
                                        break
                                    else:
                                        continue
                                else:
                                    newCommand = ""
                                    direction = (items[-1].xPosition-self.xPosition,items[-1].yPosition-self.yPosition)
                                    if (direction[1] < 0):
                                        newCommand += str(-direction[1])+"wJwJwJwJw"
                                    if (direction[0] < 0):
                                        newCommand += str(-direction[0])+"aJaJaJaJa"
                                    if (direction[1] > 0):
                                        newCommand += str(direction[1])+"sJsJsJsJs"
                                    if (direction[0] > 0):
                                        newCommand += str(direction[0])+"dJdJdJdJd"
                                    newCommand += "20j2000."
                                    self.runCommandOnNewCrawler(newCommand)
                                    break

                        lastCharacterPosition = pos

                        if items[0].type in ("Bloom","SickBloom","Coal"):
                            command += "k"
                        else:
                            command += "j"
                    elif items[0].type in ("Bush"):
                        foundSomething = True
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1]-pos[1])+"w"
                            lastDirection = "w"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0]-pos[0])+"a"
                            lastDirection = "a"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1]-lastCharacterPosition[1])+"s"
                            lastDirection = "s"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0]-lastCharacterPosition[0])+"d"
                            lastDirection = "d"
                        command += "j"
                        for i in range(0,11):
                            command += "J"+lastDirection
                        command += lastDirection
                        lastCharacterPosition = pos
                        break

                    elif (not items[0].walkable or items[0].bolted) and not items[0].type in ("Scrap","PoisonBloom","Corpse",):
                        self.blocked = True

                        if not self.numCoal or not self.numSick or src.gamestate.gamestate.tick-self.lastExplosion < 1000:
                            break

                        self.lastExplosion = src.gamestate.gamestate.tick

                        lowestIndex = None
                        for pos in ((items[0].xPosition-1,items[0].yPosition),(items[0].xPosition+1,items[0].yPosition),(items[0].xPosition,items[0].yPosition+1),(items[0].xPosition,items[0].yPosition+1)):
                            if not pos in path:
                                continue
                            if lowestIndex == None or path.index(pos) < lowestIndex:
                                lowestIndex = path.index(pos)
                        if lowestIndex == None:
                            break
                        targetPos = path[lowestIndex]

                        newCommand = ""
                        direction = (targetPos[0]-self.xPosition,targetPos[1]-self.yPosition)
                        if (direction[1] < 0):
                            newCommand += str(-direction[1])+"w"
                        if (direction[0] < 0):
                            newCommand += str(-direction[0])+"a"
                        if (direction[1] > 0):
                            newCommand += str(direction[1])+"s"
                        if (direction[0] > 0):
                            newCommand += str(direction[0])+"d"
                        newCommand += "l20j2000."
                        newChar = self.runCommandOnNewCrawler(newCommand)
                        newChar.inventory.append(Coal(creator=self))
                        self.numCoal -= 1
                        break
                    else:
                        foundSomething = True
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1]-pos[1])+"wk"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0]-pos[0])+"ak"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1]-lastCharacterPosition[1])+"sk"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0]-lastCharacterPosition[0])+"dk"
                        command += "k"
                        break

                if not explode:
                    if self.cluttered:
                        command += "opx$=aa$=ww$=ss$=dd"
                        direction = random.choice(["a","w","s","d"])
                        reverseDirection = {"w":"s","s":"w","a":"d","d":"a"}
                        command += 6*(direction+"k")+"opx$="+2*(reverseDirection[direction])

                    pos = (self.xPosition,self.yPosition)
                    if lastCharacterPosition[1] > pos[1]:
                        command += str(lastCharacterPosition[1]-pos[1])+"w"
                    if lastCharacterPosition[0] > pos[0]:
                        command += str(lastCharacterPosition[0]-pos[0])+"a"
                    if lastCharacterPosition[1] < pos[1]:
                        command += str(pos[1]-lastCharacterPosition[1])+"s"
                    if lastCharacterPosition[0] < pos[0]:
                        command += str(pos[0]-lastCharacterPosition[0])+"d"

                    command += "opx$=aa$=ww$=ss$=ddk"
                    if foundSomething:
                        command += "j"
                    if not foundSomething:
                        if character.satiation > 100:
                            command += str(min(character.satiation-30,random.randint(100,200)))+".j"
                        else:
                            command = random.choice(["W","A","S","D"])

                    self.expectedNext = src.gamestate.gamestate.tick+len(command)-25

                if count == 168:
                    self.cluttered = False

            elif not command:
                command = ""
                new = CommandBloom(creator=self)

                directions = []
                if not self.xPosition//15 == 0:
                    directions.append("a")
                    if self.xPosition//15 > 7:
                        directions.append("a")
                        if self.yPosition//15 == 7:
                            directions.append("a")
                            directions.append("a")
                            directions.append("a")
                if not self.xPosition//15 == 14:
                    directions.append("d")
                    if self.xPosition//15 < 7:
                        directions.append("d")
                        if self.xPosition//15 == 7:
                            directions.append("d")
                            directions.append("d")
                            directions.append("d")
                if not self.yPosition//15 == 0:
                    directions.append("w")
                    if self.yPosition//15 > 7:
                        directions.append("w")
                        if self.xPosition//15 == 7:
                            directions.append("w")
                            directions.append("w")
                            directions.append("w")
                if not self.yPosition//15 == 14:
                    directions.append("s")
                    if self.yPosition//15 > 7:
                        directions.append("s")
                        if self.yPosition//15 == 7:
                            directions.append("s")
                            directions.append("s")
                            directions.append("s")
                direction = random.choice(directions)
                reversedDirection = {"w":"s","s":"w","a":"d","d":"a"}
                command += 13*direction+"9kkjjjilj.j"
                new.masterCommand = 13*reversedDirection[direction]+"9kj"
                new.faction = self.faction


                walker = character
                walker.inventory.insert(0,new)
                walker.registers["SOURCEx"] = [self.xPosition//15]
                walker.registers["SOURCEy"] = [self.yPosition//15]
                walker.registers["PATHx"] = [self.xPosition//15]
                walker.registers["PATHy"] = [self.yPosition//15]
                walker.registers["NUM COAL"] = [self.numCoal]
                walker.registers["NUM SICK"] = [self.numSick]
                walker.registers["BLOCKED"] = [self.blocked]
                walker.registers["CLUTTERED"] = [self.beganCluttered]

                if self.numSick:
                    self.runCommandOnNewCrawler("j")

                if not "NaiveDropQuest" in walker.solvers:
                    walker.solvers.append("NaiveDropQuest")

                self.charges -= 1

                while walker.satiation < 900 and self.charges:
                    walker.satiation += 100
                    self.charges -= 1
        else:
            selfDestroy = True

        if selfDestroy:
            new = FireCrystals(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            self.container.removeItem(self)
            direction = random.choice(["w","a","s","d"])
            reverseDirection = {"a":"d","w":"s","d":"a","s":"w"}
            command = "j"+3*direction+"40."+3*reverseDirection[direction]+"KaKwKsKd"
            for i in range(1,10):
                direction = random.choice(["w","a","s","d"])
                command += direction+"k"

        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def runCommandOnNewCrawler(self,newCommand):
        if not self.numSick:
            return
        newCharacter = src.characters.Monster(creator=self)

        newCharacter.solvers = [
                  "NaiveActivateQuest",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "ActivateQuestMeta",
                  "NaivePickupQuest",
                  "PickupQuestMeta",
                  "NaiveMurderQuest",
                  "NaiveDropQuest",
                ]

        newCharacter.faction = self.faction
        newCharacter.satiation = 100
        convertedCommand = []
        for item in newCommand:
            convertedCommand.append((item,["norecord"]))
        newCharacter.macroState["commandKeyQueue"] = convertedCommand
        newCharacter.xPosition = self.xPosition
        newCharacter.yPosition = self.yPosition
        self.container.addCharacter(newCharacter,self.xPosition,self.yPosition)

        self.numSick -= 1

        return newCharacter

    def configure(self,character):
        self.charges += 1

    def getLongInfo(self):
        return """
item: Command Bloom

description:
runs commands on any creature activating this item.

charges: %s
numCoal: %s
numSick: %s
masterCommand: %s
numCommandBlooms: %s
blocked: %s
cluttered: %s
faction: %s
"""%(self.charges,self.numCoal,self.numSick,self.masterCommand,self.numCommandBlooms,self.blocked,self.cluttered,self.faction)

class RipInReality(Item):
    type = "RipInReality"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.ripInReality,xPosition,yPosition,creator=creator,name="rip in reality")
        self.target = None
        self.targetPos = None

        self.walkable = True
        self.bolted = True
        self.depth = 1
        self.lastUse = 0
        self.stable = False
        self.submenu = None
        self.killInventory = False
        self.storedItems = []

    def render(self):
        if self.stable:
            return "|#"
        else:
            return self.display

    def apply(self,character):
        self.container.removeCharacter(character)
        character.staggered += 1
        character.addMessage("the reality shift staggers you")

        if not self.stable and src.gamestate.gamestate.tick-self.lastUse > 100 * self.depth:
            self.target = None
            self.targetPos = None
        if not self.target:
            import random

            character.addMessage("you enter the rip in reality")

            if self.depth == 1:
                self.stable = True
                self.killInventory = True

                startPosition = (5,5)

                newRoom = src.rooms.StaticRoom(creator=self,depth=self.depth+1)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition,self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True
                backRip.killInventory = True

                newRoom.reconfigure(11,11)
                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItems([backRip])

                newRoom.addItems([src.items.itemMap["SaccrificialCircle"](5,4)])

                newRoom.addItems([src.items.itemMap["SparcRewardLock"](5,6)])

                newRoom.addCharacter(character,startPosition[0],startPosition[1])

                positions = [(2,2),(2,4),(2,6),(2,8),(8,2),(8,4),(8,6),(8,8),(4,2),(6,2),(4,8),(6,8)]

                for position in positions:
                    if random.randint(1,2) == 1:
                        rip = RipInReality(creator=self)
                        rip.xPosition = position[0]
                        rip.yPosition = position[1]
                        rip.depth = 2
                        newRoom.addItems([rip])
                    else:
                        plug = SparkPlug(creator=self)
                        plug.xPosition = position[0]
                        plug.yPosition = position[1]
                        plug.strength = 2
                        newRoom.addItems([plug])

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 2:
                startPosition = (5,5)

                newRoom = src.rooms.StaticRoom(creator=self,depth=self.depth+1)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition,self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True

                newRoom.reconfigure(9,9)

                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItems([backRip])
                newRoom.addCharacter(character,startPosition[0],startPosition[1])

                numMice = random.randint(1,5)
                for i in range(0,numMice):
                    enemy = src.characters.Mouse()
                    enemy.frustration = 100000
                    enemy.aggro = 20
                    if i%2 == 1:
                        enemy.runCommandString("ope$=aa$=dd$=ss$=wwmm30.m100.")
                    newRoom.addCharacter(enemy,random.randint(1,8),random.randint(1,8))

                rewardItem = None
                if random.randint(1,15) == 1:
                    rewardItem = src.items.itemMap["Rod"](random.randint(1,8),random.randint(1,8))
                elif random.randint(1,15) == 1:
                    rewardItem = src.items.itemMap["Vial"](random.randint(1,8),random.randint(1,8))
                    rewardItem.uses = 1
                elif random.randint(1,15) == 1:
                    rewardItem = src.items.itemMap["Armor"](random.randint(1,8),random.randint(1,8))
                if rewardItem:
                    newRoom.addItems([rewardItem])

                self.target = newRoom
                self.targetPos = startPosition

            elif random.randint(1,5) == 5 and 1==0:
                sizeX = random.randint(4,13)
                sizeY = random.randint(4,13)

                startPosition = (random.randint(1,sizeX-2),random.randint(1,sizeY-2))

                # generate solvable captcha room
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition,self.yPosition)
                backRip.xPosition = random.randint(1,sizeX-2)
                backRip.yPosition = random.randint(1,sizeY-2)
                backRip.stable = True

                newRoom.reconfigure(sizeX,sizeY)
                newRoom = src.rooms.StaticRoom(creator=self,depth=self.depth+1)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([backRip])
                newRoom.addCharacter(character,startPosition[0],startPosition[1])

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 10:
                sizeX = 5
                sizeY = 5
                startPosition = (1,1)
                crystal = StaticCrystal(creator=self)
                crystal.xPosition = 3
                crystal.yPosition = 3

                newRoom.reconfigure(sizeX,sizeY)
                newRoom = src.rooms.StaticRoom(creator=self,depth=self.depth+1)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([crystal])
                newRoom.addCharacter(character,1,1)
            else:
                sizeX = random.randint(5,13)
                sizeY = random.randint(5,13)

                startPosition = (random.randint(1,sizeX-2),random.randint(1,sizeY-2))

                # generate maybe solvable riddle room
                newRoom = src.rooms.StaticRoom(creator=self,depth=self.depth+1)
                #newRoom.reconfigure(self,sizeX=3,sizeY=3,items=[],bio=False)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition,self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True
                backRip.depth = self.depth + 1

                newRoom.reconfigure(sizeX,sizeY)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([backRip])

                for i in range(1,self.depth):
                    wall = StaticMover(creator=self)
                    newPos = (random.randint(0,sizeX-1),random.randint(0,sizeY-1))
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    wall.xPosition = newPos[0]
                    wall.yPosition = newPos[1]
                    wall.energy = self.depth*2
                    newRoom.addItems([wall])

                while not random.randint(1,3) == 3:
                    if random.randint(1,2)==1:
                        if random.randint(1,2)==1:
                            spark = StaticSpark(creator=self)
                            spark.strength = self.depth
                            spark.name = "static spark %s"%(spark.strength)
                        else:
                            spark = SparkPlug(creator=self)
                            spark.strength = self.depth+1
                            spark.name = "spark plug %s"%(spark.strength)
                    else:
                        spark = RipInReality(creator=self)
                        spark.depth = self.depth + 1
                        spark.name = "rip in reality %s"%(spark.depth)

                    sparkPos = None
                    counter = 0
                    while not sparkPos or sparkPos == startPosition or newRoom.getItemByPosition(sparkPos):
                        sparkPos = (random.randint(1,sizeX-2),random.randint(1,sizeY-2))
                    spark.xPosition = sparkPos[0]
                    spark.yPosition = sparkPos[1]
                    newRoom.addItems([spark])

                    while not random.randint(1,self.depth+1) == 1:
                        wall = StaticWall(creator=self)
                        wall.strength = self.depth+2
                        newPos = (random.randint(0,sizeX-1),random.randint(0,sizeY-1))
                        if newPos == startPosition or newRoom.getItemByPosition(newPos):
                            continue
                        wall.xPosition = newPos[0]
                        wall.yPosition = newPos[1]
                        newRoom.addItems([wall])
                

                newRoom.addCharacter(character,startPosition[0],startPosition[1])


                self.target = newRoom
                self.targetPos = startPosition

                while not random.randint(1,self.depth+5) == 1:
                    wall = StaticWall(creator=self)
                    wall.strength = self.depth+2
                    newPos = (random.randint(0,sizeX-1),random.randint(0,sizeY-1))
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    wall.xPosition = newPos[0]
                    wall.yPosition = newPos[1]
                    newRoom.addItems([wall])
        else:
            self.target.addCharacter(character,self.targetPos[0],self.targetPos[1])

        if self.killInventory:
            character.inventory = []

        self.lastUse = src.gamestate.gamestate.tick

    def configure(self,character):
        options = [("destabilize","destabilize"),("stablize","stablize")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        staticSpark = None
        for item in self.character.inventory:
            if isinstance(item,StaticSpark) and item.strength >= self.depth:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            self.character.addMessage("no suitable static spark")
            return

        self.character.inventory.remove(staticSpark)

        if self.submenue.selection == "destabilize":
            if self.stable:
                self.stable = False
                self.character.addMessage("Rip in reality not stable anymore")
            else:
                self.target = None
                self.targetPos = None
                self.character.addMessage("Rip in reality destabilized")
        elif self.submenue.selection == "stablize":
            self.stable = True
            self.character.addMessage("Rip in reality was stabilized")
        self.submenue = None

    def getLongInfo(self):
        return """
item: RipInReality

description:
You can enter it

depth:
%s

stable:
%s

%s
%s
"""%(self.depth,self.stable,self.target,self.targetPos)


class StaticCrystal(Item):
    type = "StaticCrystal"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.staticCrystal,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = False

    def apply(self,character):
        self.character.addMessage("you break reality")
        1/0

class StaticShard(Item):
    type = "StaticShard"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.staticCrystal,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = False

    def apply(self,character):
        new = RipInReality(creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        new.stable = True
        self.container.addItems([new])
        self.container.removeItem(self)

class SparkPlug(Item):
    type = "SparkPlug"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sparkPlug,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = True
        self.bolted = True
        self.strength = 1

    def apply(self,character):
        staticSpark = None
        for item in character.inventory:
            if isinstance(item,StaticSpark) and item.strength >= self.strength-1:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        newItem = RipInReality(creator=self)
        newItem.xPosition = self.xPosition
        newItem.yPosition = self.yPosition
        newItem.depth = self.strength
        self.container.addItems([newItem])
        self.container.removeItem(self)

class StaticSpark(Item):
    type = "StaticSpark"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.staticSpark,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = True
        self.bolted = False
        self.strength = 1

    def apply(self,character):
        character.addSatiation(self.strength*50)
        character.addMessage("you gained "+str(self.strength*50)+" satiation from consuming the spark")
        self.destroy(generateSrcap=False)
    
class StaticWall(Item):
    type = "StaticWall"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.forceField,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = True
        self.strength = 1

    def apply(self,character):
        staticSpark = None
        for item in character.inventory:
            if isinstance(item,StaticSpark) and item.strength >= self.strength:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        self.container.removeItem(self)
        character.addMessage("you use a static spark on the static wall and it dissapears")

class StaticMover(Item):
    type = "StaticMover"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.forceField2,xPosition,yPosition,creator=creator,name="static spark")

        self.walkable = False
        self.bolted = True
        self.strength = 1
        self.energy = 1

    def apply(self,character):
        staticSpark = None
        for item in character.inventory:
            if isinstance(item,StaticSpark) and item.strength >= self.strength:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        self.container.removeItem(self)
        character.addMessage("you use a static spark on the static wall and it dissapears")


    def getLongInfo(self):
        return """
item: StaticMover

description:
Moves towards you and leeches your energy

energy:
%s

"""%(self.energy)

class HealingStation(Item):
    type = "HealingStation"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.healingStation,xPosition,yPosition,creator=creator,name="healingstation")

        self.walkable = False
        self.bolted = True
        self.charges = 0

    def apply(self,character):
        options = [("heal","heal me"),("vial","fill vial")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "heal":
            self.heal(self.character)
        if self.submenue.selection == "vial":
            self.fill(self.character)

    def heal(self,character):

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        character.addMessage("the machine heals you")
        character.health = 100
        self.charges -= 1

    def fill(self,character):

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        for item in character.inventory:
            if not isinstance(item,src.items.Vial):
                continue
            if self.charges > item.maxUses-item.uses:
                self.charges -= item.maxUses-item.uses
                item.uses = item.maxUses
                character.addMessage("you fill your vial with the healing")
                return
            else:
                item.uses += self.charges
                self.charges = 0
                character.addMessage("you drain the healing into your vial")
                return

        character.addMessage("you have no vial in your inventory")

    def getLongInfo(self):
        return """
item: HealingStation

description:
heals you

charges:
%s

"""%(self.charges)

class SunScreen(Item):
    type = "SunScreen"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.sunScreen,xPosition,yPosition,creator=creator,name="sunscreen")

        self.walkable = True
        self.bolted = False

    def apply(self,character):
        character.addMessage("you apply the sunscreen and gain +1 heat resistance") 
        character.heatResistance += 1
        self.destroy()

    def getLongInfo(self):
        return """
item: SunScreen

description:
protects from solar radiation

"""

class WaterPump(Item):
    type = "WaterPump"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__("WP",xPosition,yPosition,creator=creator,name="water pump")

        self.walkable = False
        self.bolted = True
        self.rods = 0


    def apply(self,character):
        options = [("drink","drink"),("rod","add rod")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if not self.terrain:
            self.character.addMessage("the water condenser needs to be placed outside to work")
            return

        self.bolted = True

        if self.submenue.selection == "drink":
            if self.terrain.heatmap[self.xPosition//15][self.yPosition//15] > 4:
                self.character.addMessage("there is no water left")
                return

            amount = 100+self.rods*10
            self.character.addMessage("you drink from the water condenser. You gain %s satiation, but are poisoned"%(amount,)) 
            self.character.satiation += amount
            if self.character.satiation > 1000:
                self.character.satiation = 1000
            self.character.hurt(amount//100,reason="poisoned")

            self.terrain.heatmap[self.xPosition//15][self.yPosition//15] += 1

        if self.submenue.selection == "rod":
            for item in self.character.inventory:
                if isinstance(item,src.items.Rod):

                    self.character.addMessage("you insert a rod into the water condenser increasing its output")
                    self.rods += 1
                    self.character.inventory.remove(item)
                    return
            self.character.addMessage("you have no rods in your inventory")

    def getLongInfo(self):
        return """
item: Water condenser

description:
you can drink condensed water from it

"""

class WaterCondenser(Item):
    type = "WaterCondenser"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__("WW",xPosition,yPosition,creator=creator,name="water condenser")

        self.walkable = False
        self.bolted = True
        self.rods = 0
        try:
            self.lastUsage = src.gamestate.gamestate.tick
        except:
            self.lastUsage = 0

    def apply(self,character):
        options = [("drink","drink"),("rod","add rod")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if not self.terrain:
            self.character.addMessage("the water condenser needs to be placed outside to work")
            return

        self.bolted = True

        if self.submenue.selection == "drink":
            if self.terrain.heatmap[self.xPosition//15][self.yPosition//15] > 4:
                self.character.addMessage("there is no water left")
                return

            amount = (src.gamestate.gamestate.tick-self.lastUsage)//100*(self.rods+1+5)
            self.character.addMessage("you drink from the water condenser. You gain %s satiation, but are poisoned"%(amount,)) 
            self.character.satiation += amount
            if self.character.satiation > 1000:
                self.character.satiation = 1000
            self.character.hurt(amount//100+1,reason="poisoned")

            self.lastUsage = src.gamestate.gamestate.tick

        if self.submenue.selection == "rod":
            if self.rods > 9:
                self.character.addMessage("the water condenser cannot take more rods")
                return

            for item in self.character.inventory:
                if isinstance(item,src.items.Rod):

                    self.character.addMessage("you insert a rod into the water condenser increasing its output to %s per 100 ticks"%(self.rods+1+5,))
                    self.rods += 1
                    self.character.inventory.remove(item)
                    self.lastUsage = src.gamestate.gamestate.tick
                    return
            self.character.addMessage("you have no rods in your inventory")

    def getLongInfo(self):
        return """
item: Water condenser

description:
you can drink condensed water from it, but the water is poisoned

it generates %s satiation for every 100 ticks left alone

"""%(self.rods+1+5,)

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class ResourceTerminal(Item):
    type = "ResourceTerminal"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="ScrapTerminal",creator=None,noId=False):
        super().__init__("RT",xPosition,yPosition,name=name,creator=creator)

        self.balance = 0
        self.resource = "Scrap"
        self.attributesToStore.extend([
               "balance","resource"])

    def setResource(self,resource):
        self.resource = resource

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        options = [
                   ("showBalance","show balance"),
                   ("addResource","add %s"%(self.resource)),
                   ("getResource","get %s"%(self.resource)),
                   ("getTokens","get token"),
                   ("addTokens","add token"),
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character


    def apply2(self):
        if self.submenue.selection == "showBalance":
            self.character.addMessage("your balance is %s"%((self.balance,)))

        if self.submenue.selection == "addResource":
            toRemove = []
            for item in self.character.inventory:
                if isinstance(item,src.items.itemMap[self.resource]):
                    toRemove.append(item)

            self.character.addMessage("you add %s %s"%((len(toRemove),self.resource,)))
            for item in toRemove:
                self.character.inventory.remove(item)
            self.balance += len(toRemove)//2
            self.character.addMessage("your balance is now %s"%(self.balance,))
        if self.submenue.selection == "getTokens":
            self.character.inventory.append(src.items.Token(None,None,tokenType=self.resource+"Token",payload=self.balance))
            self.balance = 0
        if self.submenue.selection == "addTokens":
            for item in self.character.inventory:
                if isinstance(item,src.items.Token) and item.tokenType == self.resource+"Token":
                    self.balance += item.payload
                    self.character.inventory.remove(item)
            pass
        if self.submenue.selection == "getResource":

            numAdded = 0
            for i in range(len(self.character.inventory),10):
                if self.balance < 2:
                    self.character.addMessage("your balance is too low")
                    break

                numAdded += 1
                self.balance -= 2
                self.character.inventory.append(src.items.itemMap[self.resource]())

            self.character.addMessage("your balance is now %s"%(self.balance,))

    def getLongInfo(self):
        text = """
item: ResourceTerminal

description:
A resource Terminal. 
"""

'''
a dummy for an interface with the mech communication network
'''
class ItemCollector(Item):
    type = "ItemCollector"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="ItemCollector",creator=None,noId=False):
        super().__init__("ic",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.commands = {}
        self.attributesToStore.extend([
               "balance"])

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.terrain:
            character.addMessage("the item collector cannot be used within rooms")
            return

        if not (self.xPosition%15 == 7 and self.yPosition%15 == 7):
            character.addMessage("the item collector needs to be placed in the middle of a tile")
            return
        
        if not self.bolted:
            character.addMessage("the item collector digs into the ground and is now ready for use")
            self.bolted = True

        if isinstance(character,src.characters.Monster):
            character.die()
            return

        if len(character.inventory) > 9:
            character.addMessage("inventory full")
            self.runCommand("fullInventory",character)
            return

        command = ""
        length = 1
        pos = [self.xPosition,self.yPosition]
        path = []
        path.append((pos[0],pos[1]))
        for x in range(pos[0],pos[0]+7):
            path.append((x,pos[1]))
        for x in reversed(range(pos[0]-6,pos[0])):
            path.append((x,pos[1]))
        for y in range(pos[1],pos[1]+7):
            path.append((pos[0],y))
        for y in reversed(range(pos[1]-6,pos[1])):
            path.append((pos[0],y))
        while length < 13:
            if length%2 == 1:
                for i in range(0,length):
                    pos[1] -= 1
                    path.append((pos[0],pos[1]))
                for i in range(0,length):
                    pos[0] += 1
                    path.append((pos[0],pos[1]))
            else:
                for i in range(0,length):
                    pos[1] += 1
                    path.append((pos[0],pos[1]))
                for i in range(0,length):
                    pos[0] -= 1
                    path.append((pos[0],pos[1]))
            length += 1
        for i in range(0,length-1):
            pos[1] -= 1
            path.append((pos[0],pos[1]))

        character.addMessage(path[:5])

        lastCharacterPosition = path[0]
        foundItem = None
        lastPos = path[0]
        for pos in path[1:]:
            items = self.container.getItemByPosition((pos[0],pos[1],0))
            if not items or pos == path[0]:
                lastPos = pos
                continue
            foundItem = items[0]
            break

        if not foundItem:
            character.addMessage("no items found")
            self.runCommand("empty",character)
            return

        if foundItem:
            newCharacterPosition = [lastCharacterPosition[0],lastCharacterPosition[1]]
            if lastCharacterPosition[0] > pos[0]:
                numMoves = lastCharacterPosition[0]-pos[0]-1
                if numMoves > 0:
                    command += "a"*numMoves
                    newCharacterPosition[0] -= numMoves
            if lastCharacterPosition[0] < pos[0]:
                numMoves = pos[0]-lastCharacterPosition[0]-1
                if numMoves > 0:
                    command += "d"*numMoves
                    newCharacterPosition[0] += numMoves
            if lastCharacterPosition[1] > pos[1]:
                numMoves = lastCharacterPosition[1]-pos[1]-1
                if numMoves > 0:
                    command += "w"*numMoves
                    newCharacterPosition[1] -= numMoves
            if lastCharacterPosition[1] < pos[1]:
                numMoves = pos[1]-lastCharacterPosition[1]-1
                if numMoves > 0:
                    command += "s"*numMoves
                    newCharacterPosition[1] += numMoves
            lastCharacterPosition = newCharacterPosition

            newCharacterPosition = [lastCharacterPosition[0],lastCharacterPosition[1]]
            if lastCharacterPosition[0] < pos[0] and lastCharacterPosition[1] < pos[1]:
                command += "d"
                newCharacterPosition[0] += 1
            if lastCharacterPosition[0] > pos[0] and lastCharacterPosition[1] < pos[1]:
                command += "s"
                newCharacterPosition[1] += 1
            if lastCharacterPosition[0] < pos[0] and lastCharacterPosition[1] > pos[1]:
                command += "w"
                newCharacterPosition[1] -= 1
            if lastCharacterPosition[0] > pos[0] and lastCharacterPosition[1] > pos[1]:
                command += "a"
                newCharacterPosition[0] -= 1
            lastCharacterPosition = newCharacterPosition

            if lastCharacterPosition[0] < pos[0]:
                command += "Kd"
            if lastCharacterPosition[0] > pos[0]:
                command += "Ka"
            if lastCharacterPosition[1] < pos[1]:
                command += "Ks"
            if lastCharacterPosition[1] > pos[1]:
                command += "Kw"

        command += "opx$=ss$=ww$=dd$=aa"

        character.addMessage(command)
        convertedCommand = []
        for item in command:
            convertedCommand.append((item,["norecord"]))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("empty","no items left"))
            options.append(("fullInventory","inventory full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character):
        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getState(self):
        state = super().getState()
        state["commands"] = self.commands
        return state

    def setState(self,state):
        super().setState(state)
        if "commands" in state:
            self.commands = state["commands"]

    def getLongInfo(self):
        text = """
item: ItemCollector

description:
use it to collect items
"""


'''
'''
class SanitaryStation(Item):
    type = "SanitaryStation"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="SanitaryStation",creator=None,noId=False):
        super().__init__("SS",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False
        self.commands = {}
        self.healthThreshold = 10
        self.satiationThreshold = 100
        self.frustrationThreshold = 10000

        self.attributesToStore.extend([
               "commands","healthThreshold","satiationThreshold",
               ])

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if character.health < self.healthThreshold:
            character.addMessage("health needed")
            self.runCommand("healing",character)
            return
        if character.frustration > self.frustrationThreshold:
            character.addMessage("depressed")
            self.runCommand("depressed",character)
            return
        if character.satiation < self.satiationThreshold:
            character.addMessage("satiation needed")
            self.runCommand("hungry",character)
            return
        character.addMessage("nothing needed")

    def configure(self,character):
        options = [("addCommand","add command"),("changeSetting","change settings"),("showSettings","show settings")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("healing","need healing"))
            options.append(("hungry","need satiation"))
            options.append(("depressed","need depressed"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand
        if self.submenue.selection == "changeSetting":
            options = []
            options.append(("health","set health threshold"))
            options.append(("satiation","set satiation threshold"))
            options.append(("depressed","set depressed threshold"))
            self.submenue = src.interaction.SelectionMenu("Choose setting to set",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setSetting
            self.settingName = None
        if self.submenue.selection == "showSettings":
            self.submenue = src.interaction.TextMenu("health threshold: %s\nsatiation threshold: %s"%(self.healthThreshold,self.satiationThreshold,))
            self.character.macroState["submenue"] = self.submenue

    def setSetting(self):
        if not self.settingName:
            self.settingName = self.submenue.selection

            self.submenue = src.interaction.InputMenu("input the value")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setSetting
            return

        if self.settingName == "health":
            self.healthThreshold = int(self.submenue.text)
        if self.settingName == "satiation":
            self.satiationThreshold = int(self.submenue.text)
        if self.settingName == "depressed":
            self.frustrationThreshold = int(self.submenue.text)

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character=None):
    
        if character == None:
            character=self.character

        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getLongInfo(self):
        text = """
item: ItemCollector

description:
use it to collect items
"""
        return text

    def fetchSpecialRegisterInformation(self):
        result = super().fetchSpecialRegisterInformation()

        result["healthThreshold"] = self.healthThreshold
        result["satiationThreshold"] = self.satiationThreshold
        result["frustrationThreshold"] = self.frustrationThreshold
        
        return result

'''
'''
class GooFaucet(Item):
    type = "GooFaucet"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="GooFaucet",creator=None,noId=False):
        super().__init__("GF",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False
        self.commands = {}
        self.balance = 0
        self.character = None

        self.attributesToStore.extend([
               "balance","commands",
               ])

        self.objectsToStore.extend([
               "character",
               ])

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        options = [("drink","drink from the faucet"),("fillFlask","fill goo flask"),("addTokens","add goo tokens"),("showBalance","show balance")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "drink":
            if self.balance < 2:
                self.character.addMessage("balance too low")
                self.runCommand("ballanceTooLow")
                return
            self.character.satiation = 1000
            self.balance -= 2
        if self.submenue.selection == "fillFlask":
            filled = False
            fillAmount = 100
            for item in self.character.inventory:
                if isinstance(item,GooFlask) and not item.uses >= fillAmount:
                    fillAmount = fillAmount-item.uses
                    if fillAmount*2 > self.balance:
                        self.character.addMessage("balance too low")
                        self.runCommand("ballanceTooLow")
                        return
                    item.uses += fillAmount
                    filled = True
                    self.balance -= fillAmount*2
                    break
            if filled:
                self.character.addMessage("you fill the goo flask")
        if self.submenue.selection == "addTokens":
            pass
        if self.submenue.selection == "showBalance":
            self.character.addMessage("your balance is %s"%(self.balance,))

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            #options.append(("empty","no items left"))
            options.append(("fullInventory","inventory full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character=None):
        if character == None:
            character = self.character

        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getLongInfo(self):
        text = """
item: GooFaucet

description:
use it to collect items
"""

'''
'''
class PathingNode(Item):
    type = "PathingNode"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="PathingNode",creator=None,noId=False):
        super().__init__(";;",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.nodeName = ""

        self.attributesToStore.extend([
               "nodeName",
               ])

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        character.addMessage("This is the pathingnode: %s"%(self.nodeName,))
        self.bolted = True

    def configure(self,character):
        options = [("setName","set name")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("enter node name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName

    def setName(self):
        self.nodeName = self.submenue.text
        
    def getLongInfo(self):
        text = """
item: PathingNode

name:
%s

description:
the basis for semi smart pathing
"""%(self.nodeName,)

'''
'''
class CityBuilderOld(Item):
    type = "CityBuilder"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="PathingNode",creator=None,noId=False):
        super().__init__("CB",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

        self.plots = []
        self.plotCandidates = []

        self.tileMap = []
        for x in range(0,7):
            self.tileMap.append([])
            for y in range(0,7):
                self.tileMap[x].append({"display":"  "})
                if [x,y] == [6,6] or x==0 or y==0:
                    continue
                self.plotCandidates.append([x,y])

        import random
        #random.shuffle(self.plotCandidates)

        self.tileMap[6][6]["display"] = "CB"
        self.tileMap[6][6]["type"] = "RoomControl"

        self.attributesToStore.extend([
               "tileMap","plots","plotCandidates","jobs",
               ])

        self.jobs = []
        self.jobs.extend(["extend stockpiles","add plot"])
        self.jobs.append("add map")
        self.jobs.append("add StockpileMetaManager")
        self.jobs.append("add RoomBuilder")
        self.jobs.append("add pathingNodeRT")

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.jobs:
            return
        
        job = self.jobs.pop()
        if job == "extend stockpiles":
            plot = self.plots.pop()
            item = src.items.Map()

            toRoute = "5d10wawwd"
            fromRoute = "assd8s5a"
            x = 6
            y = 5
            if plot[0][1] == 6:
                toRoute = toRoute+"as11awa"
                fromRoute = "ds11dwd"+fromRoute
                x = 5
                y = 5

            while x < plot[0][0]:
                toRoute = toRoute + "ds11dwd"
                fromRoute = "as11awa"+fromRoute
                x += 1
            while x > plot[0][0]:
                toRoute = toRoute + "as11awa"
                fromRoute = "ds11dwd"+fromRoute
                x -= 1
            while y < plot[0][1]:
                toRoute = toRoute + "assd11s"
                fromRoute = "11wdwwa"+fromRoute
                y += 1
            while y > plot[0][1]:
                toRoute = toRoute + "11wdwwa"
                fromRoute = "assd11s"+fromRoute
                y -= 1



            item.routes["central stockpile"] = {}
            item.routes["central stockpile"][plot[1]] = list(toRoute)
            item.routes[plot[1]] = {}
            item.routes[plot[1]]["central stockpile"] = list(fromRoute)
            character.inventory.append(item)

            command = "3w5alsc4sjjksjsjsjj5d3s"
            character.runCommandString(command)
            return

        if job == "add plot":
            plot = self.plotCandidates.pop()
            item = src.items.PathingNode()
            item.nodeName = "plot"+str(plot)
            self.plots.append([plot,item.nodeName])
            character.inventory.append(item)
            #move to 5,5
            toCommand = "13wawwd"
            backCommand = "assd11s"
            x = 6
            y = 5
            if plot[1] == 6:
                toCommand = toCommand + "as11awa"
                backCommand = "ds11dwd"+backCommand
                x = 5
                y = 5
            while x < plot[0]:
                toCommand = toCommand + "ds11dwd"
                backCommand = "as11awa"+backCommand
                x += 1
            while x > plot[0]:
                toCommand = toCommand + "as11awa"
                backCommand = "ds11dwd"+backCommand
                x -= 1
            while y < plot[1]:
                toCommand = toCommand + "assd11s"
                backCommand = "11wdwwa"+backCommand
                y += 1
            while y > plot[1]:
                toCommand = toCommand + "11wdwwa"
                backCommand = "assd11s"+backCommand
                y -= 1

            #drop command
            command = toCommand+"l"+backCommand
            #move back into room
            character.runCommandString(command)
        if job == "add RoomBuilder":
            character.inventory.append(src.items.RoomBuilder())
            command = "aLsd"
            character.runCommandString(command)
        if job == "add pathingNodeRT":
            item = src.items.ResourceTerminal()
            item.setResource("PathingNode")
            character.inventory.append(item)
            command = "3w5aLw5d3s"
            character.runCommandString(command)
        if job == "add StockpileMetaManager":
            character.inventory.append(src.items.itemMap["StockpileMetaManager"]())
            item = src.items.PathingNode()
            item.nodeName = "central stockpile"
            character.inventory.append(item)

            command = "3w5alLs5d3s"
            character.runCommandString(command)
        if job == "add map":
            character.inventory.append(src.items.Sheet())
            command = "dsljssjwa"
            character.runCommandString(command)


    def configure(self,character):
        options = [("addJob","add job"),("setName","set name"),("showMap","show map")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addJob":
            options = [("add plot","add plot"),("extend stockpiles","extend stockpiles")]
            self.submenue = src.interaction.SelectionMenu("what you do you wand to add?",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.addJob
        if self.submenue.selection == "showMap":
            mapText = ""
            for x in range(0,7):
                mapText += "\n"
                for y in range(0,7):
                    mapText += self.tileMap[x][y]["display"]

            self.submenue = src.interaction.TextMenu(mapText)
            self.character.macroState["submenue"] = self.submenue
        if self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("enter node name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName
    
    def addJob(self):
        self.jobs.append(self.submenue.selection)

    def setName(self):
        self.nodeName = self.submenue.text
        
    def getLongInfo(self):
        text = """
item: PathingNode

name:
%s

description:
the basis for semi smart pathing
"""%(self.nodeName,)

class SuicideBooth(Item):
    type = "SuicideBooth"

    def __init__(self,xPosition=0,yPosition=0,name="SuicideBooth",creator=None,noId=False):
        super().__init__("SB",xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        character.addMessage("you die")
        character.die(reason="used suicide booth")

class SparcRewardLock(Item):
    type = "SparcRewardLock"

    def __init__(self,xPosition=0,yPosition=0,name="SaccrificialCircle",creator=None,noId=False):
        super().__init__("%°",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = True

    def apply(self,character):
        foundItem = None
        for item in character.inventory:
            if item.type == "StaticCrystal":
                foundItem = item
                break

        if not foundItem:
            character.addMessage("no static crystal in inventory - insert to claim reward")
            return
        
        character.inventory.append(foundItem)
        character.addMessage("well done")

class SaccrificialCircle(Item):
    type = "SaccrificialCircle"

    def __init__(self,xPosition=0,yPosition=0,name="SaccrificialCircle",creator=None,noId=False):
        super().__init__("&°",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = True
        self.level = 1
        self.uses = 2

    def apply(self,character):
        foundItem = None
        for item in character.inventory:
            if item.type == "Corpse":
                foundItem = item
                break
        
        if not foundItem:
            character.addMessage("no corpse in inventory")
            return

        character.inventory.remove(foundItem)
        spark = src.items.itemMap["StaticSpark"]()
        spark.level = self.level
        character.inventory.append(spark)
        character.addMessage("corpse sacrificed for spark")
        self.uses -= 1

    def render(self):
        if self.uses == 2:
            return (src.interaction.urwid.AttrSpec("#aaf","black"),"&°")
        elif self.uses == 1:
            return [(src.interaction.urwid.AttrSpec("#aaf","black"),"&"),(src.interaction.urwid.AttrSpec("#f00","black"),"°")]
        else:
            return (src.interaction.urwid.AttrSpec("#f00","black"),"&°")

class BluePrintingArtwork(Item):
    type = "BluePrintingArtwork"

    def __init__(self,xPosition=0,yPosition=0,name="BluePrintingArtwork",creator=None,noId=False):
        super().__init__("BA",xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        self.character = character
        self.submenue = src.interaction.InputMenu("input menue")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createBlueprint
        return

    def createBlueprint(self):
        if not self.submenue.text in itemMap:
            self.character.addMessage("item not found")
            return
        new = BluePrint()
        new.setToProduce(self.submenue.text)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        self.room.addItems([new])

class ScrapCommander(Item):
    type = "ScrapCommander"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(";;",xPosition,yPosition,creator=creator,name="scrap commander")

        self.bolted = True
        self.walkable = True
        self.numScrapStored = 0
        self.attributesToStore.extend([
               "numScrapStored"])

    def apply(self,character):
        options = [("addScrap","add scrap"),("fetchScrap","fetch scrap")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def setScrapPath(self,numScrap):
        fieldNum = numScrap//20

        rowNum = fieldNum//11
        rowRemain = fieldNum%11

        
    def runCommandString(self,command,character):
        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]


    def apply2(self):
        if self.submenue.selection == "addScrap":
            self.character.addMessage("should add now")
            self.numScrapStored += 1
            self.setScrapPath(self.numScrapStored)
        elif self.submenue.selection == "fetchScrap":
            if self.numScrapStored == 0:
                self.character.addMessage("no scrap available")
                return

            self.numScrapStored -= 1

            move = ""
            move += "a"*(11-2-self.numScrapStored//(20*11))
            remaining = self.numScrapStored%(20*11)
            self.character.addMessage(remaining)
            if remaining > 10*20-1:
                move += "Ka"
            else:
                move += "a"
                if remaining > 5*20-1:
                    move += "s"*(-(remaining//20-5-4))
                    move += "Ks"
                    move += "w"*(-(remaining//20-5-4))
                else:
                    move += "w"*(-(remaining//20-4))
                    move += "Kw"
                    move += "s"*(-(remaining//20-4))
                move += "d"
            move += "d"*(11-2-self.numScrapStored//(20*11))

            self.character.addMessage(move)
            self.runCommandString(move,self.character)


commons = [
            "MarkerBean",
            "MetalBars",
            "Connector",
            "Bolt",
            "Stripe",
            "puller",
            "pusher",
            "Puller",
            "Pusher",
            "Stripe",
            "Rod",
            "Case",
            "Heater",
            "Mount",
            "Tank",
            "Frame",
            "Radiator",
            "Sheet",
            "GooFlask",
            "Vial",
            "Wall",
            "Door",
            "MarkerBean",
            "MemoryCell",
            "Paving",
            "GooFlask",
            "Vial",
            "ScrapCompactor",
            "PavingGenerator",
            "Machine",
            "Sheet",
        ]

semiCommons = [
        "UniformStockpileManager",
        "TypedStockpileManager",
        "GrowthTank",
        "GooDispenser",
        "MaggotFermenter",
        "BioPress",
        "GooProducer",
        "ItemUpgrader",
        "Scraper",
        "Sorter",
        "StasisTank",
        "BluePrinter",
        "BloomShredder",
        "SporeExtractor",
        "BloomContainer",
        "Container",
        "SanitaryStation",
        "AutoScribe",
        "ItemCollector",
        "HealingStation",
        ]

rare = [
        "MachineMachine",
        "ProductionArtwork",
        ]

# maping from strings to all items
# should be extendable
itemMap = {
            "Item":Item,
            "MarkerBean":MarkerBean,
            "Connector":Connector,
            "Bolt":Bolt,
            "Stripe":Stripe,
            "puller":Puller,
            "pusher":Pusher,
            "Puller":Puller,
            "Pusher":Pusher,
            "Stripe":Stripe,
            "Rod":Rod,
            "Heater":Heater,
            "Mount":Mount,
            "Tank":Tank,
            "Frame":Frame,
            "Radiator":Radiator,
            "PressCake":PressCake,
            "BioMass":BioMass,
            "MemoryCell":MemoryCell,
            "Explosive":Explosive,
            "FloorPlate":FloorPlate,
            "Chemical":Chemical,
            "Paving":Paving,

            "Furnace":Furnace,
            "SuicideBooth":SuicideBooth,
            "Corpse":Corpse,
            "GrowthTank":GrowthTank,
            "RoomControls":RoomControls,
            "Boiler":Boiler,
            "GooDispenser":GooDispenser,
            "GooFlask":GooFlask,
            "ProductionArtwork":ProductionArtwork,
            "Tree":Tree,
            "MachineMachine":MachineMachine,
            "ScrapCompactor":ScrapCompactor,
            "PavingGenerator":PavingGenerator,
            "Token":Token,
            "MaggotFermenter":MaggotFermenter,
            "BioPress":BioPress,
            "VatMaggot":VatMaggot,
            "GooProducer":GooProducer,
            "Machine":Machine,
            "Scraper":Scraper,
            "Sorter":Sorter,
            "Drill":Drill,
            "RoomBuilder":RoomBuilder,
            "BluePrint":BluePrint,
            "ItemUpgrader":ItemUpgrader,
            "ItemDowngrader":ItemDowngrader,
            "StasisTank":StasisTank,
            "BluePrinter":BluePrinter,
            "PositioningDevice":PositioningDevice,
            "Watch":Watch,
            "Note":Note,
            "Bomb":Bomb,
            "Command":Command,
            "Mortar":Mortar,
            "BloomShredder":BloomShredder,
            "SporeExtractor":SporeExtractor,
            "GlobalMacroStorage":GlobalMacroStorage,
            "BloomContainer":BloomContainer,
            "Container":Container,
            "SunScreen":SunScreen,
            "Spawner":Spawner,
            "FireCrystals":FireCrystals,
            "Mover":Mover,
            "MoldFeed":MoldFeed,
            "SeededMoldFeed":SeededMoldFeed,
            "Vial":Vial,
            "CorpseShredder":CorpseShredder,
            "BluePrintingArtwork":BluePrintingArtwork,
            "WaterCondenser":WaterCondenser,
            "GooFaucet":GooFaucet,
            "ResourceTerminal":ResourceTerminal,
            "RessourceTerminal":ResourceTerminal,

            "Hutch":Hutch,
            "Lever":Lever,
            "CommLink":Commlink,
            "Display":RoomControls,
            "Spray":Spray,
            "ObjectDispenser":OjectDispenser,
            "Engraver":Engraver,
            "CoalMine":CoalMine,
            "GameTestingProducer":GameTestingProducer,
            "ReactionChamber":ReactionChamber,
            "Chute":Chute,
            "CommandBook":CommandBook,
            "PortableChallenger":PortableChallenger,

            "PathingNode":PathingNode,
            "MemoryBank":MemoryBank,
            "MemoryDump":MemoryDump,
            "MemoryStack":MemoryStack,
            "MemoryReset":MemoryReset,
            "BackTracker":BackTracker,
            "SimpleRunner":SimpleRunner,
            "Tumbler":Tumbler,
            "MacroRunner":MacroRunner,
            "Sheet":Sheet,
            "Map":Map,
            "SanitaryStation":SanitaryStation,

            "ScrapCommander":ScrapCommander,
            "InfoScreen":AutoTutor,
            "AutoTutor":AutoTutor,
            "AutoTutor2":AutoTutor2,
            "TransportOutNode":TransportOutNode,
            "TransportInNode":TransportInNode,
            "UniformStockpileManager":UniformStockpileManager,
            "TypedStockpileManager":TypedStockpileManager,
            "RipInReality":RipInReality,
            "AutoScribe":AutoScribe,
            "ItemCollector":ItemCollector,
            "HealingStation":HealingStation,
            "JobBoard":JobBoard,
            "AutoFarmer":AutoFarmer,

            "Explosion":Explosion,

            "Moss":Mold,
            "Mold":Mold,
            "MossSeed":MoldSpore,
            "MoldSpore":MoldSpore,
            "Bloom":Bloom,
            "Sprout":Sprout,
            "Sprout2":Sprout2,
            "SickBloom":SickBloom,
            "CommandBloom":CommandBloom,
            "PoisonBloom":PoisonBloom,
            "Bush":Bush,
            "PoisonBush":PoisonBush,
            "EncrustedBush":EncrustedBush,
            "Test":EncrustedPoisonBush,
            "EncrustedPoisonBush":EncrustedPoisonBush,
            "HiveMind":HiveMind,
            "SwarmIntegrator":SwarmIntegrator,
            "SaccrificialCircle":SaccrificialCircle,

            "MiningShaft":MiningShaft,
            "Armor":Armor,
            "StaticSpark":StaticSpark,
            "SparcRewardLock":SparcRewardLock,
}

rawMaterialLookup = {
    "WaterCondenser":["Sheet","Case"],
    "Sheet":["MetalBars"],
    "Radiator":["MetalBars"],
    "Mount":["MetalBars"],
    "Stripe":["MetalBars"],
    "Bolt":["MetalBars"],
    "Rod":["MetalBars"],
    "Tank":["Sheet"],
    "Heater":["Radiator"],
    "Connector":["Mount"],
    "pusher":["Stripe"],
    "puller":["Bolt"],
    "Frame":["Rod"],
    "Case":["Frame"],
    "PocketFrame":["Frame"],
    "MemoryCell":["Connector"],
    "AutoScribe":["Case","MetalBars","MemoryCell","pusher","puller"],
    "FloorPlate":["Sheet","MetalBars"],
    "Scraper":["Case","MetalBars"],
    "GrowthTank":["Case","MetalBars"],
    "Door":["Case","MetalBars"],
    "Wall":["Case","MetalBars"],
    "Boiler":["Case","MetalBars"],
    "Drill":["Case","MetalBars"],
    "Furnace":["Case","MetalBars"],
    "ScrapCompactor":["MetalBars"],
    "GooFlask":["Tank"],
    "GooDispenser":["Case","MetalBars","Heater"],
    "MaggotFermenter":["Case","MetalBars","Heater"],
    "BloomShredder":["Case","MetalBars","Heater"],
    "SporeExtractor":["Case","MetalBars","puller"],
    "BioPress":["Case","MetalBars","Heater"],
    "GooProducer":["Case","MetalBars","Heater"],
    "CorpseShredder":["Case","MetalBars","Heater"],
    "MemoryDump":["Case","MemoryCell"],
    "MemoryStack":["Case","MemoryCell"],
    "MemoryReset":["Case","MemoryCell"],
    "MemoryBank":["Case","MemoryCell"],
    "SimpleRunner":["Case","MemoryCell"],
    "MarkerBean":["PocketFrame"],
    "PositioningDevice":["PocketFrame"],
    "Watch":["PocketFrame"],
    "BackTracker":["PocketFrame"],
    "Tumbler":["PocketFrame"],
    "RoomControls":["Case","pusher","puller"],
    "StasisTank":["Case","pusher","puller"],
    "ItemUpgrader":["Case","pusher","puller"],
    "ItemDowngrader":["Case","pusher","puller"],
    "RoomBuilder":["Case","pusher","puller"],
    "BluePrinter":["Case","pusher","puller"],
    "Container":["Case","Sheet"],
    "BloomContainer":["Case","Sheet"],
    "Mover":["Case","pusher","puller"],
    "Sorter":["Case","pusher","puller"],
    "FireCrystals":["Coal","SickBloom"],
    "Bomb":["Frame","Explosive"],
    "ProductionManager":["Case","MemoryCell","Connector"],
    "AutoFarmer":["FloorPlate","MemoryCell","Connector"],
    "UniformStockpileManager":["Case","MemoryCell","Connector"],
    "TypedStockpileManager":["Case","MemoryCell","Connector"],
}

'''
get item instances from dict state
'''
def getItemFromState(state):
    item = itemMap[state["type"]](noId=True)
    item.setState(state)
    if "id" in state:
        item.id = state["id"]
    src.saveing.loadingRegistry.register(item)
    return item

