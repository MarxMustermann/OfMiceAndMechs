import src
import random

class RestockBase(src.quests.MetaQuestSequence):
    type = "RestockBase"

    def __init__(self, description="restock base", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        rooms = self.findRestockableRooms()

        if not rooms:
            if not dryRun:
                self.postHandler()
            return (None,("+","end quest"))

        room = random.choice(rooms)
        quest = src.quests.questMap["RestockRoom"](targetPositionBig=room.getPosition(),allowAny=True)
        return ([quest],None)

    def findRestockableRooms(self):
        result = []
        terrain = self.character.getTerrain()
        for room in terrain.rooms:
            if room.tag == "ruin":
                continue
            for item in self.character.inventory:
                inputSlots = room.getEmptyInputslots(allowAny=True,allowStorage=True)
                if inputSlots:
                    if room not in result:
                        result.append(room)
        return result

    def generateTextDescription(self):
        text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Restock the base"),f""" with items from your inventory.
"""]
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if self.findRestockableRooms():
            return False

        if not dryRun:
            self.postHandler()
        return True

src.quests.addType(RestockBase)
