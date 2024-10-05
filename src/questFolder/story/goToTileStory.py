import src


class GoToTileStory(src.quests.questMap["GoToTile"]):
    type = "GoToTileStory"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,reason=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates, reason=reason)

    def generateTextDescription(self):
        command = ""

        reasonString = ""
        if self.reason:
            reasonString += ", to "+self.reason
        

        return [f"""
Go to the base entrance located on tile {self.targetPosition}{reasonString}.
Avoid fighting you are not equipped for it.
Enemies are shown with a red background.

Do not enter tiles with Spiders ("""+"SP"+"""), they can kill you easily.
You should be able to beat the Spiderlings ("""+"sp"+""") for some extra resources.

This quest is part of the quest to secure the base.

Press a to show the main quest again.
"""]

src.quests.addType(GoToTileStory)
