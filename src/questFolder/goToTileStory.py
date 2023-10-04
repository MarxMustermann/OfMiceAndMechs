import src


class GoToTileStory(src.quests.questMap["GoToTile"]):
    type = "GoToTileStory"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True, direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        command = ""
        if self.direction == "south":
            command = "s"
        if self.direction == "north":
            command = "w"
        if self.direction == "west":
            command = "a"
        if self.direction == "east":
            command = "d"

        item1 = src.items.itemMap["Scrap"](amount=6)
        item2 = src.items.itemMap["LandMine"]()
        return ["""
Go one tile to the """+self.direction+""".
The quest ends when you do that.
This quest is part of the quest to reach the base.

Avoid fighting with the enemies, you are not equipped for it.
Also avoid running into obstacles (""",item1.render(),""")
and try not to step on the land mines (""",item2.render(),""").


The playing field is divided into tiles by the blue borders.
You can pass from tile to tile using the pathway in the middle.
So go to the """+self.direction+""" side of this tile and press """+command+""" to switch tile.

Those suggested action on how to do this are shown during normal gameplay on the left.
Following that suggestion should avoid the obstacles and most landmines.
The suggestion doesn't avoid enemies and might even run into them.
So use the suggested keystrokes as orientation and don't follow them blindly.



Press a to move the quest cursor back to the main quest
"""%(self.getSolvingCommandString(self.character))]

src.quests.addType(GoToTileStory)
