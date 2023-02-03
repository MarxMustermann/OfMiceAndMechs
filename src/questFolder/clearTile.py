import src
import random

class ClearTile(src.quests.MetaQuestSequence):
    type = "ClearTile"

    def __init__(self, description="clean tile", creator=None, targetPosition=None, noDelegate=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        self.timesDelegated = 0

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.tuplesToStore.append("targetPosition")
        self.noDelegate = noDelegate

    def generateTextDescription(self):
        if self.character.rank == 3:
            text = """
Ensure that the trap room on %s is cleaned.

Since you are the commander of the base you can make other people do it.
Send the rank 5-6 NPCs and proceed to do something else in the meantime.

You can send NPCs to do tasks in rooms by using the room menu.
It work like this:
* go to the room
* press r to open room menu
* press o to issue command for this room
* press c for issuing the order to clean traps
* select the group to execute the order

After you do this the NPCs should stop what they are doing and start working on the new order.
If the task is not completed after some time, reload the trap room yourself.
Use the shockers in the trap room for this."""%(self.targetPosition,)
        else:
            text = """
Clean the room on tile %s.

Remove all items from the walkways."""%(self.targetPosition,)
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getLeftoverItems(character):
            self.postHandler()
            return

        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPosition)
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            if (not self.noDelegate) and character.rank == 3 and self.timesDelegated < 2:
                if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                    self.addQuest(quest)
                    return

                if not isinstance(character.container,src.rooms.Room):
                    if character.yPosition%15 == 14:
                        character.runCommandString("w")
                        return
                    if character.yPosition%15 == 0:
                        character.runCommandString("s")
                        return
                    if character.xPosition%15 == 14:
                        character.runCommandString("a")
                        return
                    if character.xPosition%15 == 0:
                        character.runCommandString("d")
                        return

                quest = src.quests.questMap["WaitQuest"](lifetime=200, creator=self)
                quest.assignToCharacter(character)
                self.addQuest(quest)
                quest = src.quests.questMap["RunCommand"](command="roc"+9*"s"+"j",description="send clones to clean tile")
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

                self.timesDelegated += 1
                return
            if not character.getFreeInventorySpace() > 0:
                quest = src.quests.questMap["ClearInventory"]()
                self.addQuest(quest)
                return
            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14:
                    character.runCommandString("w")
                    return
                if character.yPosition%15 == 0:
                    character.runCommandString("s")
                    return
                if character.xPosition%15 == 14:
                    character.runCommandString("a")
                    return
                if character.xPosition%15 == 0:
                    character.runCommandString("d")
                    return

            if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                return

            charPos = character.getPosition()
            
            offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
            foundOffset = None
            foundItems = None
            for offset in offsets:
                checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
                items = character.container.getItemByPosition(checkPos)
                if not items:
                    continue
                if items[0].bolted:
                    continue
                foundOffset = offset
                foundItems = items

            if foundOffset:
                if foundOffset == (0,0,0):
                    command = "k"
                elif foundOffset == (1,0,0):
                    command = "Kd"
                elif foundOffset == (-1,0,0):
                    command = "Ka"
                elif foundOffset == (0,1,0):
                    command = "Ks"
                elif foundOffset == (0,-1,0):
                    command = "Kw"

                quest = src.quests.questMap["RunCommand"](command=command*len(foundItems))
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)
                return

            items = self.getLeftoverItems(character)
            if items:
                item = random.choice(items)

                quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True)
                self.addQuest(quest)
                return

        super().solver(character)

    def getLeftoverItems(self,character):
        
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        rooms = terrain.getRoomByPosition(self.targetPosition)
        room = None
        if rooms:
            room = rooms[0]

        if room.floorPlan:
            return []

        foundItems = []
        for position in random.sample(list(room.walkingSpace)+[(6,0,0),(0,6,0),(12,6,0),(6,12,0)],len(room.walkingSpace)+4):
            items = room.getItemByPosition(position)

            if not items:
                continue
            if items[0].bolted:
                continue

            foundItems.append(items[0])

        return foundItems

src.quests.addType(ClearTile)
