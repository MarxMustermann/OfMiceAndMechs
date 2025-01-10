import random

import src

class DropItemsOutside(src.quests.MetaQuestSequence):
    type = "DropItemsOutside"

    def __init__(self, description="drop items outside", creator=None, toCollect=None, lifetime=None, reason=None):
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
        text = """
Clear your inventory outside"""
        text += f"""{reason}."""
        text += """

This quest will end when your inventory is empty."""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not character.inventory:
            self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        if not character:
            return (None,None)

        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        # drop items
        if not terrain.getRoomByPosition(character.getBigPosition()):
            if not terrain.getItemByPosition(character.getPosition()) and not (character.getSpacePosition()[0] in (1,13) or character.getSpacePosition()[1] in (1,13)):
                return (None,("l","drop item"))
            # go somewhere else
            if random.random() > 0.2:
                pos = (random.randint(2,12),random.randint(2,12),0)
                quest = src.quests.questMap["GoToPosition"](targetPosition=pos,reason="move to a random point to drop items")
                return ([quest],None)

        # go somewhere else
        bigPos = (random.randint(2,12),random.randint(2,12),0)
        quest = src.quests.questMap["GoToTile"](targetPosition=bigPos,reason="move to a random tile to drop items")
        return ([quest],None)

        return (None,None)

        if not self.subQuests:
            terrain = character.getTerrain()


            for item in terrain.getNearbyItems(character):
                if self.toCollect and item.type != self.toCollect:
                    continue
                #if item.type == "Scrap":
                #    continue
                if item.bolted:
                    continue

                target = character.getBigPosition()

                centerItems = terrain.getItemByPosition((target[0]*15+7,target[1]*15+7,0))
                if centerItems and centerItems[0].type == "RoomBuilder":
                    continue

                if not (target not in terrain.scrapFields and target not in terrain.forests and not terrain.getRoomByPosition(target)):
                    continue
                if terrain.getRoomByPosition(target):
                    continue

                hasIdleSubordinate = False
                for subordinate in character.subordinates:
                    if len(subordinate.quests) < 2:
                        hasIdleSubordinate = True

                if hasIdleSubordinate:
                    return (None,("Hjsssssj","make subordinate scavenge"))
                else:
                    quest = src.quests.questMap["ScavengeTile"](targetPosition=target,toCollect=self.toCollect,reason="fill your inventory")
                    return ([quest],None)

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

                if not (target not in terrain.scrapFields and target not in terrain.forests and not terrain.getRoomByPosition(target)):
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
                    if self.toCollect and item.type != self.toCollect:
                        continue
                    #if item.type == "Scrap":
                    #    continue
                    if item.bolted:
                        continue

                    self.lastMoveDirection = offset
                    quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move to a scavenging spot")
                    return ([quest],None)

            for offset in offsets:

                target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
                if target[0] < 1 or target[0] > 13 or target[1] < 1 or target[1] > 13:
                    continue
                if not (target not in terrain.scrapFields and target not in terrain.forests and not terrain.getRoomByPosition(target)):
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
                quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items")
                return ([quest],None)


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
                quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items")
                return ([quest],None)


            bigPos = (random.randint(1,13),random.randint(1,13),0)
            quest = src.quests.questMap["GoToTile"](targetPosition=bigPos,reason="move to a random point to search for items")
            return ([quest],None)

        return (None,None)

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.droppedItem, "itemDropped")
        return super().assignToCharacter(character)

src.quests.addType(DropItemsOutside)
