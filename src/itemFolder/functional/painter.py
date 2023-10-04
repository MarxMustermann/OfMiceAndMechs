import copy
import json

import src


class Painter(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "Painter"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__(src.canvas.displayChars.markerBean_inactive)
        self.walkable = True
        self.bolted = False
        self.name = "painter"
        self.description = """
A painter. it can be used to draw markers on the floor
"""
        self.usageInfo = """
"""
        self.paintMode = "inputSlot"
        self.paintType = "Scrap"
        self.paintExtraInfo = {}

        self.offset = (0,0,0)

    def getUsageInformation(self):
        return """
Place the Painter on the floor and activate it to draw.

You can control what types of markers are drawn by configuring it.

It can be configured to draw
* inputStockpiles
* outputStockpiles
* storageStockpiles
* walkingSpaces
or to remove markings.

For stockpiles the item type that the stockpile applies to can be set.
For example a storageStockpile with the type Scrap will store Scrap.

More complex parameters can be set as extra parameters.

You also can set the direction for the Painter.
This will paint the marker next to the Painter.
This should be used in cases where you can not place the Painter on the position the marker should be drawn.
"""

    def render(self):
        """
        render the marker as animation if active

        Returns:
            how the item should currently be rendered
        """
        if self.paintMode == "inputSlot":
            return "xi"
        if self.paintMode == "outputSlot":
            return "xo"
        if self.paintMode == "storageSlot":
            return "xs"
        if self.paintMode == "walkingSpace":
            return "xw"
        if self.paintMode == "buildSite":
            return "xb"
        if self.paintMode == "delete":
            return "xd"
        return "x?"

    def configure(self, character):
        submenue = src.interaction.OneKeystrokeMenu(
               "what do you want to do?\n\nm: set painting mode\nt: set type\ne: set extra info\nc: clear extra info\nd: set direction"
                                       )
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"configure2","params":{"character":character}}
        character.runCommandString("~",nativeKey=True)

    def configure2(self,extraInfo):
        character = extraInfo["character"]
        keyPressed = extraInfo["keyPressed"]

        if keyPressed == "c":
            self.paintExtraInfo = {}
            return

        if keyPressed == "d":
           submenue = src.interaction.InputMenu(
               "type in the direction to set\n\n"+
               "(w,a,s,d)"
               )
           character.macroState["submenue"] = submenue
           character.macroState["submenue"].followUp = {"container":self,"method":"setDirection","params":{"character":character}}
           return

        if keyPressed == "m":
           submenue = src.interaction.InputMenu(
               "type in the mode you want to set\n\n"+
               "inputSlot, outputSlot, storageSlot, walkingSpace, buildSite, delete (i,o,s,w,b,d)"
               )
           submenue.tag = "paintModeSelection"
           character.macroState["submenue"] = submenue
           character.macroState["submenue"].followUp = {"container":self,"method":"setMode","params":{"character":character}}
           return

        if keyPressed == "t":
           submenue = src.interaction.InputMenu(
               "type in the type you want to set"
                                       )
           character.macroState["submenue"] = submenue
           submenue.tag = "paintTypeSelection"
           character.macroState["submenue"].followUp = {"container":self,"method":"setType","params":{"character":character}}
           return

        if keyPressed == "e":
           submenue = src.interaction.InputMenu(
               "type in the name of the extra parameter you want to set",
               targetParamName="name",
                                       )
           character.macroState["submenue"] = submenue
           submenue.tag = "paintExtraParamName"
           submenue.extraInfo["item"] = self
           character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo2","params":{"character":character}}
           return

    def addExtraInfo1(self,extraInfo):
        character = extraInfo["character"]
        submenue = src.interaction.InputMenu(
               "type in the type of the extra parameter you want to set (empty for string)",
               targetParamName="type",
                                       )
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo2","params":extraInfo}
        return

    def addExtraInfo2(self,extraInfo):
        character = extraInfo["character"]

        submenue = src.interaction.InputMenu(
               "type in the value of the extra parameter you want to set",
               targetParamName="value",
                                       )

        character.macroState["submenue"] = submenue
        submenue.tag = "paintExtraParamValue"
        submenue.extraInfo["item"] = self
        character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo3","params":extraInfo}
        return

    def addExtraInfo3(self,extraInfo):
        extraInfo["type"] = None
        value = extraInfo["value"]
        if extraInfo["type"] in ("int","integer"):
            value = int(value)
        if extraInfo["type"] in ("json",):
            value = json.loads(value)
        self.paintExtraInfo[extraInfo["name"]] = value

    def setDirection(self,extraInfo):
        mode = extraInfo.get("text")
        offset = (0,0,0)
        if mode == "w":
            offset = (0,-1,0)
        if mode == "s":
            offset = (0,1,0)
        if mode == "a":
            offset = (-1,0,0)
        if mode == "d":
            offset = (1,0,0)
        self.offset = offset
        extraInfo["character"].addMessage(f"you set the offset to {self.offset}")

    def setMode(self,extraInfo):
        character = extraInfo["character"]

        mode = extraInfo.get("text")
        if mode == "i":
            mode = "inputSlot"
        if mode == "o":
            mode = "outputSlot"
        if mode == "s":
            mode = "storageSlot"
        if mode == "w":
            mode = "walkingSpace"
        if mode == "b":
            mode = "buildSite"
        if mode == "d":
            mode = "delete"
        self.paintMode = mode

        character.addMessage(f"you set the mode to {self.paintMode}")

    def setType(self,extraInfo):
        if extraInfo.get("text") in ("","None",None):
            self.paintType = None
        else:
            self.paintType = extraInfo["text"]
        extraInfo["character"].addMessage(f"you set the type to {self.paintType}")

    def apply(self, character):
        """
        activate the marker bean

        Parameters:
            character: the character activating the marker bean
        """

        super().apply(character)
        if isinstance(character.container,src.rooms.Room):

            room = character.container
            pos = character.getPosition(offset=self.offset)

            # delete old marking
            if pos in room.walkingSpace:
                room.walkingSpace.remove(pos)
            for inputSlot in room.inputSlots[:]:
                if inputSlot[0] == pos:
                    room.inputSlots.remove(inputSlot)
            for outputSlot in room.outputSlots[:]:
                if outputSlot[0] == pos:
                    room.outputSlots.remove(outputSlot)
            for storageSlot in room.storageSlots[:]:
                if storageSlot[0] == pos:
                    room.storageSlots.remove(storageSlot)
            for buildSite in room.buildSites[:]:
                if buildSite[0] == pos:
                    room.buildSites.remove(buildSite)

            if self.paintMode == "delete":
                character.changed("deleted marking",{})

            if self.paintMode == "inputSlot":
                room.addInputSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan and room.floorPlan.get("inputSlots"):
                    for inputSlot in room.floorPlan.get("inputSlots")[:]:
                        if inputSlot[0] == pos:
                            room.floorPlan["inputSlots"].remove(inputSlot)
                            break
                if not "resource fetching" in room.requiredDuties:
                    room.requiredDuties.append("resource fetching")
                if self.paintType == "Scrap":
                    room.requiredDuties.append("resource gathering")
                character.changed("drew marking",{})
            if self.paintMode == "outputSlot":
                room.addOutputSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan and room.floorPlan.get("outputSlots"):
                    for outputSlot in room.floorPlan.get("outputSlots")[:]:
                        if outputSlot[0] == pos:
                            room.floorPlan["outputSlots"].remove(outputSlot)
                            break
                character.changed("drew marking",{})
            if self.paintMode == "storageSlot":
                room.addStorageSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan and room.floorPlan.get("storageSlots"):
                    for storageSlot in room.floorPlan.get("storageSlots")[:]:
                        if storageSlot[0] == pos:
                            room.floorPlan["storageSlots"].remove(storageSlot)
                            break
                character.changed("drew marking",{})
            if self.paintMode == "walkingSpace":
                room.walkingSpace.add(character.getPosition(offset=self.offset))
                if room.floorPlan and room.floorPlan.get("walkingSpace"):
                    for walkingSpacePos in room.floorPlan.get("walkingSpace")[:]:
                        if walkingSpacePos == pos:
                            room.floorPlan["walkingSpace"].remove(walkingSpacePos)
                            break
                character.changed("drew marking",{})
            if self.paintMode == "buildSite":
                room.addBuildSite(character.getPosition(offset=self.offset),self.paintType, self.paintExtraInfo)
                if room.floorPlan:
                    for buildSite in room.floorPlan.get("buildSites")[:]:
                        if buildSite[0] == pos:
                            room.floorPlan["buildSites"].remove(buildSite)
                            break
                if not "machine placing" in room.requiredDuties:
                    room.requiredDuties.append("machine placing")
                character.changed("drew marking",{})

        self.paintExtraInfo = copy.copy(self.paintExtraInfo)
        character.container.addAnimation(self.getPosition(),"showchar",1,{"char":"::"})

        character.addMessage("you paint a marking on the floor")
        character.addMessage((self.paintMode,self.paintType,str(self.paintExtraInfo)))

    def getLongInfo(self):
        """
        generate simple text description

        Returns:
            the decription text
        """

        text = super().getLongInfo()
        text += f"""

mode: {self.paintMode}
type: {self.paintType}
extraInfo: {self.paintExtraInfo}
offset: {self.offset}
"""

        return text

src.items.addType(Painter)
