import random

import src


class Scavenge(src.quests.MetaQuestSequence):
    '''
    quest to collect items from the outside on a terrain
    '''
    type = "Scavenge"
    def __init__(self, description="scavenge", creator=None, toCollect=None, lifetime=None, reason=None, ignoreAlarm=False, tryHard=False, ignoreScrap=False, amountToCollect=None):
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
        self.tryHard = tryHard
        self.ignoreScrap = ignoreScrap
        self.amountToCollect = amountToCollect

    def generateTextDescription(self):
        '''
        generate a text description of the quest to be shown on the UI
        '''
        out = []

        reason = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reason = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f",")," to {self.reason}."]
        text = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""
Scavenge the outside area""")]
        if self.toCollect:
            text.append((src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f" for {self.toCollect}"))
        text.append(reason)
        text.append("""

This quest will end when your inventory is full.""")

        if self.amountToCollect:
            text.append(f"\nCollect {self.amountToCollect} more items")

        if self.doneTiles:

            text.append(f"""\n\ncompleted spots:\n""")
            rawMap = []
            for y in range(15):
                rawMap.append([])
                for x in range(15):
                    if x == 0 or y == 0 or x == 14 or y == 14:
                        rawMap[y].append("~~")
                    else:
                        rawMap[y].append("  ")
                rawMap[y].append("\n")
            for pos in self.doneTiles:
                rawMap[pos[1]][pos[0]] = "XX"
            if self.character:
                rawMap[self.character.getBigPosition()[1]][self.character.getBigPosition()[0]] = "@@"
            text.append("\n")
            text.append(rawMap)
            text.append("\n")

        return text

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
        if character.getTerrain().alarm and not self.tryHard and not self.ignoreAlarm:
            return self._solver_trigger_fail(dryRun,"alarm")

        # scavenge all item on the current tile
        terrain = character.getTerrain()
        for item in terrain.getNearbyItems(character):

            # filter for appropriate items
            if self.toCollect and item.type != self.toCollect:
                continue
            if self.ignoreScrap and item.type == "Scrap":
                continue
            if item.bolted:
                continue

            # do not rescavange spots
            target = character.getBigPosition()
            if target in self.doneTiles:
                continue

            # do not scavange special spot
            centerItems = terrain.getItemByPosition((target[0]*15+7,target[1]*15+7,0))
            if centerItems and centerItems[0].type == "RoomBuilder":
                continue
            if not (target not in terrain.scrapFields and target not in terrain.forests and not terrain.getRoomByPosition(target)):
                continue
            if terrain.getRoomByPosition(target):
                continue

            # create the actual scavanging quest
            hasIdleSubordinate = False
            for subordinate in character.subordinates:
                if len(subordinate.quests) < 2:
                    hasIdleSubordinate = True
            if hasIdleSubordinate:
                return (None,("Hjsssssj","make subordinate scavenge"))
            else:
                quest = src.quests.questMap["ScavengeTile"](targetPositionBig=target,toCollect=self.toCollect,reason="fill your inventory",ignoreAlarm=self.ignoreAlarm,tryHard=self.tryHard,ignoreScrap=self.ignoreScrap)
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

        # collect candidates to visit
        target_candidates = []
        pos = character.getBigPosition()
        for offset in offsets:
            target_candidates.append((pos[0]+offset[0],pos[1]+offset[1],pos[2]+offset[2]))
        x_values = list(range(1,14))
        random.shuffle(x_values)
        y_values = list(range(1,14))
        random.shuffle(y_values)
        for x in x_values:
            for y in y_values:
                target_candidates.append((x,y,0))

        # visit unvisited tiles
        for target in target_candidates:

            # filter invalid targets
            if target in self.doneTiles:
                continue
            if target[0] < 1 or target[0] > 13 or target[1] < 1 or target[1] > 13:
                continue
            if not (target not in terrain.scrapFields and target not in terrain.forests and not terrain.getRoomByPosition(target)):
                continue
            if terrain.getRoomByPosition(target):
                continue
            centerItems = terrain.getItemByPosition((target[0]*15+7,target[1]*15+7,0))
            if centerItems and centerItems[0].type == "RoomBuilder":
                continue

            # avoid enemies
            foundEnemy = False
            for otherCharacter in terrain.charactersByTile.get(target,[]):
                if otherCharacter.faction == character.faction:
                    continue
                foundEnemy = True
            if foundEnemy:
                continue

            # go to tile if valuable loot was found
            for item in terrain.itemsByBigCoordinate.get(target,[]):
                if self.toCollect and item.type != self.toCollect:
                    continue
                if item.bolted:
                    continue

                self.lastMoveDirection = offset
                quest = src.quests.questMap["GoToTile"](targetPosition=target,reason="move to the next scavenging spot",paranoid=True)
                return ([quest],None)

        # fail because nothing is left to scavenge
        return self._solver_trigger_fail(dryRun,"nothing left to scavenge")

    def pickedUpItem(self,extraInfo):
        '''
        check for completion when picking up stuff
        '''
        if self.amountToCollect:
            if extraInfo[1].type == self.toCollect:
                self.amountToCollect -= 1
            if self.amountToCollect < 1:
                self.postHandler()
                return
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
                    if self.ignoreScrap and item.type == "Scrap":
                        continue
                    result.append((item.getPosition(),"target"))

        return result
    
    @staticmethod
    def generateDutyQuest(beUsefull,character,room, dryRun):
        '''
        generate the quests for the scavenging duty
        '''

        # ste up helper variables
        terrain = character.getTerrain()

        # do nothing on alarms
        if terrain.alarm:
            return (None,None)

        # leave some storage available
        freeStorageSpace = 0
        for room in terrain.rooms:
            freeStorageSpace += len(room.getEmptyInputslots(forceGenericStorage=True))
        if freeStorageSpace < 12:
            return (None,None)

        # scavenge collection spots
        terrain = character.getTerrain()
        while terrain.collectionSpots:
            if not terrain.itemsByBigCoordinate.get(terrain.collectionSpots[-1]):
                terrain.collectionSpots.pop()
                continue
            quests = []
            if not character.getFreeInventorySpace():
                quests.append(src.quests.questMap["ClearInventory"]())
            quests.append(src.quests.questMap["ScavengeTile"](targetPositionBig=(terrain.collectionSpots[-1]),lifetime=1000))
            if not dryRun:
                beUsefull.idleCounter = 0
            return (reversed(quests),None)

        # go scavenging
        quests = []
        if not character.getFreeInventorySpace():
            quests.append(src.quests.questMap["ClearInventory"]())
        quests.append(src.quests.questMap["Scavenge"](lifetime=1000))
        if not dryRun:
            beUsefull.idleCounter = 0
        return (reversed(quests),None)

# register the quest type
src.quests.addType(Scavenge)
