import random

import src


class ClearTile(src.quests.MetaQuestSequence):
    '''
    quest to make NPC tidy up a room
    '''
    type = "ClearTile"
    lowLevel = True
    def __init__(self, description="clean tile", creator=None, targetPositionBig=None, noDelegate=False, reason=None, story=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        if targetPositionBig:
            self.metaDescription += " "+str(targetPositionBig)
        self.baseDescription = description
        self.reason = reason
        self.story = story

        self.timesDelegated = 0

        self.targetPositionBig = targetPositionBig

        self.noDelegate = noDelegate

    def generateTextDescription(self):
        '''
        generate a long text description to be shown on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = self.story

        if self.character.rank == 3:
            text = f"""{storyString}
Ensure that the trap room on {self.targetPositionBig} is cleaned{reasonString}.

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
Clean the room on tile {self.targetPositionBig}{reasonString}.

Remove all items from the walkways that are not bolted down."""
        return text

    def assignToCharacter(self, character):
        '''
        handle assigning the quest to a character
        '''
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self,extraInfo=None):
        '''
        indirection to call the actual funtion with converted parameters
        '''
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest if completed
        '''
        if not character:
            return False

        if not self.getLeftoverItems(character):
            if not dryRun:
                self.postHandler()
            return True

        return False

    def setParameters(self,parameters):
        '''
        set the parameters ina indirect way (obsolete)
        '''
        if "targetPositionBig" in parameters and "targetPositionBig" in parameters:
            self.targetPositionBig = parameters["targetPositionBig"]
            self.metaDescription = self.baseDescription+" "+str(self.targetPositionBig)
        return super().setParameters(parameters)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        calculate the next step towards solving the quest
        '''

        # wait for subquests to complete
        if self.subQuests:
            return (None,None)

        # abort on weird states
        if not character:
            return (None,None)

        # guess missing parameters
        if not self.targetPositionBig:
            if not dryRun:
                self.targetPositionBig = character.getBigPosition()
            return (None,("+","set current position as target"))

        # abort if threatended
        if character.getNearbyEnemies():
            return self._solver_trigger_fail(dryRun,"nearby enemies")

        # close menus
        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        # ensure inventory space
        if not character.getFreeInventorySpace() > 0:
            quest = src.quests.questMap["ClearInventory"](reason="have inventory space to pick up more items",returnToTile=False)
            return ([quest],None)

        # enter rooms properly
        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))

        # go to the tile to clean up
        if character.getBigPosition() != (self.targetPositionBig[0], self.targetPositionBig[1], 0):
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
            return ([quest],None)

        # check for items to pick up directly next to the character
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

        # clear items directly next to the character
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

        # go to an item to pick up
        items = self.getLeftoverItems(character)
        if items:
            item = random.choice(items)
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True)
            return ([quest],None)

        # complete when done
        if dryRun:
            self.postHandler()
        return (None,("+","end quest"))

    def getLeftoverItems(self,character):
        '''
        get a list of items that still needs to be cleaned up
        '''
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        targetPositionBig = self.targetPositionBig
        if not targetPositionBig:
            targetPositionBig = character.getBigPosition()

        rooms = terrain.getRoomByPosition(targetPositionBig)
        room = None
        if rooms:
            room = rooms[0]

        if not room:
            return []

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

# register quest type
src.quests.addType(ClearTile)
