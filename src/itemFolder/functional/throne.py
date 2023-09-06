import src
import copy
import json

class Throne(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "Throne"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__("TT")
        self.walkable = False
        self.bolted = False
        self.name = "throne"
        self.description = """
A throne. Use it to win the game.
"""

    def apply(self,character):
        hasAllSpecialItems = True
        currentTerrain = character.getTerrain()
        room = currentTerrain.getRoomByPosition((7,7,0))[0]
        for item in room.itemsOnFloor:
            if item.type == "SpecialItemSlot" and not item.hasItem:
                hasAllSpecialItems = False

        if not hasAllSpecialItems:
            character.addMessage("you need to control all special items")
            return

        if character == src.gamestate.gamestate.mainChar:
            text = """
You won the game and rule the world now. congratz.

I know the ending is cheap, but the game is a shadow of whait it should be.
I'm currently working on making this thing more fluid and hope to get tha actual game running.

I'd love to get feedback. Do not hestiate to contact me.

The game will continue to run, but there is not further content for you to see.

= press enter to continue =
"""
            src.interaction.showInterruptText(text)
src.items.addType(Throne)
