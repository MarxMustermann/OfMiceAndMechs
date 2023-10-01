import src

class InitialLeaveRoomStory(src.quests.questMap["GoToTile"]):
    type = "InitialLeaveRoomStory"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        return ["""
You reach out to your implant and it answers.
It whispers, but you understand clearly:

You are safe. You are in a farming complex.
Something is not right, though.
It looks freshly seeded, but the ghoul is not active.

You can not stay here forever, so start moving and leave this room.
Use the wasd movement keys to move.
Pass through the door (""",door.render(),""") in the """+self.direction+""".



Right now you are looking at the quest menu.
Detailed instructions are shown here.
For now ignore the options below and press esc to continue.

"""]

src.quests.addType(InitialLeaveRoomStory)
