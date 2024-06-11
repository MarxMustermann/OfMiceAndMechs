import random

import src


class TriggerPlate(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "TriggerPlate"
    walkable = True
    name = "TriggerPlate"
    isStepOnActive = True
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.landmine)

        self.active = True
        self.target = None

    def toggleActive(self,character):
        if self.active:
            self.active = False
        else:
            self.active = True

    def doStepOnAction(self, character):
        if self.active:
            character.addMessage("you step on a trigger plate")
            self.trigger(character)

    def render(self):
        if self.active:
            return self.display
        else:
            return "_~"

    def trigger(self, character):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        if not self.target:
            return

        items = self.container.getItemByPosition(self.target)
        if not items:
            return

        items[0].remoteActivate()

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
        options["a"] = ("toggle active", self.toggleActive)
        options["t"] = ("configure target", self.configureTargetHook)
        return options

    def configureTargetHook(self,character):
        self.configureTarget({"character":character})

    def configureTarget(self,params):
        self.configureTargetPosition(params)

    def configureTargetPosition(self,params):
        key = params.get("keyPressed")
        if key:
            if key in ("enter","esc","lESC","rESC"):
                return
            if key == "w":
                self.target = (self.target[0],self.target[1]-1,0)
            if key == "a":
                self.target = (self.target[0]-1,self.target[1],0)
            if key == "s":
                self.target = (self.target[0],self.target[1]+1,0)
            if key == "d":
                self.target = (self.target[0]+1,self.target[1],0)

        character = params["character"]
        roomRender = self.container.render()

        if not self.target:
            self.target = self.getPosition()
        pos = self.target
        roomRender[pos[1]][pos[0]] = "XX"

        for line in roomRender:
            line.append("\n")

        submenue = src.interaction.OneKeystrokeMenu([roomRender,"\nselect the target position\npress wasd to move cursor"])
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"configureTargetPosition","params":params}

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(TriggerPlate)
