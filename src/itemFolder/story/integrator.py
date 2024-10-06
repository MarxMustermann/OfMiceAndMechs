import src
import random

class Integrator(src.items.Item):
    """
    """

    type = "Integrator"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="IT")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        character.addMessage(f"your duties were set. be useful!")

        quest = src.quests.questMap["BeUsefull"](strict=True)
        quest.autoSolve = True
        quest.assignToCharacter(character)
        quest.activate()
        character.assignQuest(quest,active=True)
        character.foodPerRound = 1

        terrain = character.getTerrain()

        duties = [ "resource gathering",
                   "scrap hammering",
                   "resource fetching",
                   "hauling",
                   "metal working",
                   "machine placing",
                   "maggot gathering",
                   "painting",
                   "cleaning",
                   "machine operation",
                   "manufacturing",
                   "praying" ]
        character.duties = duties

        character.registers["HOMEx"] = 7
        character.registers["HOMEy"] = 7
        character.registers["HOMETx"] = terrain.xPosition
        character.registers["HOMETy"] = terrain.yPosition

        self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"OO"})
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"OO"})


src.items.addType(Integrator)
