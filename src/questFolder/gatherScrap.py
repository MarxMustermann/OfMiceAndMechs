import src
import random

class GatherScrap(src.quests.MetaQuestSequence):
    type = "GatherScrap"

    def __init__(self, description="gather scrap", creator=None, targetPosition=None,lifetime=None,reason=None,amount=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.amount = amount

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

    def generateTextDescription(self):
        scrap1 = src.items.itemMap["Scrap"](amount=1)
        scrap2 = src.items.itemMap["Scrap"](amount=6)
        scrap3 = src.items.itemMap["Scrap"](amount=20)
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return ["""
Fill your inventory with scrap""",reason,""".
Scrap can be found in scrapfields and
looks like this: """,scrap1.render()," or ",scrap2.render()," or ",scrap3.render(),"""


Scrapfields are shown on the minimap as white ss"""]

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
        return super().setParameters(parameters)

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if self.completed:
            return

        if not character:
            return

        if not character.getFreeInventorySpace() < 1:
            return

        if character.inventory[-1].type != "Scrap":
            return

        self.postHandler()

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getNextStep(self,character=None,ignoreCommands=False):

        if self.subQuests:
            return (None,None)

        if character.getFreeInventorySpace() < 1:
            if character.inventory[-1].type != "Scrap":
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)

        room = character.container
        if not isinstance(room,src.rooms.Room):
            directions = [(0,0,0),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
            for direction in directions:
                items = character.container.getItemByPosition(character.getPosition(offset=direction))
                if items:
                    if items[0].type == "Scrap":
                        command = "k"
                        if direction == (1,0,0):
                            command = "Kd"
                        if direction == (-1,0,0):
                            command = "Ka"
                        if direction == (0,1,0):
                            command = "Ks"
                        if direction == (0,-1,0):
                            command = "Kw"

                        return (None,(command*min(10-len(character.inventory),items[0].amount),"pick up scrap"))

        foundScrap = None
        room = character.container
        if not isinstance(room,src.rooms.Room):
            # check for direct scrap
            toCheckFrom = [character.getPosition()]
            pathMap = {toCheckFrom[0]:[]}
            directions = [(-1,0),(1,0),(0,1),(0,-1)]
            while len(toCheckFrom):
                #random.shuffle(directions)
                pos = toCheckFrom.pop()
                for direction in directions:
                    foundScrap = None

                    oldPos = pos
                    newPos = (pos[0]+direction[0],pos[1]+direction[1],pos[2])
                    if newPos[0]%15 < 1 or newPos[0]%15 > 13 or newPos[1]%15 < 1 or newPos[1]%15 > 13:
                        continue

                    items = character.container.getItemByPosition(newPos)
                    if items:
                        if items[0].type == "Scrap":
                            foundScrap = (oldPos,newPos,direction)
                            break

                    if character.container.getPositionWalkable(newPos) and not newPos in pathMap:
                        toCheckFrom.append(newPos)
                        pathMap[newPos] = pathMap[oldPos]+[direction]
                if foundScrap:
                    break

        if not foundScrap:
            source = None
            if isinstance(room,src.rooms.Room):
                for potentialSource in random.sample(list(room.sources),len(room.sources)):
                    if potentialSource[1] == "rawScrap":
                        source = potentialSource
                        break

            if source == None and not character.getTerrain().scrapFields:
                self.fail(reason="no scrap source found")
                return (None,None)
            elif source == None:
                terrain = character.getTerrain()
                scrapFields = terrain.scrapFields[:]
                for scrapField in scrapFields[:]:
                    foundScrap = False
                    for item in terrain.itemsByBigCoordinate.get(scrapField,[]):
                        if item.type == "Scrap":
                            foundScrap = True
                            break
                    if not foundScrap:
                        scrapFields.remove(scrapField)

                if not scrapFields:
                    self.fail(reason="no scrap source")
                    return (None,None)

                targetPos = random.choice(scrapFields)
            else:
                targetPos = (source[0][0],source[0][1],0)

            quest = src.quests.questMap["GoToTile"](targetPosition=targetPos,description="go to scrap field",reason="go to scrap field")
            return ([quest],None)

        quest = src.quests.questMap["GoToPosition"](targetPosition=(foundScrap[1][0]%15,foundScrap[1][1]%15,0),description="go to scrap",reason="go to scrap",ignoreEndBlocked=True)
        return ([quest],None)

src.quests.addType(GatherScrap)
