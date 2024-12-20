import src


class SharpenPersonalSword(src.quests.MetaQuestSequence):
    type = "SharpenPersonalSword"

    def __init__(self, description="sharpen personal sword", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"

    def handleSwordSharpened(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleSwordSharpened, "sharpened sword")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue

                if not items[0].type == "SwordSharpener":
                    continue
                
                if offset == (0,0,0):
                    return (None,("jjj","sharpen personal sword"))
                if offset == (1,0,0):
                    return (None,("Jdjj","sharpen personal sword"))
                if offset == (-1,0,0):
                    return (None,("Jajj","sharpen personal sword"))
                if offset == (0,1,0):
                    return (None,("Jsjj","sharpen personal sword"))
                if offset == (0,-1,0):
                    return (None,("Jwjj","sharpen personal sword"))


            for item in character.container.itemsOnFloor:
                if not item.type == "SwordSharpener":
                    continue
                if not item.bolted:
                    continue

                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to SwordSharpener",ignoreEndBlocked=True)
                    return ([quest],None)

        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "SwordSharpener":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a SwordSharpener")
                return ([quest],None)

        return (None,None)

src.quests.addType(SharpenPersonalSword)
