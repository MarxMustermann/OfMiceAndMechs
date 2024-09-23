import src


class Ascend(src.quests.MetaQuestSequenceV2):
    type = "Ascend"

    def __init__(self, description="ascend", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleAscended(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleAscended, "ascended")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

You obtained all GlassHearts and fully control the GlassStatues now.
But you are under constant attack by your enemies.
They envy your status and try to steal it from you.

Show your enemies who rules this world by stepping to the throne and taking the crown.
This will permanently bond the GlassHearts and your enemies will see reason.
Rule the world and put an end to those attacks!
"""]
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.rank != 1:
            return False

        self.postHandler()

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break

        if not throne:
            if not dryRun:
                self.fail("no throne")
            return (None,None)

        if character.container != throne.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=throne.container.getPosition(),reason="get to the temple", description="go to temple")
            return ([quest],None)

        pos = character.getPosition()
        targetPosition = throne.getPosition()
        if targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=targetPosition,ignoreEndBlocked=True,reason="get near the throne", description="go to throne")
            return ([quest],None)

        if (pos[0],pos[1],pos[2]) == targetPosition:
            return (None,("j","activate the Throne"))
        if (pos[0]-1,pos[1],pos[2]) == targetPosition:
            return (None,("Ja","activate the Throne"))
        if (pos[0]+1,pos[1],pos[2]) == targetPosition:
            return (None,("Jd","activate the Throne"))
        if (pos[0],pos[1]-1,pos[2]) == targetPosition:
            return (None,("Jw","activate the Throne"))
        if (pos[0],pos[1]+1,pos[2]) == targetPosition:
            return (None,("Js","activate the Throne"))
        return None


src.quests.addType(Ascend)
