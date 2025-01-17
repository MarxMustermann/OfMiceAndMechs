"""
items and item related code belongs here
"""
import logging

import src

logger = logging.getLogger(__name__)

class Item:
    """
    This is the base class for ingame items. It is intended to hold the common behaviour of items.

    Attributes:
        seed (int): rng seed intended to have predictable randomness
        container: references where the item is placed currently

    """

    type = "Item"

    # flags for traits
    runsJobOrders = False
    hasSettings = False
    runsCommands = False
    canReset = False
    hasMaintenance = False
    hasStepOnAction = False

    isAbstract = False
    isFood = False
    godMode = False
    isStepOnActive = False
    level = 1
    nutrition = 0
    description = None
    xPosition = None
    yPosition = None
    zPosition = None
    walkable = False
    bolted = True
    blocked = False
    usageInfo = None
    tasks = []
    container = None
    name = "unknown"

    def getTerrainPosition(self):
        return self.getTerrain().getPosition()

    def callInit(self):
        super().__init__()

    def __init__(self, display=None, name=None, seed=0, noId=False):
        """
        the constructor

        Parameters:
            display: information on how the item is shown, can be a string
            name: name shown to the user
            seed: rng seed
            noId: flag to prevent generating useless ids (obsolete?)
        """
        #super().__init__()

        self.commandOptions = []
        self.applyOptions = []
        self.ignoreAttributes = []
        self.applyMap = {}
        self.settings = {}
        self.charges = 0
        self.watched = []

        self.callInit()

        self.doOwnInit(display=display,name=name,seed=seed,noId=noId)

    def doOwnInit(self,display=None, name=None, seed=0, noId=False):
        if display:
            self.display = display
        else:
            self.display = "??"

        # basic information
        self.seed = seed
        if name:
            self.name = name

        # storage for other entities listening to changes
        self.listeners = {"default": []}

        # management for movement
        self.chainedTo = []

        # properties for traits
        self.commands = {}

    def callIndirect(self, callback, extraParams=None):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if extraParams is None:
            extraParams = {}
        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

    def startWatching(self, target, callback, tag=""):
        """
        register callback to be notified if an event occours

        Parameters:
            target: the thing that is watching
            callback: the callback to call
            tag: the type of event to listen for
        """

        if tag == "":
            1/0

        try:
            self.watched
        except:
            self.watched = []
        target.addListener(callback, tag)
        self.watched.append((target, callback,tag))

    def stopWatching(self, target, callback, tag=""):
        """
        deregister callback from being notified if an event occurs

        Parameters:
            target: the thing that is watching
            callback: the callback to call
            tag: the type of event to listen for
        """

        if tag == "":
            1/0

        target.delListener(callback, tag)
        self.watched.remove((target, callback, tag))

    def stopWatchingAll(self):
        try:
            self.watched
        except:
            self.watched = []
        for listenItem in self.watched[:]:
            self.stopWatching(listenItem[0], listenItem[1], listenItem[2])

    def doStepOnAction(self, character):
        pass

    def setPosition(self, pos):
        """
        set the position

        Parameters:
            the position
        """

        self.xPosition = pos[0]
        self.yPosition = pos[1]
        self.zPosition = pos[2]

    def getPosition(self,offset=(0,0,0)):
        """
        get the position

        Returns:
            the position
        """
        if self.xPosition is None or self.yPosition is None or self.zPosition is None:
            logger.error(f"get position of non positioned item. {self}")
            return (None,None,None)
        return self.xPosition+offset[0], self.yPosition+offset[1], self.zPosition+offset[2]

    def getSmallPosition(self,offset=(0,0,0)):
        pos = self.getPosition()
        return (pos[0]%15,pos[1]%15,pos[2]%15)

    def useJoborderRelayToLocalRoom(self, character, tasks, itemType, information=None):
        """
        delegate a task to another item using a room manager

        Parameters:
            character: the character used for running the job order
            tasks: the tasks to delegate
            itemType: the type of item the task should be delegated to
            information: optional information block on the job order
        """

        # set up job order
        if information is None:
            information = {}
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.taskName = "relay job Order"
        jobOrder.information = information

        # prepare the task for going to the roommanager
        newTasks = [
            {
                "task": "go to room manager",
                "command": self.commands["go to room manager"],
            },
        ]

        # prepare the tasks for delegating the given tasks
        for task in tasks:
            newTasks.append(
                {
                    "task": "insert job order",
                    "command": "scj",
                }
            )
            newTasks.append(
                {
                    "task": "relay job order",
                    "command": None,
                    "type": "Item",
                    "ItemType": itemType,
                }
            )
            newTasks.append(task)

        # prepare the task for returning from the roommanager
        newTasks.append(
            {
                "task": "return from room manager",
                "command": self.commands["return from room manager"],
            }
        )

        # prepare the task for going to the roommanager
        newTasks.append(
            {
                "task": "insert job order",
                "command": "scj",
            }
        )
        newTasks.append(
            {
                "task": "register result",
                "command": None,
            }
        )

        # add prepared tasks to job order
        jobOrder.tasks = list(reversed(newTasks))

        # run job order
        character.addMessage("running job order local room relay")
        character.jobOrders.append(jobOrder)
        character.runCommandString("Jj.j")

    def gatherApplyActions(self, character=None):
        """
        returns a list of actions that should be run when using this item
        this is intended to be overwritten to add actions

        Parameters:
            character: the character using the item
        Returns:
            a list of function calls to run
        """

        result = []

        # add spawning menus if applicable
        if self.applyOptions:
            result.append(self.__spawnApplyMenu)

        # eat food on activation
        if self.isFood:
            result.append(self.getEaten)

        return result

    def __spawnApplyMenu(self, character):
        """
        spawns a selection menu and registers a callback for when the selection is ready
        this is intended to by used by setting self.applyOptions

        Parameters:
            character: the character getting the menu
        """

        options = []
        for option in self.applyOptions:
            options.append(option)
        submenu = src.menuFolder.selectionMenu.SelectionMenu(
            "what do you want to do?", options
        )
        submenu.extraInfo["item"] = self
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
            "method": "handleApplyMenu",
            "container": self,
            "params": {"character": character},
        }
        character.runCommandString("~",nativeKey=True)

    def handleApplyMenu(self, params):
        """
        calls a function depending on user selection

        Parameters:
            params: context for the selection
        """

        character = params["character"]

        selection = character.macroState["submenue"].selection

        if not selection:
            return

        # call the function set for the selection
        if selection+"_"+params.get("key","") in self.applyMap:
            self.applyMap[selection+"_"+params.get("key","")](character)
            return

        self.applyMap[selection](character)

    def getTerrain(self):
        """
        gets the terrain the item is placed on directly or indirectly

        Return:
            the terrain
        """

        if isinstance(self.container, src.rooms.Room):
            terrain = self.container.container
        elif self.container:
            terrain = self.container
        return terrain

    def apply(self, character):
        """
        handles usage by a character

        Parameters:
            character: the character using the item
        """

        # gather actions
        actions = self.gatherApplyActions(character)
        character.timeTaken += 1

        # run actions
        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("i can not do anything useful with this")

    def __vanillaPickUp(self, character):
        """
        basic behaviour for getting picked up

        Parameters:
            character: the character using the item
        """

        # prevent crashes
        if self.xPosition is None or self.yPosition is None:
            return

        # apply restrictions
        if self.bolted:
            character.addMessage("you cannot pick up bolted items")
            character.changed("pickup bolted fail",{"item":self})
            return

        # do the pick up
        character.addMessage("you pick up a %s" % self.type)
        if not self.walkable:
            character.addMessage("it's heavy and slows you down")
        self.container.removeItem(self)
        character.addToInventory(self)

    def gatherPickupActions(self, character=None):
        """
        returns a list of actions that should be run when picking up this item
        this is intended to be overwritten to add actions

        Parameters:
            character: the character picking up the item
        Returns:
            a list of functions
        """

        return [self.__vanillaPickUp ,self.pickUpNonWalkable]

    def degrade(self,multiplier=1,character=None):
        return

    def pickUp(self, character):
        """
        handles getting picked up by a character

        Parameters:
            character: the character picking up the item
        """

        if src.gamestate.gamestate.mainChar in character.container.characters:
            src.interaction.playSound("itemPickedUp","actions")

        oldPos = self.getPosition()

        # gather the actions
        actions = self.gatherPickupActions()

        # run the actions
        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("no pickup action found")

        character.changed("itemPickedUp",(character,self,oldPos))

    def pickUpNonWalkable(self, character):
        if not self.walkable:
            character.addListener(self.OnDropNonWalkable,"dropped")
            self.NonWalkableItemDeBuff = src.statusEffects.statusEffectMap["Slowed"](slowDown=0.1, duration = None,inventoryItem = self)
            character.statusEffects.append(self.NonWalkableItemDeBuff)

    def OnDropNonWalkable(self,params):
        (character,item) = params
        if item == self:
            if self.NonWalkableItemDeBuff in character.statusEffects:
                character.statusEffects.remove(self.NonWalkableItemDeBuff)
            character.delListener(self.OnDropNonWalkable,"dropped")

    def getBigPosition(self,offset=(0,0,0)):
        if self.container.isRoom:
            return (self.container.xPosition+offset[0],self.container.yPosition+offset[1],offset[2])
        else:
            return (self.xPosition//15+offset[0],self.yPosition//15+offset[1],offset[2])

    def getUsageInformation(self):
        return self.usageInfo

    def getLongInfo(self):
        """
        returns a long text description to show to the player

        Returns:
            string: the description text
        """

        text = "item: " + self.type + " \n\n"
        if self.description:
            text += "description: \n" + self.description + "\n\n"
        if self.usageInfo:
            text += f"usage: \n{self.getUsageInformation()}\n"
        if self.commands:
            text += "commands: \n"
            for (
                key,
                value,
            ) in self.commands.items():
                text += f"{key}: {value}\n"
            text += "\n"
        if self.settings:
            text += "settings: \n"
            for (
                key,
                value,
            ) in self.settings.items():
                text += f"{key}: {value}\n"
            text += "\n"
        return text

    def render(self):
        """
        returns the rendered item

        Returns:
            the display information
        """

        return self.display

    def getDetailedInfo(self):
        """
        returns a short text description to show to the player

        Returns:
            str: the description text
        """
        if self.description:
            return self.description
        else:
            return ""

    def fetchSpecialRegisterInformation(self):
        """
        returns some of the objects state to be stored ingame in a characters registers
        this is intended to be overwritten to add more information

        Returns:
            a dictionary containing the information
        """

        result = {}
        if hasattr(self, "type"):
            result["type"] = self.type
        if hasattr(self, "charges"):
            result["charges"] = self.charges
        if hasattr(self, "uses"):
            result["uses"] = self.uses
        if hasattr(self, "level"):
            result["level"] = self.level
        if hasattr(self, "coolDown"):
            result["coolDown"] = self.coolDown
        if hasattr(self, "amount"):
            result["amount"] = self.amount
        if hasattr(self, "walkable"):
            result["walkable"] = self.walkable
        if hasattr(self, "bolted"):
            result["bolted"] = self.bolted
        if hasattr(self, "blocked"):
            result["blocked"] = self.blocked
        return result

    def getEaten(self, character):
        """
        get eaten by a character

        Parameters:
            character: the character eating the item
        """

        character.addMessage(f"you eat the {self.name}")
        character.addSatiation(self.nutrition)
        self.destroy(generateScrap=False)

    def configure(self, character):
        """
        handle a character trying to configure this item by spawning a submenu

        Parameters:
            character: the character configuring this item
        """

        # store last action for debug purposes
        self.lastAction = "configure"

        # fetch the option
        options = self.getConfigurationOptions(character)

        # reformat options for menu
        text = ""
        if not options:
            text += "this machine cannot be configured, press any key to continue"
        else:
            for (key, value) in options.items():
                text += f"{key}: {value[0]}\n"

        # spawn menu
        submenu = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text)
        submenu.tag = "configurationSelection"
        character.macroState["submenue"] = submenu

        # register callback
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "configureSwitch",
            "params": {"character": character},
        }

    def configureSwitch(self, params):
        """
        handle the selection of a configuration option by a character
        Parameters:
            params: context for the selection
        """

        # save last action for debug
        self.lastAction = "configureSwitch"

        # fetch configuration options
        character = params["character"]
        options = self.getConfigurationOptions(character)

        # call selected function
        if params["keyPressed"] in options:
            option = options[params["keyPressed"]][1](character)
        else:
            character.addMessage("no configure action found for this key")

    # bug: breaks saving if a npc uses this while saving
    # it breaks because function pointers cannot be saved directly
    # needs to be migrate to indirect call
    def getConfigurationOptions(self, character):
        """
        returns a list of configuration options for the item
        this is intended to be overwritten to add more options

        Returns:
            a dictionary containing function calls with description
        """

        options = {}
        if self.runsCommands:
            options["c"] = ("add command", self.spawnSetCommand)
        if self.hasSettings:
            options["s"] = ("machine settings", None)  # self.setMachineSettings)
        if self.runsJobOrders:
            options["j"] = ("run job order", self.runJobOrder)
        if self.canReset:
            options["r"] = ("reset", self.reset)
        if self.hasMaintenance:
            options["m"] = ("do maintenance", self.doMaintenance)
        return options

    def spawnSetCommand(self,character):
        """
        spawns a menu to set a command
        will call setCommand eventually

        Parameters:
            character: the character trying to set a command
        """

        options = self.commandOptions
        submenu = src.menuFolder.selectionMenu.SelectionMenu(
            "what command do you want to set?", options
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
            "method": "handleSetCommandMenu",
            "container": self,
            "params": {"character": character},
        }

    def handleSetCommandMenu(self,params):
        """
        handle a character having selected which command to set

        Parameters:
            params: context from the interaction menu
        """

        # get command from characters inventory
        character = params["character"]
        commands = character.searchInventory("Command")
        if not commands:
            character.addMessage("no command found in inventory")
            return
        command = commands[0]
        character.removeItemFromInventory(command)

        character.addMessage("you set the command for %s"%params["selection"])
        self.setCommand(command,params["selection"])

    def setCommand(self,command,eventName):
        """
        actually set an command
        the command set will be run by the item under certain condition
        is intended to be used by the player to automate things
        is used to automate prefabricated settings

        Parameters:
            command: the command to set
            eventName: the name of the event that should trigger running the command
        """

        self.commands[eventName] = command.command

    def reset(self, character):
        """
        dummy for handling a character trying to reset the machine

        Parameters:
            character: the character triggering the reset request
        """

        if character:
            character.addMessage("you reset the machine")

    def doMaintenance(self, character):
        """
        dummy for handling a character trying to do maintenance

        Parameters:
            character: the character triggering the maintenance offer
        """

        character.addMessage("no maintenance action set")

    def addTriggerToTriggerMap(self, result, name, function):
        """
        helper function to handle annoying data structure.

        Parameters:
            result: a dict of lists containing callbacks that should be extended
            name: the name or key the callback should trigger on
                function: the callback
        """

        triggerList = result.get(name)
        if not triggerList:
            triggerList = []
            result[name] = triggerList
        triggerList.append(function)

    def getJobOrderTriggers(self):
        """
        returns a dict of lists containing callbacks to be triggered by a job order

        Returns:
            a dict of lists
        """

        result = {}
        self.addTriggerToTriggerMap(result, "configure machine", self.jobOrderConfigure)
        self.addTriggerToTriggerMap(result, "register result", self.doRegisterResult)
        self.addTriggerToTriggerMap(result, "run command", self.jobOrderRunCommand)
        return result

    def doRegisterResult(self, task, context):
        """
        dummy callback for registering success or failure of a job order

        Parameters:
            task: the task details
            context: the context of the task
        """


    def jobOrderRunCommand(self, task, context):
        character = context["character"]
        character.runCommandString(self.commands[task["toRun"]])

    def jobOrderConfigure(self, task, context):
        """
        callback for configuring the item throug a job order
        Parameters:
            task: the task details
            context: the context of the task
        """

        # configure commands
        for (commandName, command) in task["commands"].items():
            self.commands[commandName] = command

    def runJobOrder(self, character):
        """
        handle a job order run on this item
        Parameters:
            character: the character running the job order on the item
        """

        # save last action for debug
        self.lastAction = "runJobOrder"

        if not character.jobOrders:
            character.addMessage("no job order")
            return

        # get task
        jobOrder = character.jobOrders[-1]
        task = jobOrder.popTask()

        if not task:
            character.addMessage("no tasks left")
            return

        # select callback to trigger
        triggerMap = self.getJobOrderTriggers()
        triggers = triggerMap.get(task["task"])
        if not triggers:
            character.addMessage(
                f"unknown trigger: {self} {task}"
            )
            return

        # trigger callbacks
        for trigger in triggers:
            trigger(task, {"character": character, "jobOrder": jobOrder})

    def runCommand(self, commandName, character):
        """
        runs a preconfigured command on a character
        Parameters:
            commandName: the kind/name of command to run
            character: the character to run the command on
        """

        # select the command from the list of preconfigured commands
        command = self.commands.get(commandName)
        if not command:
            return

        # run the selected command on the character
        character.runCommandString(command)
        character.addMessage(
            f"running command for trigger: {commandName} - {command}"
        )

    def upgrade(self):
        """
        upgrade item
        """

        self.level += 1

    def downgrade(self):
        """
        downgrade item
        """

        self.level -= 1

    # bad code: should be extra class
    def addListener(self, listenFunction, tag="default"):
        """
        register a callback for notifications

        Parameters:
            listenFunction: the callback to call if the item needs to notify something
            tag: a tag to restrict notifications to
        """

        # create bucket if it does not exist yet
        if tag not in self.listeners:
            self.listeners[tag] = []

        # store the callback to call when applicable
        if listenFunction not in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    # bad code: should be extra class
    def delListener(self, listenFunction, tag="default"):
        """
        deregistering a callback for notifications
        """

        # remove callback from internal list
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clean up empty buckets
        if not self.listeners[tag] and tag != "default":
            del self.listeners[tag]

    # bad code: probably misnamed
    # bad code: should be extra class
    def changed(self, tag="default", info=None):
        """
        send notifications about changes to registered listeners

        Parameters:
            tag: the tag for filtering the listeners to notify
            info: additional information
        """

        if tag not in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info is None:
                listenFunction()
            else:
                listenFunction(info)

    def getAffectedByMovementDirection(self, direction, force=1, movementBlock=None):
        """
        extend the list of things that would be affected if this item would move

        Parameters:
            direction: the direction the item should move in
            force: force movement even if something breaks
            movementBlock: the collection of things that are moving and should be extended
        """

        # add self
        if movementBlock is None:
            movementBlock = set()
        movementBlock.add(self)

        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and thing != self:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(
                    direction, force=force, movementBlock=movementBlock
                )

        return movementBlock

    def moveDirection(self, direction, force=1, initialMovement=True):
        """
        move the item into a direction

        Parameters:
            direction: the direction the item should move in
            force: force movement even if something breaks
            movementBlock: a flag if this initates the movement
        """

        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            oldPosition = (self.xPosition, self.yPosition, self.zPosition)
            if direction == "north":
                newPosition = (self.xPosition, self.yPosition - 1, self.zPosition)
            elif direction == "south":
                newPosition = (self.xPosition, self.yPosition + 1, self.zPosition)
            elif direction == "west":
                newPosition = (self.xPosition - 1, self.yPosition, self.zPosition)
            elif direction == "east":
                newPosition = (self.xPosition + 1, self.yPosition, self.zPosition)

            # remove self from current position
            container = self.container
            self.container.removeItem(self)

            # destroy everything on target position
            for item in container.getItemByPosition(newPosition):
                item.destroy()

            # place self on new position
            container.addItem(self, newPosition)

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(container.getItemByPosition(newPosition)) > 1:
                self.destroy()

    def getResistance(self):
        """
        get the physical resistance to being moved

        Returns:
            int: a indicator of the resistance against being moved
        """

        if self.walkable:
            return 1
        else:
            return 50

    def destroy(self, generateScrap=True):
        """
        destroy the item and leave scrap

        Parameters:
            generateScrap: a flag indication wether scrap should be left by the destruction
        """

        container = self.container

        if not container:
            return

        pos = (self.xPosition, self.yPosition, self.zPosition)

        # remove item
        container.removeItem(self)

        # clean up references
        self.stopWatchingAll()

        # generate scrap
        if generateScrap:
            amount = 1
            if not self.walkable:
                amount = 20
            newItem = src.items.itemMap["Scrap"](amount=amount)

            toRemove = []
            for item in container.getItemByPosition(pos):
                toRemove.append(item)
                if item.type != "Scrap":
                    newItem.amount += 1
                else:
                    newItem.amount += item.amount
            container.removeItems(toRemove)
            newItem.setWalkable()

            # place scrap
            container.addItems([(newItem,pos)])

    def constrain_within_room(self, pos):
        x = src.helpers.clamp(pos[0],1,11)
        y = src.helpers.clamp(pos[1],1,11)
        return x,y,pos[2]

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


def addType(toRegister,potion=False):
    """
    add a item type to the item map
    This is used to be able to store the item classes without knowing where everything exactly is.
    Each item needs to actively register here or it will not be available.
    """

    itemMap[toRegister.type] = toRegister

    if potion:
        potionTypes.append(toRegister)

potionTypes = []

# mapping from strings to all items
# should be extendable
itemMap = {
    "Item": Item,
}

rawMaterialLookup = {
    "WaterCondenser": ["Sheet", "Case"],
    "Sheet": ["MetalBars"],
    "Radiator": ["MetalBars"],
    "Mount": ["MetalBars"],
    "Stripe": ["MetalBars"],
    "Bolt": ["MetalBars"],
    "Rod": ["MetalBars"],
    "Painter": ["Tank","Heater"],
    "Tank": ["Sheet"],
    "Heater": ["Radiator"],
    "Connector": ["Mount"],
    "pusher": ["Stripe"],
    "puller": ["Bolt"],
    "Frame": ["Rod"],
    "Case": ["Frame"],
    "PocketFrame": ["Frame"],
    "MemoryCell": ["Connector"],
    "AutoScribe": ["Case", "MetalBars", "MemoryCell", "pusher", "puller"],
    "FloorPlate": ["Sheet", "MetalBars"],
    "Scraper": ["Case", "MetalBars"],
    "GrowthTank": ["Case", "MetalBars"],
    "Door": ["Case", "MetalBars"],
    "Wall": ["Case", "MetalBars"],
    "Boiler": ["Case", "MetalBars"],
    "Drill": ["Case", "MetalBars"],
    "Furnace": ["Case", "MetalBars"],
    "ScrapCompactor": ["MetalBars"],
    "Flask": ["Tank"],
    "GooDispenser": ["Case", "MetalBars", "Heater"],
    "MaggotFermenter": ["Case", "MetalBars", "Heater"],
    "BloomShredder": ["Case", "MetalBars", "Heater"],
    "SporeExtractor": ["Case", "MetalBars", "puller"],
    "BioPress": ["Case", "MetalBars", "Heater"],
    "GooProducer": ["Case", "MetalBars", "Heater"],
    "CorpseShredder": ["Case", "MetalBars", "Heater"],
    "MemoryDump": ["Case", "MemoryCell"],
    "MemoryStack": ["Case", "MemoryCell"],
    "MemoryReset": ["Case", "MemoryCell"],
    "MemoryBank": ["Case", "MemoryCell"],
    "SimpleRunner": ["Case", "MemoryCell"],
    "MarkerBean": ["PocketFrame"],
    "PositioningDevice": ["PocketFrame"],
    "Watch": ["PocketFrame"],
    "BackTracker": ["PocketFrame"],
    "Tumbler": ["PocketFrame"],
    "RoomControls": ["Case", "pusher", "puller"],
    "StasisTank": ["Case", "pusher", "puller"],
    "ItemUpgrader": ["Case", "pusher", "puller"],
    "ItemDowngrader": ["Case", "pusher", "puller"],
    "RoomBuilder": ["Case", "pusher", "puller"],
    "BluePrinter": ["Case", "pusher", "puller"],
    "Container": ["Case", "Sheet"],
    "BloomContainer": ["Case", "Sheet"],
    "Mover": ["Case", "pusher", "puller"],
    "Sorter": ["Case", "pusher", "puller"],
    "FireCrystals": ["Coal", "SickBloom"],
    "Bomb": ["Frame", "Explosive"],
    "ProductionManager": ["Case", "MemoryCell", "Connector"],
    "AutoFarmer": ["FloorPlate", "MemoryCell", "Connector"],
    "UniformStockpileManager": ["Case", "MemoryCell", "Connector"],
    "TypedStockpileManager": ["Case", "MemoryCell", "Connector"],
    "Sword": ["Rod"],
}
