import src

class PrepareAttack(src.quests.MetaQuestSequence):
    type = "PrepareAttack"

    def __init__(self, description="prepare attack", creator=None, command=None, lifetime=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shortCode = "P"
        self.targetPosition = targetPosition

    def generateTextDescription(self):
        (numCharges,discard,numItemsOnFloor) = self.getTrapInfo(self.character)
        numGuards = len(self.getGuards(self.character))
        text = """
When you destroy the hive the hive guards will become agitated.
This means they will start to attack everybody on this terrain.
Likely that means a wave of insects is rushing at the base.
This can overwhelm the bases defenses and cause damage.

Before starting the attack prepare for that wave.
Ensure the trap rooms are maintained to kill the incoming guards.
Destroying the hive will agitate hive guards within a distance of 3 tiles.
Killing those insects before killing the hive will reduce the waves size.
So you have two ways you can prepare for the wave.

This quest will end when you have prepared enough.
Your current preparedness score is {}, bring it to below 0.


The formula for the preparedness score is:
    10*numGuards-numCharges+numItemsOnFloor*20 = 10*{}-{}+{}*20 = {}""".format(self.getPreparednessScore(self.character),numGuards,numCharges,numItemsOnFloor,self.getPreparednessScore(self.character),)
        text += """



This quest works a bit different to previous quests.
It can handle multiple subquests at once.
The idea is to issue orders to the NPCs to maintain the traps and
Attack the hive guards while you are waiting for the work complete.
"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        foundSpawner = False
        terrain = character.getTerrain()
        rooms = terrain.getRoomByPosition(self.targetPosition)
        for room in rooms:
            items = room.getItemByPosition((6,6,0))
            for item in items:
                if isinstance(item, src.items.itemMap["MonsterSpawner"]) and not item.disabled:
                    foundSpawner = True

        if not foundSpawner:
            self.postHandler()
            return True

        # end when preparedness reached
        if self.getPreparednessScore(character) < 0:
            self.postHandler()
            return True
        return False

    def getPreparednessScore(self,character):
        numGuards = len(self.getGuards(character))
        (numCharges,discard,numItemsOnFloor) = self.getTrapInfo(character)
        rating = 10*numGuards-numCharges+numItemsOnFloor*20
        return rating

    def getTrapInfo(self,character):
        terrain = character.getTerrain()
        numCharges = 0
        maxCharges = 0
        numItemsOnFloor = 0
        for room in terrain.rooms:
            if not isinstance(room,src.rooms.TrapRoom):
                continue
            numCharges += room.electricalCharges
            maxCharges += room.maxElectricalCharges

            for item in room.itemsOnFloor:
                if item.bolted:
                    continue
                if item.getPosition() == (None,None,None):
                    continue
                numItemsOnFloor += 1
        return (numCharges,maxCharges,numItemsOnFloor)

    def getGuards(self,character):
        terrain = character.getTerrain()
        guards = []
        for otherChar in terrain.characters:
            if otherChar.faction != "invader":
                continue

            distance = otherChar.getBigDistance(self.targetPosition)
            if distance > 3:
                continue
            if otherChar.tag != "hiveGuard":
                continue
            guards.append(otherChar)

        for room in terrain.rooms:
            if otherChar.faction != "invader":
                continue

            distance = room.getDistance(self.targetPosition)
            if distance > 3:
                continue
            if otherChar.tag != "hiveGuard":
                continue
            guards.append(otherChar)
        return guards

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if not self.subQuests:
            (numCharges,numMaxCharges,numItemsOnFloor) = self.getTrapInfo(character)
            guards = self.getGuards(character)

            if guards:
                toSecure = []
                for guard in guards:
                    pos = guard.getBigPosition()
                    if pos in toSecure:
                        continue
                    toSecure.append(pos)
                self.addQuest(src.quests.questMap["SecureTiles"](toSecure=toSecure))
            if numItemsOnFloor > 0:
                self.addQuest(src.quests.questMap["CleanTraps"]())
            if numCharges < numMaxCharges:
                self.addQuest(src.quests.questMap["ReloadTraps"]())
            return

        # remove completed quests
        toRemove = []
        for quest in self.subQuests:
            if quest.completed:
                toRemove.append(quest)
        for quest in toRemove:
            self.subQuests.remove(quest)

        for subQuest in self.subQuests:
            if not subQuest.active:
                subQuest.activate()
                return
            if subQuest.character != character:
                subQuest.assignToCharacter(character)
                return
            if subQuest.isPaused():
                continue
            subQuest.solver(character)
            return
        character.runCommandString("10.")

src.quests.addType(PrepareAttack)
