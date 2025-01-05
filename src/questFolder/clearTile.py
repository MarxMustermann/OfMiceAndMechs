import random

import src


class ClearTile(src.quests.MetaQuestSequence):
    type = "ClearTile"

    def __init__(self, description="clean tile", creator=None, targetPosition=None, noDelegate=False, reason=None, story=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.reason = reason
        self.story = story

        self.timesDelegated = 0

        if targetPosition:
            self.setParameters({"targetPosition":targetPosition})

        self.noDelegate = noDelegate

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = self.story

        if self.character.rank == 3:
            text = f"""{storyString}
Ensure that the trap room on {self.targetPosition} is cleaned{reasonString}.

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
Use the shockers in the trap room for this."""
        else:
            text = f"""{storyString}
Clean the room on tile {self.targetPosition}{reasonString}.

Remove all items from the walkways that are not bolted down."""
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self,extraInfo=None):
        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):

        if not character:
            return False

        if not self.getLeftoverItems(character):
            self.postHandler()
            return True

        return False

    def setParameters(self,parameters):
        if "targetPosition" in parameters and "targetPosition" in parameters:
            self.targetPosition = parameters["targetPosition"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPosition)
        return super().setParameters(parameters)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getFreeInventorySpace() > 0:
            quest = src.quests.questMap["ClearInventory"](reason="have inventory space to pick up more items",returnToTile=False)
            return ([quest],None)
        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

        if character.getBigPosition() != (self.targetPosition[0], self.targetPosition[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
            return ([quest],None)

        charPos = character.getPosition()

        offsets = [(0,0,0),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
        foundOffset = None
        foundItems = None
        for offset in offsets:
            checkPos = (charPos[0]+offset[0],charPos[1]+offset[1],charPos[2]+offset[2])
            if checkPos not in character.container.walkingSpace:
                continue
            items = character.container.getItemByPosition(checkPos)
            if not items:
                continue

            if items[0].bolted:
                continue

            foundOffset = offset

            foundItems = []
            for item in items:
                if item.bolted:
                    break
                foundItems.append(item)
            break

        if foundOffset:
            interactionCommand = "K"
            if "advancedPickup" in character.interactionState:
                interactionCommand = ""

            if foundOffset == (0,0,0):
                command = "k"
            if foundOffset == (1,0,0):
                command = interactionCommand+"d"
            if foundOffset == (-1,0,0):
                command = interactionCommand+"a"
            if foundOffset == (0,1,0):
                command = interactionCommand+"s"
            if foundOffset == (0,-1,0):
                command = interactionCommand+"w"

            return (None,(command*len(foundItems),"clear spot"))

        items = self.getLeftoverItems(character)
        if items:
            item = random.choice(items)

            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True)
            return ([quest],None)

        return (None,None)

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
        for position in random.sample([*list(room.walkingSpace), (6, 0, 0), (0, 6, 0), (12, 6, 0), (6, 12, 0)],len(room.walkingSpace)+4):
            items = room.getItemByPosition(position)

            if not items:
                continue
            if items[0].bolted:
                continue

            foundItems.append(items[0])

        return foundItems

src.quests.addType(ClearTile)
