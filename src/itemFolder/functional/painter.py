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
        self.paintModes = ["scrapin","walkingSpace","delete","buildSite"]
        self.paintIndex = 0
    
        # set up meta information for saving
        self.attributesToStore.extend(["activated"])

    def render(self):
        """
        render the marker as animation if active

        Returns:
            how the item should currently be rendered
        """
        return src.canvas.displayChars.markerBean_inactive

    def configure(self, character):
        self.paintIndex += 1
        if self.paintIndex >= len(self.paintModes):
            self.paintIndex = 0
        character.addMessage("set painter to: %s"%(self.paintModes[self.paintIndex],))

    def apply(self, character):
        """
        activate the marker bean

        Parameters:
            character: the character activating the marker bean
        """

        super().apply(character)
        if isinstance(character.container,src.rooms.Room):
            if self.paintModes[self.paintIndex] == "scrapin":
                character.container.addInputSlot(character.getPosition(),"Scrap")
            if self.paintModes[self.paintIndex] == "buildSite":
                character.container.addBuildSite(character.getPosition(),"ScrapCompactor")
            if self.paintModes[self.paintIndex] == "walkingSpace":
                character.container.walkingSpace.add(character.getPosition())
            if self.paintModes[self.paintIndex] == "delete":
                if character.getPosition() in character.container.walkingSpace:
                    character.container.walkingSpace.remove(character.getPosition())
                for inputSlot in character.container.inputSlots[:]:
                    if inputSlot[0] == character.getPosition():
                        character.container.inputSlots.remove(inputSlot)
                for outputSlot in character.container.outputSlots[:]:
                    if outputSlot[0] == character.getPosition():
                        character.container.outputSlots.remove(outputSlot)

        character.addMessage("you paint a marking on the floor")

src.items.addType(Painter)
