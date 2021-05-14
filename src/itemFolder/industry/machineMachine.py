import src

"""
"""


class MachineMachine(src.items.Item):
    type = "MachineMachine"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        self.coolDown = 1000
        self.coolDownTimer = -self.coolDown
        self.charges = 3
        self.level = 1

        self.endProducts = {}
        self.blueprintLevels = {}

        super().__init__(display=src.canvas.displayChars.machineMachine)
        self.name = "machine machine"

        self.attributesToStore.extend(
            ["coolDown", "coolDownTimer", "endProducts", "charges", "level"]
        )

    """
    trigger production of a player selected item
    """

    def apply(self, character, resultType=None):
        super().apply(character, silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        options = []
        options.append(("blueprint", "load blueprint"))
        options.append(("produce", "produce machine"))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.basicSwitch
        self.character = character

    def configure(self, character):
        options = [("addCommand", "add command")]
        self.submenue = src.interaction.OneKeystrokeMenu(
            "what do you want to do?\n\nc: add command\nj: run job order"
        )
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
        if (self.xPosition, self.yPosition - 1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[
                (self.xPosition, self.yPosition - 1)
            ]:
                if item.type in ["BluePrint"]:
                    blueprintFound = item
                    break

        if not blueprintFound:
            self.character.addMessage("no blueprint found above/north")
            return

        self.endProducts[blueprintFound.endProduct] = blueprintFound.endProduct
        if blueprintFound.endProduct not in self.blueprintLevels:
            self.blueprintLevels[blueprintFound.endProduct] = 0
        if self.blueprintLevels[blueprintFound.endProduct] < blueprintFound.level:
            self.blueprintLevels[blueprintFound.endProduct] = blueprintFound.level

        self.character.addMessage(
            "blueprint for " + blueprintFound.endProduct + " inserted"
        )
        self.room.removeItem(blueprintFound)

    def productionSwitch(self):

        if self.endProducts == {}:
            self.character.addMessage("no blueprints available.")
            return

        if (
            src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
            and not self.charges
        ):
            self.character.addMessage(
                "cooldown not reached. Wait %s ticks"
                % (self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer),)
            )
            return

        options = []
        for itemType in self.endProducts:
            options.append((itemType, itemType + " machine"))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.produceSelection

    """
    trigger production of the selected item
    """

    def produceSelection(self):
        self.produce(self.submenue.selection)

    """
    produce an item
    """

    def produce(self, itemType, resultType=None):

        if not self.container:
            if self.room:
                self.container = self.room
            elif self.terrain:
                self.container = self.terrain

        # gather a metal bar
        resourcesNeeded = ["MetalBars"]

        resourcesFound = []
        if (self.xPosition - 1, self.yPosition) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[
                (self.xPosition - 1, self.yPosition)
            ]:
                if item.type in resourcesNeeded:
                    resourcesFound.append(item)
                    resourcesNeeded.remove(item.type)

        # refuse production without resources
        if resourcesNeeded:
            self.character.addMessage(
                "missing resources: %s" % (",".join(resourcesNeeded))
            )
            return

        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.room.itemByCoordinates:
            if (
                len(self.room.itemByCoordinates[(self.xPosition + 1, self.yPosition)])
                > 0
            ):
                targetFull = True

        if targetFull:
            self.character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return
        else:
            self.character.addMessage("not full")

        if self.charges:
            self.charges -= 1
        else:
            self.coolDownTimer = src.gamestate.gamestate.tick

        self.character.addMessage(
            "you produce a machine that produces %s" % (itemType,)
        )

        # remove resources
        for item in resourcesFound:
            self.room.removeItem(item)

        # spawn new item
        new = Machine(creator=self)
        new.productionLevel = self.blueprintLevels[itemType]
        new.setToProduce(itemType)
        new.xPosition = self.xPosition + 1
        new.yPosition = self.yPosition
        new.bolted = False

        if hasattr(new, "coolDown"):
            new.coolDown = random.randint(new.coolDown, int(new.coolDown * 1.25))

        self.room.addItems([new])

    def getState(self):
        state = super().getState()
        state["endProducts"] = self.endProducts
        state["blueprintLevels"] = self.blueprintLevels
        return state

    def setState(self, state):
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
""" % (
            self.coolDown,
        )

        coolDownLeft = self.coolDown - (
            src.gamestate.gamestate.tick - self.coolDownTimer
        )
        if coolDownLeft > 0:
            text += """
Currently you need to wait %s ticks to use this machine again.

""" % (
                coolDownLeft,
            )
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
