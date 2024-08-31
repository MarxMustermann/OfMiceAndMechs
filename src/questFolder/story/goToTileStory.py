import src


class GoToTileStory(src.quests.questMap["GoToTile"]):
    type = "GoToTileStory"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,reason=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates, reason=reason)

    def generateTextDescription(self):
        command = ""

        reasonString = ""
        if self.reason:
            reasonString += ", to"+self.reason
        

        return [f"""
Go to the base entrance located on tile {self.targetPosition}{reasonString}.
Avoid fighting with the insects, you are not equipped for it.

The insects are shown as: """,(src.interaction.urwid.AttrSpec("#fff", "#f00"), "<-"),"""
Enemies are shown with a red background. The insects are 

This quest is part of the quest to reach the base.
This quest ends and the main quest will take back control when you do that.

Press a to move the quest cursor back to the main quest
"""]

src.quests.addType(GoToTileStory)
