import src

'''
'''
class Machine(src.items.Item):
    type = "Machine"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,name="Machine",seed=0,noId=False):
        self.toProduce = "Wall"

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.productionLevel = 1
        self.commands = {}

        super().__init__(display=src.canvas.displayChars.machine,name=name,seed=seed)

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

src.items.addType(Machine)
