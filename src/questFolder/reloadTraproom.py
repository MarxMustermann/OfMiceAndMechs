import src
import random

class ReloadTraproom(src.quests.MetaQuestSequence):
    type = "ReloadTraproom"

    def __init__(self, description="reload traproom", creator=None, command=None, lifetime=None, targetPosition=None, noDelegate=False):
        super().__init__(creator=creator, lifetime=lifetime)
        self.baseDescription = description
        self.metaDescription = self.baseDescription+f" {targetPosition}"
        self.shortCode = "R"

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.timesDelegated = 0
        self.noDelegate = noDelegate

    def generateTextDescription(self):
        text = """
Reload the trap room on tile %s."""
        if self.character.rank == 3:
            text = f"""
Ensure that the trap room on {self.targetPosition} is reloaded.

Since you are the commander of the base you can make other people do it.
Send the rank 5-6 NPCs and proceed to do something else in the meantime.


You can send NPCs to do tasks in rooms by using the room menu.
It work like this:
* go to the room
* press r to open room menu
* press o to issue command for this room
* press t to issue the order to reload the trap room.
* select the group to execute the order

After you do this the NPCs should stop what they are doing and start working on the new order.
If the task is not completed after some time, reload the trap room yourself.
Use the shockers in the trap room for this.
"""
        else:
            text = f"""
Reload the trap room on {self.targetPosition}.

Do this by using the shockers in the trap rooms.
Activate the shockers with lightning rods in your inventory.

This will reload the trap room and consume the lightning rods.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if self.getRoomCharged(character):
            super().triggerCompletionCheck()
            return

        return

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+f" {self.targetPosition}"
        return super().setParameters(parameters)

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            if (not self.noDelegate) and character.rank == 3 and self.timesDelegated < 2:
                if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
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
                self.addQuest(quest, addFront=False)
                quest = src.quests.questMap["RunCommand"](command="rot"+9*"s"+"j",description="send clones to reload trap room")
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

                self.timesDelegated += 1
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

            terrain = character.getTerrain()

            rooms = terrain.getRoomByPosition(self.targetPosition)
            room = None
            if rooms:
                room = rooms[0]

            if room != character.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                return

            character.addMessage("should recharge now")

            foundCharger = None
            for item in room.itemsOnFloor:
                if not item.bolted:
                    continue
                if item.type != "Shocker":
                    continue
                foundCharger = item

            if character.inventory and character.inventory[-1].type == "LightningRod":
                chargerPos = foundCharger.getPosition()
                characterPos = character.getPosition()
                if chargerPos == (characterPos[0]-1,characterPos[1],characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Ja")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0]+1,characterPos[1],characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Jd")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0],characterPos[1]-1,characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Jw")
                    quest.activate()
                    self.addQuest(quest)
                elif chargerPos == (characterPos[0],characterPos[1]+1,characterPos[2]):
                    quest = src.quests.questMap["RunCommand"](command=10*"Js")
                    quest.activate()
                    self.addQuest(quest)
                else:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundCharger.getPosition(),ignoreEndBlocked=True)
                    quest.activate()
                    quest.assignToCharacter(character)
                    self.addQuest(quest)
                return

            if character.getFreeInventorySpace() < 1:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)
                return

            if foundCharger:
                source = None
                for sourceCandidate in random.sample(list(room.sources),len(room.sources)):
                    if sourceCandidate[1] != "LightningRod":
                       continue

                    sourceRoom = room.container.getRoomByPosition(sourceCandidate[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    if not sourceRoom.getNonEmptyOutputslots(itemType=sourceCandidate[1]):
                        continue

                    source = sourceCandidate
                if source:
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=foundCharger.getPosition(),ignoreEndBlocked=True))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                    self.addQuest(src.quests.questMap["FetchItems"](toCollect="LightningRod"))
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=source[0]))
                    return

        super().solver(character)

    def getRoomCharged(self,character):

        terrain = character.getTerrain()

        rooms = terrain.getRoomByPosition(self.targetPosition)
        room = None
        if rooms:
            room = rooms[0]

        try:
            if room.electricalCharges < room.maxElectricalCharges:
                return False
            return True
        except:
            pass

        return False

src.quests.addType(ReloadTraproom)
