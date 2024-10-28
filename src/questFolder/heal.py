import src
import random

class Heal(src.quests.MetaQuestSequence):
    type = "Heal"

    def __init__(self, description="heal"):
        super().__init__()
        self.metaDescription = description

    def generateTextDescription(self):
        text = """
You are hurt. Heal yourself.

You can heal yourself using vials.
Use vials to heal yourself.
Press JH to auto heal.

"""
        return text

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # heal using vials
        foundVial = None
        for item in character.inventory:
            if item.type == "Vial" and item.uses > 0:
                foundVial = item
        if foundVial:
            return (None,("JH","drink from vial"))

        # heal using coal burners
        terrain = character.getTerrain()
        rooms = terrain.rooms[:]
        if character.container.isRoom:
            rooms.insert(0,character.container)
        for room in rooms:
            items = room.getItemsByType("CoalBurner",needsBolted=True)
            foundBurners = []
            for item in items:
                if not item.getMoldFeed(character):
                    continue
                foundBurners.append(item)

            if not foundBurners:
                continue

            if not character.container == room:
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                return ([quest],None)

            for item in foundBurners:
                direction = None
                if character.getPosition(offset=(1,0,0)) == item.getPosition():
                    direction = "d"
                if character.getPosition(offset=(-1,0,0)) == item.getPosition():
                    direction = "a"
                if character.getPosition(offset=(0,1,0)) == item.getPosition():
                    direction = "s"
                if character.getPosition(offset=(0,-1,0)) == item.getPosition():
                    direction = "w"

                if direction:
                    return (None,("J"+direction,"inhale smoke"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=random.choice(foundBurners).getPosition(),ignoreEndBlocked=True)
            return ([quest],None)

        if character.container.isRoom and character.container.tag == "temple":
            return (None,("..........","wait to heal"))

        for room in rooms:
            if room.tag == "temple":
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                return ([quest],None)

        self.fail("no way to heal")
        return (None,None)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.health < character.maxHealth:
            return False

        self.postHandler()
        return True


    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "healed")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return
    
        self.triggerCompletionCheck(self.character)

src.quests.addType(Heal)
