import src
import random


class DoGroundskeeping(src.quests.MetaQuestSequence):
    type = "DoGroundskeeping"

    def __init__(self, description="do groundskeeping", creator=None, onlyDoBasicSetup=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.onlyDoBasicSetup = onlyDoBasicSetup

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # no actions with sub quests
        if self.subQuests:
            return (None,None)

        # set up helper variable
        painter_stockpile_pos = (1,11,0)
        storageSpaces = []
        for x in range(1,12):
            if x == 6:
                continue
            storageSpaces.append((x,9,0))
            storageSpaces.append((x,11,0))
        if painter_stockpile_pos in storageSpaces:
            storageSpaces.remove(painter_stockpile_pos)
        done_painting = False
        groundskeepers_room = None
        for room in character.getTerrain().rooms:
            if room.tag != src.story.groundskeeper_room_tag:
                continue
            groundskeepers_room = room
            if not room.floorPlan:
                done_painting = True
        if isinstance(character,src.characters.characterMap["GroundsKeeper"]):
            has_painter = character.hasPainter()
        else:
            has_painter = False
            if character.searchInventory("Painter"):
                has_painter = True
            for room in character.getTerrain().rooms:
                if room.tag == "ruin":
                    continue
                if room.getNonEmptyOutputslots("Painter"):
                    has_painter = True

        # fetch Painter if not the actual groundskeeper
        if not has_painter and not isinstance(character,src.characters.characterMap["GroundsKeeper"]):
            for room in character.getTerrain().rooms:
                painter = room.getItemByType("Painter")
                if painter:
                    quest = src.quests.questMap["CleanSpace"](reason="fetch Painter",targetPositionBig=painter.getBigPosition(),targetPosition=painter.getPosition())
                    return ([quest],None)
            if character.getTerrain().search_item_by_type("Painter"):
                quest = src.quests.questMap["Scavenge"](toCollect="Painter",amountToCollect=1,ignoreAlarm=True)
                return ([quest],None)
            else:
                quest = src.quests.questMap["Adventure"]()
                return ([quest],None)

        # stack the scrap
        if not has_painter and not done_painting:
            if not character.getFreeInventorySpace():
                dropSpot = random.choice(storageSpaces)
                quests = []
                quests.append(src.quests.questMap["PlaceItem"](targetPosition=dropSpot,targetPositionBig=character.getBigPosition()))
                for _i in range(9):
                    quests.append(src.quests.questMap["ActivateItem"](targetPosition=dropSpot,targetPositionBig=character.getBigPosition()))
                return (list(reversed(quests)),None)
            scrap_items = character.container.getItemsByType("Scrap")
            candidates = []
            for scrap_item in scrap_items:
                if scrap_item.getPosition() in storageSpaces:
                    continue
                candidates.append(scrap_item)
            if candidates:
                scrap = random.choice(candidates)
                items_on_painter_position = groundskeepers_room.getItemByPosition(painter_stockpile_pos)
                if items_on_painter_position:
                    scrap = items_on_painter_position[0]
                quest = src.quests.questMap["CleanSpace"](targetPosition=scrap.getPosition(),targetPositionBig=scrap.getBigPosition())
                return ([quest],None)

        # draw Painter stockpile
        if groundskeepers_room and not groundskeepers_room.getMarkersOnPosition(painter_stockpile_pos):
            if groundskeepers_room.getItemByPosition(painter_stockpile_pos):
                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["DiscardItemsInside"](reason="get rid of the items safely",amount=1)
                    return ([quest],None)
                quest = src.quests.questMap["CleanSpace"](targetPosition=painter_stockpile_pos,targetPositionBig=groundskeepers_room.getPosition())
                return ([quest],None)
            quest = src.quests.questMap["DrawStockpile"](itemType="Painter",stockpileType="s",targetPositionBig=character.getBigPosition(),targetPosition=(1,11,0))
            return ([quest],None)

        # draw the general purpose stockpiles first
        rooms = character.getTerrain().getRoomsByTag(src.story.groundskeeper_room_tag)
        if rooms:
            room = rooms[0]
            if room.floorPlan:
                for storageSlot in room.floorPlan.get("storageSlots",[]):
                    if storageSlot[1]:
                        continue
                    quest = src.quests.questMap["DrawStockpile"](stockpileType="s",targetPositionBig=room.getPosition(),targetPosition=storageSlot[0])
                    return ([quest],None)

        # draw initial floorplan for the groundskeepers place
        rooms = character.getTerrain().getRoomsByTag(src.story.groundskeeper_room_tag)
        if rooms:
            room = rooms[0]
            if room.floorPlan:
                quest = src.quests.questMap["DrawFloorPlan"](targetPosition=room.getPosition())
                return ([quest],None)

        if self.onlyDoBasicSetup:
            return self._solver_trigger_success(dryRun)

        # be useful
        quest1 = src.quests.questMap["BeUsefull"](strict=True,endOnIdle=True)
        quest2 = src.quests.questMap["GoToPosition"](targetPosition=(6,6,0))
        quest3 = src.quests.questMap["WaitQuest"](lifetime=10)
        return ([quest3,quest2,quest1],None)

    def generateTextDescription(self):
        text = ["""
Do some groundskeeping."""]
        return text

src.quests.addType(DoGroundskeeping)
