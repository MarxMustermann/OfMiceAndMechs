import src
import copy
import json

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

        self.character = None
        self.submenue = None
    
        # set up meta information for saving
        self.attributesToStore.extend(["activated"])
        self.objectsToStore.append("character")
        self.objectsToStore.append("submenue")

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
       self.submenue = src.interaction.OneKeystrokeMenu(
               "what do you want to do?\n\nm: set painting mode\nt: set type\ne: set extra info\nc: clear extra info\nd: set direction"
                                       )
       character.macroState["submenue"] = self.submenue
       character.macroState["submenue"].followUp = self.configure2
       self.character = character

    def configure2(self):
        if self.submenue.keyPressed == "c":
            self.paintExtraInfo = {}
            return

        if self.submenue.keyPressed == "d":
           self.submenue = src.interaction.InputMenu(
               "type in the direction to set\n\n"+
               "(w,a,s,d)"
               )
           self.character.macroState["submenue"] = self.submenue
           self.character.macroState["submenue"].followUp = self.setDirection
           return

        if self.submenue.keyPressed == "m":
           self.submenue = src.interaction.InputMenu(
               "type in the mode you want to set\n\n"+
               "inputSlot, outputSlot, storageSlot, walkingSpace, buildSite, delete (i,o,s,w,b,d)"
               )
           self.character.macroState["submenue"] = self.submenue
           self.character.macroState["submenue"].followUp = self.setMode
           return

        if self.submenue.keyPressed == "t":
           self.submenue = src.interaction.InputMenu(
               "type in the type you want to set"
                                       )
           self.character.macroState["submenue"] = self.submenue
           self.character.macroState["submenue"].followUp = self.setType
           return

        if self.submenue.keyPressed == "e":
           self.submenue = src.interaction.InputMenu(
               "type in the name of the extra parameter you want to set",
               targetParamName="name",
                                       )
           self.character.macroState["submenue"] = self.submenue
           self.character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo2","params":{"character":self.character}}
           return

    def addExtraInfo1(self,extraInfo):
        self.submenue = src.interaction.InputMenu(
               "type in the type of the extra parameter you want to set (empty for string)",
               targetParamName="type",
                                       )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo2","params":extraInfo}
        return

    def addExtraInfo2(self,extraInfo):
        self.submenue = src.interaction.InputMenu(
               "type in the value of the extra parameter you want to set",
               targetParamName="value",
                                       )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = {"container":self,"method":"addExtraInfo3","params":extraInfo}
        return

    def addExtraInfo3(self,extraInfo):
        extraInfo["type"] = None
        value = extraInfo["value"]
        if extraInfo["type"] in ("int","integer"):
            value = int(value)
        if extraInfo["type"] in ("json",):
            value = json.loads(value)
        self.paintExtraInfo[extraInfo["name"]] = value

    def setDirection(self):
        mode = self.submenue.text
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
        self.character.addMessage("you set the offset to %s"%(self.offset,))

    def setMode(self):
        mode = self.submenue.text
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
        self.character.addMessage("you set the mode to %s"%(self.paintMode,))

    def setType(self):
        if self.submenue.text in ("","None"):
            self.paintType = None
        else:
            self.paintType = self.submenue.text
        self.character.addMessage("you set the type to %s"%(self.paintType,))

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
            if self.paintMode == "inputSlot":
                room.addInputSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan:
                    for inputSlot in room.floorPlan.get("inputSlots")[:]:
                        if inputSlot[0] == pos:
                            room.floorPlan["inputSlots"].remove(inputSlot)
                            break
                if not "resource fetching" in room.requiredDuties:
                    room.requiredDuties.append("resource fetching")
                if self.paintType == "Scrap":
                    room.requiredDuties.append("resource gathering")
            if self.paintMode == "outputSlot":
                room.addOutputSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan:
                    for outputSlot in room.floorPlan.get("outputSlots")[:]:
                        if outputSlot[0] == pos:
                            room.floorPlan["outputSlots"].remove(outputSlot)
                            break
            if self.paintMode == "storageSlot":
                room.addStorageSlot(pos,self.paintType,self.paintExtraInfo)
                if room.floorPlan:
                    for storageSlot in room.floorPlan.get("storageSlots")[:]:
                        if storageSlot[0] == pos:
                            room.floorPlan["storageSlots"].remove(storageSlot)
                            break
            if self.paintMode == "walkingSpace":
                room.walkingSpace.add(character.getPosition(offset=self.offset))
                if room.floorPlan:
                    for walkingSpacePos in room.floorPlan.get("walkingSpace")[:]:
                        if walkingSpacePos == pos:
                            room.floorPlan["walkingSpace"].remove(walkingSpacePos)
                            break
            if self.paintMode == "buildSite":
                room.addBuildSite(character.getPosition(offset=self.offset),self.paintType, self.paintExtraInfo)
                if room.floorPlan:
                    for buildSite in room.floorPlan.get("buildSites")[:]:
                        if buildSite[0] == pos:
                            room.floorPlan["buildSites"].remove(buildSite)
                            break
                if not "machine placing" in room.requiredDuties:
                    room.requiredDuties.append("machine placing")
            if self.paintMode == "delete":
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

        self.paintExtraInfo = copy.copy(self.paintExtraInfo)
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"::"})

        character.addMessage("you paint a marking on the floor")
        character.addMessage((self.paintMode,self.paintType,str(self.paintExtraInfo)))

    def getLongInfo(self):
        """
        generate simple text description

        Returns:
            the decription text
        """

        text = super().getLongInfo()
        text += """

mode: %s
type: %s
extraInfo: %s
offset: %s
""" % (
            self.paintMode,self.paintType,self.paintExtraInfo,self.offset
        )

        return text

src.items.addType(Painter)
