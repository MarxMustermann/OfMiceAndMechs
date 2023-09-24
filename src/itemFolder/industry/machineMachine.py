import src
import random

class MachineMachine(src.items.Item):
    """
    ingame machine to produce machines that produce item
    requires blueprints for producing machines
    """

    type = "MachineMachine"

    def __init__(self):
        """
        set up interal state
        """

        self.coolDown = 1000
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1

        self.endProducts = {}
        self.blueprintLevels = {}
        self.lastProduced = None

        super().__init__(display=src.canvas.displayChars.machineMachine)
        self.name = "machine machine"
        self.description = "This machine produces machines that build machines. It needs blueprints to do that."
        self.usageInfo = """
You can load blueprints into this machine.
Prepare by placing a blueprint to the above/north of this machine.
After activation select "load blueprint" and the blueprint will be added.

You can produce machines for blueprints that were added.
Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm.
"""

    # abstraction: should use super class fuctionality
    def apply(self, character):
        """
        handle a character trying to use this item
        by offering a list of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        super().apply(character)

        options = []
        options.append(("blueprint", "load blueprint"))
        options.append(("produce", "produce machine"))
        if self.lastProduced:
            options.append(("repeat", "repeat last production"))
        submenue = src.interaction.SelectionMenu(
                "select the item to produce", options
        )
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"basicSwitch","params":{"character":character}}
        character.runCommandString("~",nativeKey=True)

    # abstraction: should use superclass functionality
    def configure(self, character):
        """
        handle a character trying to configure the item
        by offering a selection of configuration options

        Parameters:
            character: the character tryig to use the item
        """

        options = [("addCommand", "add command")]
        self.submenue = src.interaction.OneKeystrokeMenu(
            "what do you want to do?\n\nc: add command\nj: run job order"
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    # abstraction: should use superclass functionality
    def configure2(self):
        """
        handle a character having selected a configuration action
        by running the selected action
        """

        if self.submenue.keyPressed == "j":
            if not self.character.jobOrders:
                self.character.addMessage("no job order found")
                return

            jobOrder = self.character.jobOrders[-1]
            task = jobOrder.popTask()

            if task["task"] == "produce machine":
                self.produce(task["type"])

    # abstraction: should use superclass functionality
    def basicSwitch(self,extraInfo):
        """
        handle a character having seleted a activation action
        by running the selected action
        """
        character = extraInfo["character"]

        if not extraInfo.get("selection"):
            return

        selection = extraInfo["selection"]
        if selection == "blueprint":
            self.addBlueprint(character)
        elif selection == "produce":
            self.productionSwitch(character)
        elif selection == "repeat":
            self.repeatProduction(character)

    def readyToUse(self):
        if self.endProducts == {}:
            return False

        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            return False

        # gather a metal bar
        resourcesNeeded = ["MetalBars"]

        resourcesFound = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition,0)):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)

        # refuse production without resources
        if resourcesNeeded:
            return False

        targetFull = False
        if (self.xPosition + 1, self.yPosition,0) in self.container.itemByCoordinates:
            if (
                len(self.container.itemByCoordinates[(self.xPosition + 1, self.yPosition,0)])
                > 0
            ):
                targetFull = True

        if targetFull:
            return False
        return True

    def render(self):
        if self.readyToUse():
            return "M\\"
        else:
            return self.display

    def addBlueprint(self, character, blueprint=None):
        """
        try to load a blueprint into the machine
        """

        if not blueprint:
            blueprintFound = None
            if (self.xPosition, self.yPosition - 1,0) in self.container.itemByCoordinates:
                for item in self.container.itemByCoordinates[
                    (self.xPosition, self.yPosition - 1,0)
                ]:
                    if item.type in ["BluePrint"]:
                        blueprintFound = item
                        break

            if not blueprintFound:
                self.container.addAnimation(self.getPosition(offset=(0,0,0)),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
                self.container.addAnimation(self.getPosition(offset=(0,-1,0)),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
                character.addMessage("no blueprint found above/north")
                return
        else:
            blueprintFound = blueprint

        self.endProducts[blueprintFound.endProduct] = blueprintFound
        if blueprintFound.endProduct not in self.blueprintLevels:
            self.blueprintLevels[blueprintFound.endProduct] = 0
        if self.blueprintLevels[blueprintFound.endProduct] < blueprintFound.level:
            self.blueprintLevels[blueprintFound.endProduct] = blueprintFound.level

        if not blueprint:
            character.addMessage(
                "blueprint for " + blueprintFound.endProduct + " inserted"
            )
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"bb")})
            self.container.addAnimation(self.getPosition(offset=(0,-1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"--")})
            self.container.removeItem(blueprintFound)

    def repeatProduction(self,character):
        self.produce(character, self.lastProduced)

    def productionSwitch(self,character):
        """
        handle a character trying to produce a item
        by offering a selection of machines that can be produced
        """

        if self.endProducts == {}:
            character.addMessage("no blueprints available.")
            return

        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            character.addMessage(
                "cooldown not reached. Wait {} ticks".format(self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer))
            )
            return

        options = []
        for itemType in self.endProducts:
            options.append((itemType, itemType + " machine"))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        self.submenue.tag = "machineSelection"
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"produceSelection","params":{"character":character}}

    def produceSelection(self,extraInfo):
        """
        trigger production of a selected item
        """

        if not extraInfo.get("selection"):
            return

        self.produce(extraInfo["character"],extraInfo["selection"])

    def produce(self, character, itemType):
        """
        produce an item

        Parameters:
            ItemType: the typeof item that can be produced by the produced machine
        """

        self.lastProduced = itemType
        
        # gather a metal bar
        resourcesNeeded = ["MetalBars"]

        resourcesFound = []
        for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition,0)):
            if item.type in resourcesNeeded:
                resourcesFound.append(item)
                resourcesNeeded.remove(item.type)

        # refuse production without resources
        if resourcesNeeded:
            character.addMessage(
                "missing resources: %s" % (",".join(resourcesNeeded))
            )
            return

        targetFull = False
        if (self.xPosition + 1, self.yPosition,0) in self.container.itemByCoordinates:
            if (
                len(self.container.itemByCoordinates[(self.xPosition + 1, self.yPosition,0)])
                > 0
            ):
                targetFull = True

        if targetFull:
            self.container.addAnimation(self.getPosition(offset=(0,0,0)),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"M|")})
        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"M\\")})
        self.container.addAnimation(self.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"M|")})
        self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"--")})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"),"++")})
        character.addMessage(
            f"you produce a machine that produces {itemType}"
        )

        # remove resources
        for item in resourcesFound:
            self.container.removeItem(item)

        # spawn new item
        new = src.items.itemMap["Machine"]()
        new.productionLevel = self.blueprintLevels[itemType]
        new.setToProduce(itemType)
        new.bolted = False

        if hasattr(new, "coolDown"):
            new.coolDown = random.randint(new.coolDown, int(new.coolDown * 1.25))

        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))

    def getLongInfo(self):
        """
        shows a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += f"""
After using this machine you need to wait {self.coolDown} ticks till you can use this machine again.
"""

        coolDownLeft = self.coolDown - (
            src.gamestate.gamestate.tick - self.coolDownTimer
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

        if len(self.endProducts):
            text += """
This machine has blueprints for:

"""
            for itemType in self.endProducts:
                text += "* %s\n" % (itemType)
            text += "\n"
        else:
            text += """
This machine cannot produce anything since there were no blueprints added to the machine

"""
        return text


src.items.addType(MachineMachine)
