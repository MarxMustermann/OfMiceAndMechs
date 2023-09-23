import src
import random

class RaidTutorial3(src.quests.MetaQuestSequence):
    type = "RaidTutorial3"

    def __init__(self, description="raid enemy base", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shownPickedUpMachines = False

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        try:
            self.shownPickedUpSpecialItemSlot
        except:
            self.shownPickedUpSpecialItemSlot = False

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.shownPickedUpSpecialItemSlot:
            #if character.inventory:
            #    quest = src.quests.questMap["ClearInventory"](returnToTile=False)
            #    return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),(1,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(1,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((0,7,0),):
                if not character.getSpacePosition() == (1,7,0):
                    quest = src.quests.questMap["GoToPosition"](targetPosition=(1,7,0))
                    return ([quest],None)
            return (None,("a","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 5):
            specialItemSlot = None
            for room in terrain.rooms:
                for item in room.getItemsByType("SpecialItemSlot"):
                    if not item.hasItem:
                        continue
                    specialItemSlot = item
                    break

            if specialItemSlot:
                if not character.container == specialItemSlot.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=specialItemSlot.container.getPosition())
                    return ([quest],None)
                
                if character.getDistance(specialItemSlot.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=specialItemSlot.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)

                offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w")]
                for offset in offsets:
                    if character.getPosition(offset=offset[0]) == specialItemSlot.getPosition():
                        return (None,("J"+offset[1],"eject the special item"))
                7/0
                    
            specialItem = None
            for room in terrain.rooms:
                for item in room.getItemsByType("SpecialItem"):
                    specialItem = item
                    break

            if specialItem:
                if not character.container == specialItem.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=specialItem.container.getPosition())
                    return ([quest],None)
                
                if character.getDistance(specialItem.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=specialItem.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)

                offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w")]
                for offset in offsets:
                    if character.getPosition(offset=offset[0]) == specialItem.getPosition():
                        return (None,("K"+offset[1],"pick up the special item"))
                7/0
                    
            if not self.shownPickedUpSpecialItemSlot:
                text = """
Great! you picked up the special item. 
Now return it to your base.

= press space to continue =
"""
                src.interaction.showInterruptText(text)
                self.shownPickedUpSpecialItemSlot = True

            if not character.getBigPosition() in ((14,7,0),(13,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if not character.getBigPosition() in ((14,7,0),):
                if not character.getSpacePosition() == (13,7,0):
                    quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                    return ([quest],None)
            return (None,("d","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 6):
            specialItemSlot = None
            for room in terrain.rooms:
                for item in room.getItemsByType("SpecialItemSlot"):
                    if item.hasItem:
                        continue
                    specialItemSlot = item
                    break

            if specialItemSlot:
                if not character.container == specialItemSlot.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=specialItemSlot.container.getPosition())
                    return ([quest],None)
                
                if character.getDistance(specialItemSlot.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=specialItemSlot.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)

                offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w")]
                for offset in offsets:
                    if character.getPosition(offset=offset[0]) == specialItemSlot.getPosition():
                        return (None,("J"+offset[1],"eject the special item"))
                7/0

            self.postHandler()
            return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(RaidTutorial3)
