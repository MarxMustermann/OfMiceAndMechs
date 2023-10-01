import src
import random

class ReloadTraps(src.quests.MetaQuestSequence):
    type = "ReloadTraps"

    def __init__(self, description="reload traps", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.shortCode = "R"

    def generateTextDescription(self):
        text = """
Reload all trap rooms.

Trap rooms that need to be reloaded:

"""
        for traproom in self.getUnfilledTrapRooms(self.character):
            text += str(traproom.getPosition())+"\n"
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getUnfilledTrapRooms(character):
            super().triggerCompletionCheck()
            return

        return

    def getUnfilledTrapRooms(self,character):
        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain = character.container

        foundTraprooms = []
        for room in terrain.rooms:
            if not isinstance(room,src.rooms.TrapRoom):
                continue

            if room.electricalCharges > room.maxElectricalCharges-30:
                continue

            foundTraprooms.append(room)

        return foundTraprooms

    def solver(self, character):
        self.triggerCompletionCheck(character)

        if self.completed:
            return

        if not self.subQuests:
            room = random.choice(self.getUnfilledTrapRooms(character))

            quest = src.quests.questMap["ReloadTraproom"](targetPosition=room.getPosition())
            self.addQuest(quest)
            return

        return super().solver(character)

src.quests.addType(ReloadTraps)
