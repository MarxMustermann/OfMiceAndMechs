import src
import random

class ChangeJob(src.quests.MetaQuestSequence):
    type = "ChangeJob"

    def __init__(self, description="take on new duty"):
        super().__init__()
        self.metaDescription = description

    def generateSubquests(self,character=None):
        if self.subQuests:
            return

        duty = None
        duties = []
        if character and isinstance(character.container,src.rooms.Room):
            room = character.container
            if not duties:
                for _scrapIn in room.getEmptyInputslots(itemType="Scrap"):
                    duties.append("resource gathering")

            for item in room.itemsOnFloor:
                if item.type in ("ScrapCompactor","Machine") and item.readyToUse():
                    duties.append("machine operation")

            emptyInputs = character.container.getEmptyInputslots()
            if emptyInputs:
                for emptyInput in emptyInputs:
                    if character.container.getNonEmptyOutputslots(emptyInput[1]):
                        duties.append("hauling")

        if duties:
            duty = random.choice(duties)
        self.addQuest(src.quests.questMap["Assimilate"](description="set new duties",preferedDuty=duty))

        skill = None
        if duty == "resource gathering":
            skill = "gathering"
        if duty == "machine operation":
            skill = "machine operation"
        if duty == "hauling":
            skill = "hauling"
        if duty == "resource fetching":
            skill = "resource fetching"

        if skill and skill in character.skills:
            return

        self.addQuest(src.quests.questMap["TrainSkill"](skillToTrain=skill))

    def generateTextDescription(self):
        return """
Retrain for a different duty.

Use the basic trainer to learn a new skill.
Reset your duties at the assimilator afterward.
"""

    def solver(self,character):
        if not self.subQuests:
            self.generateSubquests(character)
            return
        super().solver(character)

src.quests.addType(ChangeJob)
