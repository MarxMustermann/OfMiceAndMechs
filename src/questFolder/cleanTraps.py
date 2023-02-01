import src

class CleanTraps(src.quests.MetaQuestSequence):
    type = "CleanTraps"

    def __init__(self, description="clean traps", creator=None, reputationReward=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reputationReward = reputationReward

    def generateTextDescription(self):
        text = """
Clean all trap room.

Items like corpses cluttering the trap rooms are a problem.
The traps work by shocking enemies when they step on the floor.
For this to work they need to directly step onto the floor.
Item lying on the floor prevent that.

So clean all trap rooms.

Trap rooms that need to be cleaned are:

"""
        for traproom in self.getClutteredTraprooms(self.character):
            text += str(traproom.getPosition())+"\n"
        return text

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getClutteredTraprooms(character):
            self.postHandler()
            return True

        return

    def getClutteredTraprooms(self,character):

        if isinstance(character.container,src.rooms.Room):
            terrain = character.container.container
        else:
            terrain  = character.container

        filledTraproom = []
        for room in terrain.rooms:
            if isinstance(room,src.rooms.TrapRoom):
                for item in room.itemsOnFloor:
                    if item.bolted:
                        continue
                    if item.getPosition() == (None, None, None):
                        continue
                    filledTraproom.append(room)
                    break
        
        return filledTraproom 

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            for room in self.getClutteredTraprooms(character):
                quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                quest.activate()
                quest.assignToCharacter(character)
                self.addQuest(quest)

        super().solver(character)

    def postHandler(self):
        if self.reputationReward and self.character:
            text = "cleaning the trap rooms"
            self.character.awardReputation(amount=self.reputationReward, reason=text)
        super().postHandler()

src.quests.addType(CleanTraps)
