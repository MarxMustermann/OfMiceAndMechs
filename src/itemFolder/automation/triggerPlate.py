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
    description = "Triggers an action when stepped on"
    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.landmine)

        self.active = True
        self.targets = []
        self.faction = None
        self.coolDown = 10
        self.lastUsed = 0

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
            if not self.isInCoolDown():
                color = "#f00"
            else:
                color = "#600"
        else:
            if not self.isInCoolDown():
                color = "#aaa"
            else:
                color = "#666"
        return (src.interaction.urwid.AttrSpec(color, "black"), "_~")

    def isInCoolDown(self):
        if not (src.gamestate.gamestate.tick - self.lastUsed) > self.coolDown:
            return True
        else:
            return False

    def apply(self, character):
        character.macroState["submenue"] = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu("\npress j to confirm manually triggering the TriggerPlate",ignoreFirstKey=False,do_not_scale=True,tag="confirm_TriggerPlate")
        character.macroState["submenue"].followUp = {"container":self,"method":"activate","params":{"character":character}}

    def activate(self,extraParams):
        if extraParams["keyPressed"] != "j":
            return
        character = extraParams["character"]
        self.trigger(character,checkFaction=False)

    def trigger(self, character, checkFaction=True):
        """
        handle a character trying to use this item
        by starting to explode

        Parameters:
            character: the character trying to use the item
        """
        if not self.bolted:
            return

        if checkFaction and self.faction == character.faction:
            return

        items = self.container.getItemByPosition(self.getPosition())
        if not (items[0] == self):
            return

        character.addMessage("you step on a trigger plate")

        if self.isInCoolDown():
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "black"), "tt")]})
            return

        self.lastUsed = src.gamestate.gamestate.tick

        if not self.targets:
            return

        character.changed("triggered trigger plate",{})

        for target in self.targets:
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"tt"})
            self.container.addAnimation(target,"showchar",1,{"char":"TT"})

            items = self.container.getItemByPosition(target)
            if not items:
                continue

            try:
                items[0].remoteActivate
            except:
                continue
            items[0].remoteActivate(extraParams={"pos":self.getPosition()})

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
            if key == "w" and cursor[1] > 1:
                cursor = (cursor[0],cursor[1]-1,0)
                params["cursor"] = cursor
            if key == "a" and cursor[0] > 1:
                cursor = (cursor[0]-1,cursor[1],0)
                params["cursor"] = cursor
            if key == "s" and cursor[1] < 11:
                cursor = (cursor[0],cursor[1]+1,0)
                params["cursor"] = cursor
            if key == "d" and cursor[0] < 11:
                cursor = (cursor[0]+1,cursor[1],0)
                params["cursor"] = cursor

        character = params["character"]
        roomRender = self.container.render()

        roomRender[cursor[1]][cursor[0]] = "XX"

        for target in self.targets:
            display = "OO"
            if target == cursor:
                display = "oo"
            roomRender[target[1]][target[0]] = display

        for line in roomRender:
            line.append("\n")

        submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu([roomRender,"\nselect the target position\npress wasd to move cursor\npress j to add/remove target"])
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"configureTargetPosition","params":params}

    def getLongInfo(self, character=None):
        text = [super().getLongInfo(character)]

        if self.faction:
            faction_line.append(f"{self.faction}")
        else:
            faction_line.append("this item has not set a faction yet")
        faction_line.append("\n\n")
        text = faction_line + text
        return text

src.items.addType(TriggerPlate)
