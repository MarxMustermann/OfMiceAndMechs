import src
import random

class CleanSpace(src.quests.MetaQuestSequenceV2):
    type = "CleanSpace"

    def __init__(self, description="clean space", creator=None, targetPositionBig=None, targetPosition=None, reason=None, abortOnfullInventory=True):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason
        self.abortOnfullInventory = abortOnfullInventory

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Remove all items from the space {self.targetPosition} on tile {self.targetPositionBig}{reason}.
"""
        return text

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])


    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPositionBig)
        if rooms:
            room = rooms[0]
            items = room.getItemByPosition(self.targetPosition)
            if not items:
                self.postHandler()
                return True
        else:
            items = terrain.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))
            if not items:
                self.postHandler()
                return True
        return None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:
            terrain = character.getTerrain()
            rooms = terrain.getRoomByPosition(self.targetPositionBig)
            if not character.getFreeInventorySpace():
                if self.abortOnfullInventory:
                    if not dryRun:
                        self.fail("full inventory")
                    return (None,None)
                quest = src.quests.questMap["ClearInventory"](reason="be able to pick up more items")
                return ([quest],None)

            if character.getBigPosition() != self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get near the target tile")
                return ([quest], None)

            if rooms:
                room = rooms[0]
                items = room.getItemByPosition(self.targetPosition)
                if not items:
                    if not dryRun:
                        self.postHandler()
                    return (None,None)
            else:
                items = terrain.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))
                if not items:
                    if not dryRun:
                        self.postHandler()
                    return (None,None)

            if character.container.isRoom:
                if character.getDistance(self.targetPosition) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get to the target space")
                    return ([quest], None)
            else:
                if character.getDistance((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0)) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get to the target space")
                    return ([quest], None)

            offsets = {(0,0,0):".",(1,0,0):"d",(-1,0,0):"a",(0,1,0):"s",(0,-1,0):"w"}
            for (offset,direction) in offsets.items():
                if character.container.isRoom:
                    if character.getPosition(offset=offset) == self.targetPosition:
                        if items[0].bolted:
                            return (None, (direction+"cb","unbolt item"))
                        return (None, (direction+"k","pick up item"))
                else:
                    if character.getPosition(offset=offset) == (self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0):
                        return (None, ("K"+direction,"pick up item"))
        return (None,None)

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):
        if len(character.inventory):
            quest = src.quests.questMap["ClearInventory"]()
            beUsefull.addQuest(quest)
            beUsefull.idleCounter = 0
            return True

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            foundEnemy = False
            for otherChar in room.characters:
                if not otherChar.faction == character.faction:
                    foundEnemy = True
                    break
            if foundEnemy:
                continue

            if not room.floorPlan:
                for position in random.sample(list(room.walkingSpace),len(room.walkingSpace)):
                    items = room.getItemByPosition(position)

                    if not items:
                        continue
                    if items[0].bolted:
                        continue

                    if character.getFreeInventorySpace() <= 0:
                        quest = src.quests.questMap["ClearInventory"]()
                        beUsefull.addQuest(quest)
                        beUsefull.idleCounter = 0
                        return True

                    quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                    beUsefull.addQuest(quest)
                    quest.assignToCharacter(character)
                    quest.activate()
                    beUsefull.idleCounter = 0
                    return True

        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            foundEnemy = False
            for otherChar in room.characters:
                if not otherChar.faction == character:
                    foundEnemy = True
                    break
            if foundEnemy:
                continue

            slots = room.inputSlots+room.outputSlots+room.storageSlots
            random.shuffle(slots)
            for slot in slots:
                if not slot[1]:
                    continue
                items = room.getItemByPosition(slot[0])
                if not items:
                    continue

                misplacmentFound = False
                for item in items:
                    if not item.type == slot[1]:
                        misplacmentFound = True

                if not misplacmentFound:
                    continue

                beUsefull.addQuest(src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=slot[0]))
                beUsefull.idleCounter = 0
                return True

        return None
src.quests.addType(CleanSpace)
