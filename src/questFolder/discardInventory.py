import src
import random

class DiscardInventory(src.quests.MetaQuestSequence):
    type = "DiscardInventory"

    def __init__(self, description="discard inventory", returnToTile=True, reason=None,tryHard=False):
        questList = []
        super().__init__(questList)
        self.metaDescription = description
        self.returnToTile = False
        self.tryHard = tryHard
        self.reason = reason
        if returnToTile:
            self.setParameters({"returnToTile":returnToTile})

        self.tileToReturnTo = None

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason += ", to %s"%(self.reason,)
        text = """
Discard your inventory%s.

Just drop the content of your inventory somewhere, preferably outside.

To see your items open the your inventory by pressing i."""%(reason,)
        return text

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def handleTileChange(self):
        self.triggerCompletionCheck(self.character)

    def activate(self):
        if self.character:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = self.character.getBigPosition()
            self.triggerCompletionCheck(self.character)
        super().activate()

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.droppedItem, "dropped")
        self.startWatching(character,self.handleTileChange, "changedTile")

        if self.active:
            if self.returnToTile and not self.tileToReturnTo:
                self.tileToReturnTo = character.getBigPosition()
            self.triggerCompletionCheck(character)
        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not character.inventory:
            if self.returnToTile and not character.getBigPosition() == self.tileToReturnTo:
                return
            self.postHandler()
            return
        return

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getNextStep(self,character=None,ignoreCommands=False):
        if self.returnToTile and not self.tileToReturnTo:
            self.tileToReturnTo = character.getBigPosition()

        if not self.subQuests:
            if character.inventory:
                if not isinstance(character.container,src.rooms.Room):
                    if character.yPosition%15 == 14:
                        return (None,("w","enter tile"))
                    if character.yPosition%15 == 0:
                        return (None,("s","enter tile"))
                    if character.xPosition%15 == 14:
                        return (None,("a","enter tile"))
                    if character.xPosition%15 == 0:
                        return (None,("d","enter tile"))
                    
                if isinstance(character.container,src.rooms.Room):
                    terrain = character.getTerrain()
                    candidates = []
                    for rooms in terrain.rooms:
                        pos = rooms.getPosition()
                        candidates.append((pos[0]-1,pos[1],0))
                        candidates.append((pos[0]+1,pos[1],0))
                        candidates.append((pos[0],pos[1]-1,0))
                        candidates.append((pos[0],pos[1]+1,0))

                    for candidate in candidates[:]:
                        if ( (candidate[0],candidate[1]) in terrain.scrapFields or
                             (candidate[0],candidate[1],0) in terrain.scrapFields or
                             (candidate in terrain.forests) or
                             (terrain.getRoomByPosition(candidate)) or
                             terrain.getItemByPosition((candidate[0]*15+7,candidate[1]*15+7,0)) ):
                            candidates.remove(candidate)

                    pos = random.choice(candidates)
                    quest = src.quests.questMap["GoToTile"](targetPosition=pos,reason="go outside")
                    return ([quest],None)

                characterPos = character.getPosition()
                if (  characterPos[0]%15 in (1,7,13) or
                      characterPos[1]%15 in (1,7,13) or
                      character.container.getItemByPosition(characterPos)):
                    pos = (random.randint(2,12),random.randint(2,12))
                    quest = src.quests.questMap["GoToPosition"](targetPosition=pos,reason="go to a drop off position")
                    return ([quest],None)
                return (None,("l","drop item"))

            if self.returnToTile and not character.getBigPosition() == self.returnToTile:
                quest = src.quests.questMap["GoToTile"](description="return to tile",targetPosition=self.tileToReturnTo,reason="return to the tile this quest started on")
                return ([quest],None)

            8/0

        return (None,None)

    def setParameters(self,parameters):
        if "returnToTile" in parameters and "returnToTile" in parameters:
            self.returnToTile = parameters["returnToTile"]
        return super().setParameters(parameters)

src.quests.addType(DiscardInventory)
