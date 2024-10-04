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
        self.targets = []
        self.faction = None

    def toggleActive(self,character):
        if self.active:
            self.active = False
        else:
            self.active = True

    def doStepOnAction(self, character):
        if self.active:
            self.trigger(character)

    def render(self):
        if self.active and self.faction != src.gamestate.gamestate.mainChar.faction:
            return self.display
        else:
            return "_~"

    def apply(self, character):
        self.trigger(character,checkFaction=False)

    def trigger(self, character, checkFaction=True):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """

        print(self.faction)
        print(character.faction)
        if checkFaction and self.faction == character.faction:
            return

        items = self.container.getItemByPosition(self.getPosition())
        if not (items[0] == self):
            return

        character.addMessage("you step on a trigger plate")

        try:
            self.targets
        except:
            self.targets = []

        if not self.targets:
            return

        for target in self.targets:
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"tt"})
            self.container.addAnimation(target,"showchar",1,{"char":"TT"})

            items = self.container.getItemByPosition(target)
            if not items:
                return

            try:
                items[0].remoteActivate
            except:
                return
            items[0].remoteActivate(extraParams={"pos":self.getPosition()})

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        self.faction = character.faction
        print(self.faction)

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        options["a"] = ("toggle active", self.toggleActive)
        options["t"] = ("configure targets", self.configureTargetHook)
        return options

    def configureTargetHook(self,character):
        self.configureTarget({"character":character})

    def configureTarget(self,params):
        self.configureTargetPosition(params)

    def configureTargetPosition(self,params):
        try:
            self.targets
        except:
            self.targets = []

        if not "cursor" in params:
            params["cursor"] = self.getPosition()
        cursor = params["cursor"]

        key = params.get("keyPressed")
        if key:
            if key in ("esc","lESC","rESC"):
                return
            if key in ("j","k","enter"):
                if cursor in self.targets:
                    self.targets.remove(cursor)
                else:
                    self.targets.append(cursor)
            if key == "w":
                cursor = (cursor[0],cursor[1]-1,0)
                params["cursor"] = cursor
            if key == "a":
                cursor = (cursor[0]-1,cursor[1],0)
                params["cursor"] = cursor
            if key == "s":
                cursor = (cursor[0],cursor[1]+1,0)
                params["cursor"] = cursor
            if key == "d":
                cursor = (cursor[0]+1,cursor[1],0)
                params["cursor"] = cursor

        character = params["character"]
        roomRender = self.container.render()

        roomRender[cursor[1]][cursor[0]] = "XX"

        for target in self.targets:
            roomRender[target[1]][target[0]] = "OO"

        for line in roomRender:
            line.append("\n")

        submenue = src.interaction.OneKeystrokeMenu([roomRender,"\nselect the target position\npress wasd to move cursor\npress j to add/remove target"])
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
