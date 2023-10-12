import src

# equip
# rest

class DelveDungeon(src.quests.MetaQuestSequence):
    type = "DelveDungeon"

    def __init__(self, description="delve dungeon",targetTerrain=None,itemID=None,storyText=None):
        questList = []
        super().__init__(questList, creator=None)
        self.metaDescription = description
        self.targetTerrain = targetTerrain
        self.itemID = itemID
        self.storyText = storyText

    def generateTextDescription(self):
        text = ""

        if self.storyText:
            text += f"""
{self.storyText}
"""
        text += f"Delve the dungeon on tile {self.targetTerrain}."

        if self.itemID:
            text += f"""
Fetch the glass heart of god {self.itemID}
"""
        else:
            text += """
Fetch any glass heart.
"""
        text += """
After fetching the glass heart return the glass heart to your base and set it into the glass statue.
"""
        return text

    def handleDelivery(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleDelivery, "deliveredSpecialItem")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        hasSpecialItem = None
        for item in character.inventory:
            if item.type != "SpecialItem":
                continue
            hasSpecialItem = item

        terrain = character.getTerrain()

        if not hasSpecialItem:
            if terrain.xPosition != self.targetTerrain[0] or terrain.yPosition != self.targetTerrain[1]:
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=(self.targetTerrain[0],self.targetTerrain[1],0))
                return ([quest],None)
            if character.health < character.maxHealth//5 and character.getNearbyEnemies():
                quest = src.quests.questMap["Flee"]()
                return ([quest],None)
            if character.health < character.maxHealth*0.75:
                if character.getNearbyEnemies():
                    quest = src.quests.questMap["Fight"]()
                    return ([quest],None)
                #if character.health > character.maxHealth*0.5 and character.health < character.maxHealth:
                #    return (None,("..............","wait to heal"))
                if not dryRun:
                    self.fail("too hurt")
                return (None,None)

            foundGlassHeart = None
            for room in terrain.rooms:
                for specialItem in room.getItemsByType("SpecialItem"):
                    if self.itemID and specialItem.itemID != self.itemID:
                        continue
                    foundGlassHeart = specialItem

            if not foundGlassHeart:
                foundGlassStatue = None
                for room in terrain.rooms:
                    for glassStatue in room.getItemsByType("GlassStatue"):
                        if not glassStatue.hasItem:
                            continue
                        if self.itemID and glassStatue.itemID != self.itemID:
                            continue
                        foundGlassStatue = glassStatue

                if foundGlassStatue:
                    if character.container != foundGlassStatue.container:
                        quest = src.quests.questMap["GoToTile"](targetPosition=foundGlassStatue.getBigPosition(),abortHealthPercentage=0.75)
                        return ([quest],None)

                    if character.getDistance(foundGlassStatue.getPosition()) > 1:
                        quest = src.quests.questMap["GoToPosition"](targetPosition=foundGlassStatue.getPosition(),ignoreEndBlocked=True)
                        return ([quest],None)

                    directionCommand = None
                    if character.getPosition(offset=(0,0,0)) == foundGlassStatue.getPosition():
                        directionCommand = "."
                    if character.getPosition(offset=(1,0,0)) == foundGlassStatue.getPosition():
                        directionCommand = "d"
                    if character.getPosition(offset=(0,1,0)) == foundGlassStatue.getPosition():
                        directionCommand = "s"
                    if character.getPosition(offset=(-1,0,0)) == foundGlassStatue.getPosition():
                        directionCommand = "a"
                    if character.getPosition(offset=(0,-1,0)) == foundGlassStatue.getPosition():
                        directionCommand = "w"
                    return (None,(directionCommand+"cg","get special item"))

                if not dryRun:
                    self.fail("no glassStatue found")
                return (None,None)

            if character.getPosition() != foundGlassHeart.getPosition():
                quest = src.quests.questMap["GoToPosition"](targetPosition=foundGlassHeart.getPosition())
                return ([quest],None)
            return (None,("k","pick up special item"))

        if terrain.xPosition != character.registers["HOMETx"] or terrain.yPosition != character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"](reason="go to your home territory")
            return ([quest],None)

        if not character.container.isRoom:
            quest = src.quests.questMap["GoHome"](reason="get into a room")
            return ([quest],None)

        foundGlassStatue = None
        for room in [character.container, *terrain.rooms]:
            for glassStatue in room.getItemsByType("GlassStatue"):
                if glassStatue.itemID == hasSpecialItem.itemID:
                    foundGlassStatue = glassStatue
                    break
            if foundGlassStatue:
                break

        if not foundGlassStatue:
            self.fail(reason="no glass statues found")
            return (None,None)

        if foundGlassStatue.container != character.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=foundGlassStatue.getBigPosition())
            return ([quest],None)

        if character.getDistance(glassStatue.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=glassStatue.getPosition(),ignoreEndBlocked=True)
            return ([quest],None)
        directionCommand = None
        if character.getPosition(offset=(0,0,0)) == glassStatue.getPosition():
            directionCommand = "."
        if character.getPosition(offset=(1,0,0)) == glassStatue.getPosition():
            directionCommand = "d"
        if character.getPosition(offset=(0,1,0)) == glassStatue.getPosition():
            directionCommand = "s"
        if character.getPosition(offset=(-1,0,0)) == glassStatue.getPosition():
            directionCommand = "a"
        if character.getPosition(offset=(0,-1,0)) == glassStatue.getPosition():
            directionCommand = "w"
        return (None,(directionCommand+"cg","insert glass heart"))

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(DelveDungeon)
