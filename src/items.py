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
    """
    load the item modules
    """
    import src.itemFolder


# load basic libs
import json
import random
import uuid

# load basic internal libs
import src.saveing
import src.events
import config


class Item(src.saveing.Saveable):
    """
    This is the base class for ingame items. It is intended to hold the common behaviour of items.

    Attributes:
        seed (int): rng seed intended to have predictable randomness
        container: references where the item is placed currently

    """

    type = "Item"

    def __init__(self, display=None, name="unkown", seed=0, noId=False):
        """
        the constructor

        Parameters:
            display: information on how the item is shown, can be a string
            name: name shown to the user
            seed: rng seed
            noId: flag to prevent generating useless ids (obsolete?)
        """
        super().__init__()

        if display:
            self.display = display
        else:
            self.display = "??"

        # basic information
        self.seed = seed
        self.name = name
        self.description = None
        self.xPosition = None
        self.yPosition = None
        self.zPosition = None
        self.container = None
        self.walkable = False
        self.bolted = True
        self.usageInfo = None
        self.tasks = []
        self.blocked = False

        # storage for other entities listening to changes
        self.listeners = {"default": []}

        # management for movement
        self.lastMovementToken = None
        self.chainedTo = []

        # flags for traits
        self.runsJobOrders = False
        self.hasSettings = False
        self.runsCommands = False
        self.canReset = False
        self.hasMaintenance = False

        # properties for traits
        self.commands = {}
        self.applyOptions = []
        self.level = 1
        self.isFood = False
        self.nutrition = 0

        # set up metadata for saving
        self.attributesToStore.extend(
            [
                "seed",
                "xPosition",
                "yPosition",
                "zPosition",
                "name",
                "type",
                "walkable",
                "bolted",
                "description",
                "isConfigurable",
                "hasSettings",
                "runsCommands",
                "canReset",
                "commands",
            ]
        )

        if not noId:
            self.id = uuid.uuid4().hex
        else:
            self.id = None

    def setPosition(self, pos):
        """
        set the position

        Parameters:
            the position
        """

        self.xPosition = pos[0]
        self.yPosition = pos[1]
        self.zPosition = pos[2]

    def getPosition(self):
        """
        get the position

        Returns:
            the position
        """
        return (self.xPosition, self.yPosition, self.zPosition)

    def useJoborderRelayToLocalRoom(self, character, tasks, itemType, information={}):
        """
        delegate a task to another item using a room manager

        Parameters:
            character: the character used for running the job order
            tasks: the tasks to delegate
            itemType: the type of item the task should be delegated to
            information: optional information block on the job order
        """

        # set up job order
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.taskName = "relay job Order"
        jobOrder.information = information

        # prepare the task for gooing to the roommanager
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

        # prepare the task for gooing to the roommanager
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
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {
            "method": "handleApplyMenu",
            "container": self,
            "params": {"character": character},
        }

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
        self.applyMap[selection](character)

    def getTerrain(self):
        """
        gets the terrain the item is placed on directly or indirectly

        Return:
            the terrain
        """

        if isinstance(self.container, src.rooms.Room):
            terrain = self.container.terrain
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
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted and not character.godMode:
            character.addMessage("you cannot pick up bolted items")
            return

        # do the pick up
        character.addMessage("you pick up a %s" % (self.type))
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

        return [self.__vanillaPickUp]

    def pickUp(self, character):
        """
        handles getting picked up by a character

        Parameters:
            character: the character picking up the item
        """

        # gather the actions
        actions = self.gatherPickupActions()

        # run the actions
        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("no pickup action found")

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
            text += "usage: \n%s\n" % (self.usageInfo,)
        if self.commands:
            text += "commands: \n"
            for (
                key,
                value,
            ) in self.commands.items():
                text += "%s: %s\n" % (
                    key,
                    value,
                )
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
            result["coolDownRemaining"] = self.coolDown - (
                src.gamestate.gamestate.tick - self.coolDownTimer
            )
        if hasattr(self, "amount"):
            result["amount"] = self.amount
        if hasattr(self, "walkable"):
            result["walkable"] = self.walkable
        if hasattr(self, "bolted"):
            result["bolted"] = self.bolted
        if hasattr(self, "blocked"):
            result["blocked"] = self.blocked
        return result

    def getConfigurationOptions(self, character):
        """
        returns a list of configuration options for the item
        this is intended to be overwritten to add more options

        Returns:
            a dictionary containing function calls with description
        """

        options = {}
        if self.runsCommands:
            options["c"] = ("commands", None)  # ,self.spawnSetCommands)
        if self.hasSettings:
            options["s"] = ("machine settings", None)  # self.setMachineSettings)
        if self.runsJobOrders:
            options["j"] = ("run job order", self.runJobOrder)
        if self.canReset:
            options["r"] = ("reset", self.reset)
        if self.hasMaintenance:
            options["m"] = ("do maintenance", self.doMaintenance)
        return options

    def getEaten(self, character):
        """
        get eaten by a character

        Parameters:
            character: the character eating the item
        """

        character.addMessage("you eat the %s" % (self.name,))
        character.addSatiation(self.nutrition)
        self.destroy(generateSrcap=False)

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
                text += "%s: %s\n" % (key, value[0])

        # spawn menu
        self.submenue = src.interaction.OneKeystrokeMenu(text)
        character.macroState["submenue"] = self.submenue

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
        if self.submenue.keyPressed in options:
            option = options[self.submenue.keyPressed][1](character)
        else:
            character.addMessage("no configure action found for this key")

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
        return result

    def doRegisterResult(self, task, context):
        """
        dummy callback for registering success or failure of a job order
        Parameters:
            task: the task details
            context: the context of the task
        """

        pass

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
                "unknown trigger: %s %s"
                % (
                    self,
                    task,
                )
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
            "running command for trigger: %s - %s" % (commandName, command)
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

        self.level += 1

    # bad code: should be extra class
    def addListener(self, listenFunction, tag="default"):
        """
        register a callback for notifications

        Parameters:
            listenFunction: the callback to call if the item needs to notify something
            tag: a tag to restrict notifications to
        """

        # create bucket if it does not exist yet
        if not tag in self.listeners:
            self.listeners[tag] = []

        # store the callback to call when applicable
        if not listenFunction in self.listeners[tag]:
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
        if not self.listeners[tag] and not tag == "default":
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

        if not tag in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

    def getAffectedByMovementDirection(self, direction, force=1, movementBlock=set()):
        """
        extend the list of things that would be affected if this item would move

        Parameters:
            direction: the direction the item should move in
            force: force movement even if something breaks
            movementBlock: the collection of things that are moving and should be extended
        """

        # add self
        movementBlock.add(self)

        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
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
            self.container.remove(self)

            # destroy everything on target position
            for item in self.container.getItemByPosition(newPosition):
                item.destroy()

            # place self on new position
            container.addItem(self, newPosition)

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.container.getItemByPosition(newPosition)) > 1:
                self.destroy()

    def getResistance(self):
        """
        get the physical resistance to beeing moved

        Returns:
            int: a indicator of the resistance against beeing moved
        """

        if self.walkable:
            return 1
        else:
            return 50

    def destroy(self, generateSrcap=True):
        """
        destroy the item and leave scrap

        Parameters:
            generateSrcap: a flag indication wether scrap should be left by the destruction
        """

        container = self.container
        pos = (self.xPosition, self.yPosition, self.zPosition)

        # remove item
        container.removeItem(self)

        # generatate scrap
        if generateSrcap:
            newItem = src.items.itemMap["Scrap"](amount=1)

            toRemove = []
            for item in container.getItemByPosition(pos):
                toRemove.append(item)
                if not item.type == "Scrap":
                    newItem.amount += 1
                else:
                    newItem.amount += item.amount
            container.removeItems(toRemove)
            newItem.setWalkable()

            # place scrap
            container.addItems([newItem])


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


def addType(toRegister):
    itemMap[toRegister.type] = toRegister


# maping from strings to all items
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
    "GooFlask": ["Tank"],
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
}


def getItemFromState(state):
    """
    get item instances from dict state

    Parameters:
        state: the state to build the item from
    Returns:
        the create the item
    """

    # create blank item
    item = itemMap[state["type"]]()

    # load state into item
    item.setState(state)

    # set id
    if "id" in state:
        item.id = state["id"]

    # register the item
    src.saveing.loadingRegistry.register(item)

    return item
