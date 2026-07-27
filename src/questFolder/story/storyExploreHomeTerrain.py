import src
import random
import itertools
import logging

logger = logging.getLogger(__name__)

class StoryExploreHomeTerrain(src.quests.MetaQuestSequence):
    type = "StoryExploreHomeTerrain"

    def __init__(self, description="explore ruined facility", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.reason = reason
        self.metaDescription = "explore ruined facility"
        self.donePointsOfInterest = []

    def getRemainingPointsOfInterests(self):
        result = []

        currentTerrain = self.character.getTerrain()

        for room in currentTerrain.rooms:
            if room.tag != "ruin":
                continue
            enemies = []
            for check_character in room.characters:
                if check_character == self.character:
                    continue
                enemies.append(check_character)
            
            if enemies:
                continue
            if not room.getItems(needsUnbolted=True):
                continue

            if room.getPosition() not in result and room.getPosition() not in self.donePointsOfInterest:
                result.append(room.getPosition())

        for donePoi in self.donePointsOfInterest:
            if not donePoi in result:
                continue
            result.remove(donePoi)

        return result

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        # ensure the quest actually completes
        if self.triggerCompletionCheck(dryRun=dryRun):
            return (None,("+","end quest"))

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # handle menu interaction
        if character.macroState["submenue"]:
            return (None, (["esc"], "exit menu"))

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](reason="eliminate threats")
            return ([quest],None)

        # set up helper variables
        currentTerrain = character.getTerrain()
        groundskeepers_place = None
        for room in currentTerrain.rooms:
            if room.tag != "the groundskeepers place":
                continue
            groundskeepers_place = room

        # equip weapon
        if not character.weapon:
            item = character.searchInventory("Rod")
            if item:
                quest = src.quests.questMap["ConsumeItem"](reason="arm yourself",itemType="Rod",consumeVerb="equip",description="equip rod")
                return ([quest],None)

        # equip weapon
        if not character.armor:
            item = character.searchInventory("Armor")
            if item:
                quest = src.quests.questMap["ConsumeItem"](reason="protect yourself",itemType="Armor",consumeVerb="equip",description="equip armor")
                return ([quest],None)

        # go home
        if not character.isOnHomeTerrain():
            quest = src.quests.questMap["GoHome"](reason="be able to explore the home terrain")
            return ([quest],None)

        # ensure inventory space
        if character.getFreeInventorySpace() <= 2:
            for room in character.getTerrain().rooms:
                if room.tag == "ruin":
                    continue
                hasStorage = False
                for storageSlot in room.storageSlots:
                    if storageSlot[1]:
                        continue
                    hasStorage = True
                if hasStorage:
                    quest = src.quests.questMap["ClearInventory"](reason="be able pick up loot")
                    return ([quest],None)


                pos = random.choice(list(room.walkingSpace))
                item = character.inventory[-1]
                quest = src.quests.questMap["PlaceItem"](
                                                targetPositionBig=groundskeepers_place.getPosition(),
                                                targetPosition=pos,
                                                reason="clear your inventory",
                                                description="drop item",
                                            )
                return ([quest],None)

        # loot current tile
        if character.container.isRoom:
            itemsOnFloor = character.container.itemsOnFloor
            if character.container.tag != "ruin":
                itemsOnFloor = []
        else:
            itemsOnFloor = character.container.getNearbyItems(character)
        for item in itemsOnFloor:
            if item.bolted or not item.walkable:
                continue
            if item.xPosition == None:
                logger.error("found ghost item")
                continue
            item_pos =item.getSmallPosition()
            if item_pos[0] == None:
                logger.error("found ghost item")
                continue
            if item_pos[0] > 12:
                continue
            if character.container.isRoom and (item_pos[0] > 11 or item_pos[1] > 11 or item_pos[0] < 1 or item_pos[1] < 1):
                continue

            if item.type in ("Scrap","MetalBars","MoldFeed"):
                continue

            if item.type in ("Bolt",) and character.getFreeInventorySpace() <= 1:
                continue

            invalidStack = False
            for stackedItem in character.container.getItemByPosition(item.getPosition()):
                if stackedItem == item:
                    break
                if not stackedItem.bolted:
                    continue
                invalidStack = True
            if invalidStack:
                continue

            quest = src.quests.questMap["LootRoom"](targetPositionBig=character.getBigPosition(),endWhenFull=True,reason="gain useful items",lootEverything=True)
            return ([quest],None)

        # mark terrain as completed
        pointsOfInterest = self.getRemainingPointsOfInterests()
        if not pointsOfInterest:
            if character.getFreeInventorySpace() <= 2:
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)
            quest = src.quests.questMap["Scavenge"](ignoreAlarm=True,ignoreScrap=True,reason="find useful items")
            return ([quest],None)

        # mark current tile as explored
        if character.getBigPosition() in self.getRemainingPointsOfInterests():
            if not dryRun:
                self.mark_POI_explored(character.getBigPosition())
            return (None,("+","register room as explored"))

        # loot a different room
        char_big_pos = character.getBigPosition()
        pointOfInterest = random.choice(pointsOfInterest)
        smallest_distance = None
        for check_point in pointsOfInterest:
            if random.random() > 0.8:
                continue
            distance = abs(char_big_pos[0]-check_point[0])+abs(char_big_pos[1]-check_point[1])
            if smallest_distance is None or distance <= smallest_distance:
                smallest_distance = distance
                pointOfInterest = check_point
        quest = src.quests.questMap["LootRoom"](targetPositionBig=pointOfInterest,endWhenFull=True,reason="gather loot")
        return ([quest],None)

    def generateTextDescription(self):
        reasonString = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reasonString = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f","),f" to {self.reason}."]
        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Explore the terrain"),reasonString,"""

"""]
        if self.lifetime:
            text.append(f"""
Do this for {self.lifetime} ticks. {self.getRemainingLifetime()} ticks left.
""")

        text.append((src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),f"""

Press the g m keys to open auto travel menu.

"""))

        text.append(f"""points of interest:\n""")
        rawMap = []
        for y in range(15):
            rawMap.append([])
            for x in range(15):
                if x == 0 or y == 0 or x == 14 or y == 14:
                    rawMap[y].append("~~")
                else:
                    rawMap[y].append("  ")
            rawMap[y].append("\n")
        for pos in self.getRemainingPointsOfInterests():
            rawMap[pos[1]][pos[0]] = "OO"
        for pos in self.donePointsOfInterest:
            rawMap[pos[1]][pos[0]] = "XX"
        text.append("\n")
        text.append(rawMap)
        text.append("\n")
        for pos in self.getRemainingPointsOfInterests()+self.donePointsOfInterest:
            text.append(f"* {pos}")
            if pos in self.donePointsOfInterest:
                text.append(f" visited")
            text.append(f"\n")
        if self.character:
            rawMap[self.character.getBigPosition()[1]][self.character.getBigPosition()[0]] = "@@"

        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        return False

    def mark_POI_explored(self,pos):
        if pos in self.getRemainingPointsOfInterests() and not pos in self.donePointsOfInterest:
            self.donePointsOfInterest.append(pos)

    def handleChangedTile(self, extraInfo=None):
        self.mark_POI_explored(extraInfo.get("old_pos"))
        self.mark_POI_explored(extraInfo.get("new_pos"))

    def handleEnteredRoom(self, extraInfo=None):
        self.mark_POI_explored(extraInfo[1].getPosition())

        self.clearSubQuests()

    def assignToCharacter(self, character):
        '''
        listen to the character changing the terrain
        '''
        if self.character:
            return

        self.startWatching(character,self.handleChangedTile, "changedTile")
        self.startWatching(character,self.handleEnteredRoom, "entered room")
        super().assignToCharacter(character)

src.quests.addType(StoryExploreHomeTerrain)
