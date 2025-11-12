import random

import src


class Scavenge(src.quests.MetaQuestSequence):
    '''
    quest to collect items from the outside on a terrain
    '''
    type = "Scavenge"
    def __init__(self, description="scavenge", creator=None, toCollect=None, lifetime=None, reason=None, ignoreAlarm=False):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect
        self.doneTiles = []
        self.ignoreAlarm = ignoreAlarm

    def generateTextDescription(self):
        '''
        generate a text description of the quest to be shown on the UI
        '''
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = """
Scavenge the outside area"""
        if self.toCollect:
            text += f" for {self.toCollect}"
        text += f"""{reason}."""
        text += """

This quest will end when your inventory is full."""

        if self.doneTiles:
            text += f"""

done tiles: {self.doneTiles}"""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end if the quest is completed
        '''
        if not character:
            return False
        if not character.getFreeInventorySpace():
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        '''
        calculate the next logical step towards solving the quest
        '''

        # wait for subquest to complete
        if self.subQuests:
            return (None,None)

        # abort quest when there is an alarm
        self.tryHard = False
        if character.getTerrain().alarm and not self.tryHard and not self.ignoreAlarm:
            if not dryRun:
                self.fail("alarm")
            return (None,None)

        # scavenge all item on the current tile
        terrain = character.getTerrain()
        for item in terrain.getNearbyItems(character):
            if self.toCollect and item.type != self.toCollect:
                continue
            #if item.type == "Scrap":
            #    continue
            if item.bolted:
                continue

            target = character.getBigPosition()

            if target in self.doneTiles:
                continue

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
                quest = src.quests.questMap["ScavengeTile"](targetPosition=target,toCollect=self.toCollect,reason="fill your inventory",ignoreAlarm=self.ignoreAlarm)
                return ([quest],None)

        # mark current tile as completed
        if not dryRun:
            self.doneTiles.append(character.getBigPosition())

        # prepare a skewed list of directions to go in. Forward monumentum is preserved
        offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        if self.lastMoveDirection:
            offsets.append(self.lastMoveDirection)
            offsets.append(self.lastMoveDirection)
            offsets.append(self.lastMoveDirection)
            offsets.append(self.lastMoveDirection)
        random.shuffle(offsets)

        pos = character.getBigPosition()

        # check nearby scavenging spots
        for offset in offsets:

            target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])

            if target in self.doneTiles:
                continue

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
                if item.bolted:
                    continue

                self.lastMoveDirection = offset
                quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move to a scavenging spot",paranoid=True)
                return ([quest],None)

        # visit unvisited neighbours avoiding special areas
        for offset in offsets:

            target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])

            if target in self.doneTiles:
                continue

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

            self.lastMoveDirection = offset
            quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items",paranoid=True)
            return ([quest],None)

        # visit unvisited neighbours
        for offset in offsets:
            target = (pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2])
            if terrain.getRoomByPosition(target):
                continue

            if target in self.doneTiles:
                continue

            if target[0] < 1 or target[0] > 13 or target[1] < 1 or target[1] > 13:
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

            self.lastMoveDirection = offset
            quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move around to search for items",paranoid=True)
            return ([quest],None)

        # visit random spot
        bigPos = (random.randint(1,13),random.randint(1,13),0)
        quest = src.quests.questMap["GoToTile"](targetPosition=bigPos,reason="move to a random point to search for items",paranoid=True)
        return ([quest],None)

    def pickedUpItem(self,extraInfo):
        '''
        check for completion when picking up stuff
        '''
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def assignToCharacter(self, character):
        '''
        start watching for the character picking up stuff
        '''
        if self.character:
            return None

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        generate the quest markers on the smalest level
        '''
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
                    if item.bolted:
                        continue
                    if self.toCollect and item.type != self.toCollect:
                        continue
                    result.append((item.getPosition(),"target"))

        return result
    
    @staticmethod
    def generateDutyQuest(beUsefull,character,room, dryRun):
        '''
        generate the quests for the scavenging duty
        '''
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return (None,None)

        if not character.getFreeInventorySpace():
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([src.quests.questMap["ClearInventory"]()],None)

        terrain = character.getTerrain()
        while terrain.collectionSpots:
            if not terrain.itemsByBigCoordinate.get(terrain.collectionSpots[-1]):
                terrain.collectionSpots.pop()
                continue
            quest = src.quests.questMap["ScavengeTile"](targetPosition=(terrain.collectionSpots[-1]),lifetime=1000)
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([quest],None)

        freeStorageSpace = 0
        for room in terrain.rooms:
            freeStorageSpace += len(room.getEmptyInputslots(forceGenericStorage=True))
        if freeStorageSpace < 12:
            return (None,None)

        quest =  src.quests.questMap["Scavenge"](lifetime=1000)
        if not dryRun:
            beUsefull.idleCounter = 0
        return ([quest],None)

# register the quest type
src.quests.addType(Scavenge)
