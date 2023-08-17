import src
import random

class Scavenge(src.quests.MetaQuestSequence):
    type = "Scavenge"

    def __init__(self, description="scavenge", creator=None, toCollect=None, lifetime=None, reason=None):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        text = """
Scvange the outside area"""
        if self.toCollect:
            text += " for %s"%(self.toCollect,)
        text += """%s."""%(reason,)
        text += """

This quest will end when your inventory is full."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not character.getFreeInventorySpace():
            self.postHandler()
            return True
        return False

    def solver(self, character):
        try:
            self.lastMoveDirection
        except:
            self.lastMoveDirection = None

        if self.triggerCompletionCheck(character=character):
            return

        if not self.subQuests:
            terrain = character.getTerrain()

            
            for item in terrain.getNearbyItems(character):
                if self.toCollect and not item.type == self.toCollect:
                    continue
                #if item.type == "Scrap":
                #    continue
                if item.bolted:
                    continue

                target = character.getBigPosition()

                centerItems = terrain.getItemByPosition((target[0]*15+7,target[1]*15+7,0))
                if centerItems and centerItems[0].type == "RoomBuilder":
                    continue

                if not (not target in terrain.scrapFields and not target in terrain.forests and not terrain.getRoomByPosition(target)):
                    continue
                if terrain.getRoomByPosition(target):
                    continue

                self.addQuest(src.quests.questMap["ScavengeTile"](targetPosition=target,toCollect=self.toCollect,reason="fill your inventory"))
                return

            offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]

            if self.lastMoveDirection:
                offsets.append(self.lastMoveDirection)
                offsets.append(self.lastMoveDirection)
                offsets.append(self.lastMoveDirection)
                offsets.append(self.lastMoveDirection)

            random.shuffle(offsets)

            pos = character.getBigPosition()

            for offset in offsets:

                target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
                if target[0] < 1 or target[0] > 13 or target[1] < 1 or target[1] > 13:   
                    continue

                if not (not target in terrain.scrapFields and not target in terrain.forests and not terrain.getRoomByPosition(target)):
                    continue
                if terrain.getRoomByPosition(target):
                    continue

                foundEnemy = False
                for otherCharacter in terrain.charactersByTile.get(target,[]):
                    if otherCharacter.faction == character.faction: 
                        continue
                    foundEnemy = True
                if foundEnemy:
                    continue

                centerItems = terrain.getItemByPosition((target[0]*15+7,target[1]*15+7,0))
                if centerItems and centerItems[0].type == "RoomBuilder":
                    continue

                for item in terrain.itemsByBigCoordinate.get(target,[]):
                    if self.toCollect and not item.type == self.toCollect:
                        continue
                    #if item.type == "Scrap":
                    #    continue
                    if item.bolted:
                        continue

                    self.lastMoveDirection = offset
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=target,reason="move to a scavanging spot"))
                    return

            for offset in offsets:

                target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
                if target[0] < 1 or target[0] > 13 or target[1] < 1 or target[1] > 13:   
                    continue
                if not (not target in terrain.scrapFields and not target in terrain.forests and not terrain.getRoomByPosition(target)):
                    continue
                if terrain.getRoomByPosition(target):
                    continue

                foundEnemy = False
                for otherCharacter in terrain.charactersByTile.get(target,[]):
                    if otherCharacter.faction == character.faction: 
                        continue
                    foundEnemy = True
                if foundEnemy:
                    continue


                self.lastMoveDirection = offset
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items"))
                return

            for offset in offsets:
                target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
                if terrain.getRoomByPosition(target):
                    continue

                foundEnemy = False
                for otherCharacter in terrain.charactersByTile.get(target,[]):
                    if otherCharacter.faction == character.faction: 
                        continue
                    foundEnemy = True
                if foundEnemy:
                    continue

                self.lastMoveDirection = offset
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items"))
                return

        super().solver(character)

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)

        if renderForTile:
            terrain = character.getTerrain()

            for offset in ((0,0,0),(-1,0,0),(1,0,0),(0,-1,0),(0,1,0)):
                pos = character.getBigPosition()
                pos = (pos[0]+offset[0],pos[1]+offset[1],0)

                centerItems = terrain.getItemByPosition((pos[0]*15+7,pos[1]*15+7,0))
                if centerItems and centerItems[0].type == "RoomBuilder":
                    continue

                if pos in terrain.forests:
                    continue
                if pos in terrain.scrapFields or (pos[0],pos[1]) in terrain.scrapFields:
                    continue
                if terrain.getRoomByPosition(pos):
                    continue

                for item in character.getTerrain().itemsByBigCoordinate.get((pos[0],pos[1],0),[]):
                    if self.toCollect and not item.type == self.toCollect:
                        continue
                    result.append((item.getPosition(),"target"))

        return result

src.quests.addType(Scavenge)
