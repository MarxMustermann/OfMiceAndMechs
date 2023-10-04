import random

import src


class Machine(src.items.Item):
    """
    ingame item that produces items using ressources
    """

    type = "Machine"

    def __init__(self, seed=0):
        """
        call superclass constructor with modified parameters

        Parameters:
            seed: the rng seed
        """

        self.toProduce = "Wall"

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.productionLevel = 1
        self.commands = {}

        super().__init__(display=src.canvas.displayChars.machine, seed=seed)
        self.name = "machine"
        self.usageInfo = """
Prepare for production by placing the input materials to the west/left/noth/top of this machine.
Activate the machine to produce.
"""

        self.baseName = self.name

        self.setDescription()
        self.resetDisplay()

    def setDescription(self):
        """
        recalculate the machines description
        """

        self.description = self.baseName + f" MetalBar -> {self.toProduce}"

    def resetDisplay(self):
        """
        recalculate how the machine is shown
        """

        chars = "X\\"
        display = (src.interaction.urwid.AttrSpec("#aaa", "black"), chars)
        toProduce = self.toProduce
        colorMap2_1 = {
            "Wall": "#f88",
            "DutyBell": "#f88",
            "Stripe": "#f88",
            "Case": "#f88",
            "Frame": "#f88",
            "Rod": "#f88",
            "Connector": "#8f8",
            "Mount": "#8f8",
            "RoomBuilder": "#8f8",
            "MemoryCell": "#8f8",
            "Door": "#8f8",
            "puller": "#88f",
            "Bolt": "#88f",
            "pusher": "#88f",
            "Heater": "#88f",
            "Radiator": "#88f",
            "GooProducer": "#8ff",
            "AutoScribe": "#8ff",
        }
        colorMap2_2 = {
            "Wall": "#a88",
            "DutyBell": "#a88",
            "Stripe": "#8a8",
            "Case": "#88a",
            "Frame": "#8aa",
            "Rod": "#a8a",
            "Connector": "#a88",
            "Mount": "#8a8",
            "RoomBuilder": "#88a",
            "MemoryCell": "#8aa",
            "Door": "#a8a",
            "puller": "#a88",
            "Bolt": "#8a8",
            "pusher": "#88a",
            "Heater": "#8aa",
            "Radiator": "#a8a",
            "GooProducer": "#a88",
            "AutoScribe": "#8a8",
        }

        if toProduce in colorMap2_1:
            display = [
                (src.interaction.urwid.AttrSpec(colorMap2_1[toProduce], "black"), "X"),
                (src.interaction.urwid.AttrSpec(colorMap2_2[toProduce], "black"), "\\"),
            ]
        self.display = display

    def setToProduce(self, toProduce):
        """
        set what type of item the machine should produe

        Parameters:
            toProduce: the type of items to produce
        """

        self.toProduce = toProduce
        self.setDescription()
        self.resetDisplay()

    def apply(self, character):
        """
        handle a character trying to use this machine to produce an item

        Parameters:
            character: the character trying to produce an item
        """


        if not self.container:
            character.addMessage("this machine has to be placed to be used")
            return

        character.changed("operated machine",{"character":character,"machine":self})

        if not self.bolted:
            character.addMessage(
                "this machine need to be bolted down to be used."
                )
            return

        if not self.checkCoolDownEnded():
            character.addMessage(
                "cooldown not reached. Wait {} ticks".format(self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer))
            )
            self.runCommand("cooldown", character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        targetFull = self.checkTargetFull()
        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            self.runCommand("targetFull", character)
            color = "#740"
            if self.container.getItemByPosition((self.xPosition + 1, self.yPosition, self.zPosition))[0].type != self.toProduce:
                color = "#f00"
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"][")})
            return

        (resourcesNeeded,resourcesFound) = self.checkForInput()
        # refuse production without resources
        if resourcesNeeded:
            character.addMessage(
                "missing resources (place left/west or up/north or down/south):\n%s"
                % (", ".join(resourcesNeeded))
            )
            self.runCommand("material %s" % (resourcesNeeded[0]), character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        # remove resources
        for item in resourcesFound:
            self.container.addAnimation(item.getPosition(),"showchar",2,{"char":"--"})
            self.container.addAnimation(item.getPosition(),"showchar",1,{"char":item.render()})
            self.container.removeItem(item)

        self.container.addAnimation(self.getPosition(),"charsequence",2,{"chars":[
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"X\\"),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"X|"),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"X/"),
           ]})

        # spawn new item
        new = src.items.itemMap[self.toProduce]()
        new.bolted = False
        character.addMessage(f"you produce a {self.toProduce}")

        if hasattr(new, "coolDown"):
            new.coolDown = round(
                new.coolDown * (1 - (0.05 * (self.productionLevel - 1)))
            )

            new.coolDown = random.randint(new.coolDown, int(new.coolDown * 1.25))

        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))
        self.container.addAnimation(new.getPosition(),"showchar",2,{"char":"++"})
        character.changed("producedItem", {"item":new})

        if hasattr(new, "level"):
            new.level = self.level

        #HACK: sound effect
        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("machineUsed","machines")
        self.runCommand("success", character)

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Parameters:
            the description text
        """

        coolDownLeft = self.coolDown - (
            src.gamestate.gamestate.tick - self.coolDownTimer
        )

        text = f"""
This machine produces items of the type: {self.toProduce}

After using this machine you need to wait {self.coolDown} ticks till you can use this machine again.

this is a level {self.level} item and will produce level {self.level} items.

"""

        if coolDownLeft > 0:
            text += f"""
Currently you need to wait {coolDownLeft} ticks to use this machine again.

"""
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

""" % (
                self.charges
            )
        else:
            text += """
Currently the machine has no charges

"""

        return text

    # abstraction: use super class function
    def configure_disabled(self, character):
        """
        handle a character trying to do a configuration action
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        self.submenue = src.interaction.OneKeystrokeMenu(
                "what do you want to do?\n\nc: add command\nj: run job order\nb: bolt/unbolt"
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    # abstraction: use super class function
    def apply2(self):
        """
        handle a character having selected a configuraion option
        by running the action
        """

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
                for (commandName, command) in task["commands"].items():
                    self.commands[commandName] = command

        elif self.submenue.keyPressed == "b":
            if self.bolted:
                self.bolted = False
                self.character.addMessage("You bolt down the machine to the floor")
                self.character.changed("boltedItem",{"character":self.character,"item":self})
            else:
                self.bolted = True
                self.character.addMessage("You unbolt the machine")
                self.character.changed("unboltedItem",{"character":self.character,"item":self})
        elif self.submenue.keyPressed == "c":
            options = []
            options.append(("success", "set success command"))
            options.append(("cooldown", "set cooldown command"))
            options.append(("targetFull", "set target full command"))

            if self.toProduce in rawMaterialLookup:
                resourcesNeeded = rawMaterialLookup[self.toProduce][:]
            else:
                resourcesNeeded = ["MetalBars"]

            for itemType in resourcesNeeded:
                options.append(
                    (
                        f"material {itemType}",
                        f"set {itemType} fetching command",
                    )
                )
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    # abstraction: use super class functionality
    def setCommand(self):
        """
        set a command to run in certain situations
        """

        itemType = self.submenue.selection

        commandItem = None
        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition - 1, self.zPosition)
        ):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage(
            f"added command for {itemType} - {commandItem.command}"
        )
        return

    # abstraction: use super class functionality
    def runCommand(self, trigger, character):
        """
        run a preconfigured command

        Parameters:
            trigger (string): indicator for what command to run
            character: the character to run the command on
        """

        if trigger not in self.commands:
            return

        command = self.commands[trigger]

        character.runCommandString(command)

        character.addMessage(
            f"running command to handle trigger {trigger} - {command}"
        )

    def checkCoolDownEnded(self):
        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            return False
        return True

    def checkTargetFull(self):
        targetFull = False
        new = src.items.itemMap[self.toProduce]()

        itemList = self.container.getItemByPosition(
            (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        if itemList:
            if new.walkable:
                if (
                    len(
                        self.container.getItemByPosition(
                            (self.xPosition + 1, self.yPosition, self.zPosition)
                        )
                    )
                    > 0
                ):
                    targetFull = True
                for item in self.container.getItemByPosition(
                    (self.xPosition + 1, self.yPosition, self.zPosition)
                ):
                    if item.walkable == False:
                        targetFull = True
            else:
                if (
                    len(
                        self.container.getItemByPosition(
                            (self.xPosition + 1, self.yPosition, self.zPosition)
                        )
                    )
                    > 0
                ):
                    targetFull = True
        return targetFull

    def checkForInput(self):

        if self.toProduce in src.items.rawMaterialLookup:
            resourcesNeeded = src.items.rawMaterialLookup[self.toProduce][:]
        else:
            resourcesNeeded = ["MetalBars"]

        resourcesFound = []
        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition, self.zPosition)
        ):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)

        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition-1, self.zPosition)
        ):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)

        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition+1, self.zPosition)
        ):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)

        return (resourcesNeeded,resourcesFound)


    def readyToUse(self):
        if not self.container:
            return False

        if not self.bolted:
            return False

        if not self.checkCoolDownEnded():
            return False

        targetFull = self.checkTargetFull()
        if targetFull:
            return False

        (resourcesNeeded,resourcesFound) = self.checkForInput()
        if resourcesNeeded:
            return False

        return True


    def render(self):
        if self.readyToUse():
            return "X\\"
        else:
            return self.display

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

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Machine")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Machine")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Machine)
