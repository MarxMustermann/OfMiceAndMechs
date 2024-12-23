import src


class BrewPotion(src.quests.MetaQuestSequence):
    type = "BrewPotion"

    def __init__(self, description="brew potion", creator=None, lifetime=None, potionType=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"
        self.potionType = potionType

    def handleBrewedPotions(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleBrewedPotions, "brewed potion")
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

        if not character.searchInventory("Flask"):
            quest = src.quests.questMap["FetchItems"](toCollect="Flask",amount=1)
            return ([quest],None)

        if not character.searchInventory("ManaCrystal"):
            quest = src.quests.questMap["FetchItems"](toCollect="ManaCrystal",amount=1)
            return ([quest],None)

        if not character.searchInventory("Bloom"):
            quest = src.quests.questMap["FetchItems"](toCollect="Bloom",amount=1)
            return ([quest],None)

        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue

                if not items[0].type == "AlchemyTable":
                    continue
                
                message = "brewing a potion"
                command = list("jwj"+self.potionType)+["enter"]
                if offset == (0,0,0):
                    return (None,(list("j")+command,message))
                if offset == (1,0,0):
                    return (None,(list("Jd")+command,message))
                if offset == (-1,0,0):
                    return (None,(list("Ja")+command,message))
                if offset == (0,1,0):
                    return (None,(list("Js")+command,message))
                if offset == (0,-1,0):
                    return (None,(list("Jw")+command,message))


            for item in character.container.itemsOnFloor:
                if not item.type == "AlchemyTable":
                    continue
                if not item.bolted:
                    continue

                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to AlchemyTable",ignoreEndBlocked=True)
                    return ([quest],None)

        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "AlchemyTable":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a AlchemyTable")
                return ([quest],None)

        return (None,None)

    def generateTextDescription(self):
        text = [f"""
Brew a potion of the type {self.potionType}
"""]
        return text

    def handleQuestFailure(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(BrewPotion)
