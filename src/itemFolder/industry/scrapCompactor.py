import src

class ScrapCompactor(src.items.Item):
    """
    ingame item that converts scrapt to metal bars
    """

    type = "ScrapCompactor"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__()

        self.display = src.canvas.displayChars.scrapCompactor
        self.name = "scrap compactor"
        self.description = "This machine converts scrap into metal bars."

        self.coolDown = 10
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1
        self.commands = {}

    def readyToUse(self):
        if not self.container:
            return False

        if not self.bolted:
            return False

        if not self.checkCoolDownEnded():
            return False

        (targetFull,itemList) = self.checkTargetFull()
        if targetFull:
            return False

        scrap = self.checkForInputScrap()
        if not scrap:
            return False

        return True

    def render(self):
        if self.readyToUse():
            return "RC"
        else:
            return self.display

    def checkForInputScrap(self):

        # fetch input scrap
        scrap = None

        for item in self.container.getItemByPosition(
            (self.xPosition - 1, self.yPosition, self.zPosition)
        ):
            if item.type == "Scrap":
                scrap = item
                break
        if self.level > 1:
            if not scrap:
                for item in self.container.getItemByPosition(
                    (self.xPosition, self.yPosition + 1, self.zPosition)
                ):
                    if isinstance(item, itemMap["Scrap"]):
                        scrap = item
                        break
        if self.level > 2:
            if not scrap:
                for item in self.container.getItemByPosition(
                    (self.xPosition, self.yPosition - 1, self.zPosition)
                ):
                    if isinstance(item, itemMap["Scrap"]):
                        scrap = item
                        break
        return scrap

    def checkCoolDownEnded(self):
        tick = self.getTick()
        if (
            tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            return False
        return True

    def checkTargetFull(self):
        targetPos = (self.xPosition + 1, self.yPosition, self.zPosition)
        targetFull = False
        itemList = self.container.getItemByPosition(targetPos)

        #if len(itemList) > 15:
        if len(itemList) > 0:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True

        return (targetFull,itemList)

    def getTick(self):
        tick = src.gamestate.gamestate.tick
        if self.container and isinstance(self.container,src.rooms.Room):
            tick = self.container.timeIndex
        return tick

    def apply(self, character):
        """
        handle a character trying to use this item to produce a metal bar

        Parameters:
            character: the character trying to use the item
        """

        if not self.container:
            character.addMessage("this machine has be somewhere to be used")
            return

        character.changed("operated machine",{"character":character,"machine":self})

        if not self.bolted:
            character.addMessage(
                "this machine needs to be bolted down to be used"
            )
            return

        tick = self.getTick()

        if not self.checkCoolDownEnded():
            character.addMessage(
                f"cooldown not reached. Wait {self.coolDown - (tick - self.coolDownTimer)} ticks"
            )
            self.runCommand("cooldown", character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            return

        (targetFull,itemList) = self.checkTargetFull()
        if targetFull:
            character.addMessage(
                "the target area is full, the machine can not produce anything"
            )
            self.runCommand("targetFull", character)
            color = "#740"
            if not itemList[0].type == "MetalBars":
                color = "#f00"
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec(color, "black"),"][")})
            return

        scrap = self.checkForInputScrap()
        if not scrap:
            character.addMessage("no scraps available")
            self.runCommand("material Scrap", character)
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = tick

        character.addMessage("you produce a metal bar")

        # remove resources
        if scrap.amount <= 1:
            self.container.removeItem(scrap)
        else:
            scrap.amount -= 1
            scrap.setWalkable()
        self.container.addAnimation(scrap.getPosition(),"scrapChange",2,{})

        self.container.addAnimation(self.getPosition(),"charsequence",2,{"chars":[
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"R["),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"R-"),
            (src.interaction.urwid.AttrSpec("#aaa", "black"),"RK"),
           ]})

        # spawn the metal bar
        new = src.items.itemMap["MetalBars"]()
        self.container.addItem(
            new, (self.xPosition + 1, self.yPosition, self.zPosition)
        )
        self.container.addAnimation(new.getPosition(),"showchar",2,{"char":"++"})
        character.changed("producedItem", {"item":new})

        #HACK: sound effect
        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("scrapcompactorUsed","machines")
        self.runCommand("success", character)

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
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
           a longer than normal description text 
        """

        text = super().getLongInfo()

        directions = "west"
        if self.level > 1:
            directions += "/south"
        if self.level > 2:
            directions += "/north"
        text += f"""
Place scrap to the {directions} of the machine and activate it 

After using this machine you need to wait {self.coolDown} ticks till you can use this machine again.
"""

        tick = src.gamestate.gamestate.tick
        if self.container and isinstance(self.container,src.rooms.Room):
            tick = self.container.timeIndex
        coolDownLeft = self.coolDown - (
            tick - self.coolDownTimer
        )
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

        text += """
thie is a level %s item

""" % (
            self.level
        )
        return text

    def configure_disabled(self, character):
        """
        handle a character trying to configure the machine
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        options = [("addCommand", "add command")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2_disabled(self):
        if self.submenue.selection == "runCommand":
            options = []
            for itemType in self.commands:
                options.append((itemType, itemType))
            self.submenue = src.interaction.SelectionMenu(
                "Run command for producing item. select item to produce.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.runCommand
        elif self.submenue.selection == "addCommand":
            options = []
            options.append(("success", "set success command"))
            options.append(("cooldown", "set cooldown command"))
            options.append(("targetFull", "set target full command"))
            options.append(("material Scrap", "set Scrap fetching command"))
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        """
        set a command to be run in certain situations
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

src.items.addType(ScrapCompactor)
