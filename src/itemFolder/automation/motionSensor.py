import random

import src


class MotionSensor(src.items.Item):
    """
    """

    type = "MotionSensor"
    walkable = False
    name = "MotionSensor"
    bolted = False

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="MS")

        self.active = True
        self.target = None

    def toggleActive(self,character):
        if self.active:
            self.active = False
        else:
            self.active = True


    def apply(self,character):
        self.trigger(character)

    def trigger(self, character=None):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        if not self.target:
            if character:
                character.addMessage("no target set")
            return

        items = self.container.getItemByPosition(self.target)
        if not items:
            if character:
                character.addMessage("no items to trigger")
            return

        items[0].remoteActivate(extraParams={"pos":character.getPosition()})

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """
        self.faction = character.faction

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
            if key in ("j","k","enter","esc","lESC","rESC"):
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

        submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu([roomRender,"\nselect the target position\npress wasd to move cursor"])
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"configureTargetPosition","params":params}

    def motionDetected(self,extraParams):
        if extraParams["character"].faction == self.faction:
            return
        self.trigger(extraParams["character"])

    def boltAction(self,character):
        if self.bolted:
            return
        self.startWatching(self.container,self.motionDetected, "character moved")
        self.bolted = True
        if character:
            character.addMessage("you bolt down the Statue")
            character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        if not self.bolted:
            return
        self.stopWatching(self.container,self.motionDetected, "character moved")
        self.bolted = False
        if character:
            character.addMessage("you unbolt the Statue")
            character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(MotionSensor)
