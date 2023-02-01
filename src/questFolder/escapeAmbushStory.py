import src

class EscapeAmbushStory(src.quests.questMap["GoToTile"]):
    type = "EscapeAmbushStory"

    def __init__(self, description="go to tile", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        super().__init__(description=description, creator=creator, lifetime=lifetime, targetPosition=targetPosition, paranoid=paranoid, showCoordinates=showCoordinates)
        self.direction = direction

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        enemyDirection = " the south and east"
        if self.character.getBigPosition()[1] == 13:
            enemyDirection = " the east"
        return ["""
You reach out to your implant and it answers.
It whispers, but you understand clearly:


This room is not a safe place to stay.
Enemies are on their way to hunt you down.
They look like [- and come from """+enemyDirection+""".

So get moving and leave this room.
Use the wasd movement keys to move.
Pass through the door (""",door.render(),""") in the """+self.direction+""". 



Right now you are looking at the quest menu.
Detailed instructions and explainations are shown here.
For now ignore the options below and press esc to continue.

"""]

    def triggerCompletionCheck(self,character=None):
        if not character:
            return
        if isinstance(character.container,src.rooms.Room):
            return False
        self.postHandler()

src.quests.addType(EscapeAmbushStory)
