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

        self.character = None
        self.submenue = None
    
        # set up meta information for saving
        self.attributesToStore.extend(["activated"])
        self.objectsToStore.append("character")
        self.objectsToStore.append("submenue")

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

    def configure(self, character):
       self.submenue = src.interaction.OneKeystrokeMenu(
               "what do you want to do?\n\nm: set painting mode\nt: set type\ne: set extra info\nc: clear extra info"
                                       )
       character.macroState["submenue"] = self.submenue
       character.macroState["submenue"].followUp = self.configure2
       self.character = character

    def configure2(self):
        if self.submenue.keyPressed == "c":
            self.paintExtraInfo = {}
            return

        if self.submenue.keyPressed == "m":
           self.submenue = src.interaction.InputMenu(
               "type in the mode you want to set"
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
           self.character.addMessage("NIY")
           return

    def setMode(self):
        self.paintMode = self.submenue.text
        self.character.addMessage("you set the mode to %s"%(self.paintMode,))

    def setType(self):
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
            if self.paintMode == "inputSlot":
                character.container.addInputSlot(character.getPosition(),self.paintType,self.paintExtraInfo)
            if self.paintMode == "outputSlot":
                character.container.addOutputSlot(character.getPosition(),self.paintType,self.paintExtraInfo)
            if self.paintMode == "storageSlot":
                character.container.addStorageSlot(character.getPosition(),self.paintType,self.paintExtraInfo)
            if self.paintMode == "walkingSpace":
                character.container.walkingSpace.add(character.getPosition())
            if self.paintMode == "buildSite":
                character.container.addBuildSite(character.getPosition(),self.paintType, self.paintExtraInfo)
            if self.paintMode == "delete":
                if character.getPosition() in character.container.walkingSpace:
                    character.container.walkingSpace.remove(character.getPosition())
                for inputSlot in character.container.inputSlots[:]:
                    if inputSlot[0] == character.getPosition():
                        character.container.inputSlots.remove(inputSlot)
                for outputSlot in character.container.outputSlots[:]:
                    if outputSlot[0] == character.getPosition():
                        character.container.outputSlots.remove(outputSlot)
                for storageSlot in character.container.outputSlots[:]:
                    if storageSlot[0] == character.getPosition():
                        character.container.storageSlots.remove(storageSlot)

        character.addMessage("you paint a marking on the floor")

src.items.addType(Painter)
