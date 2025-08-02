import src
import random

class Integrator(src.items.Item):
    '''
    ingame item to set to baic values a NPC needs to work in a base
    '''
    type = "Integrator"
    def __init__(self,epoch=0):
        super().__init__(display="IT")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        '''
        set the duties for the character using this item
        '''

        # show user feedback
        character.addMessage(f"your duties were set. be useful!")

        # add quest to activate AI
        quest = src.quests.questMap["BeUsefull"](strict=True)
        quest.autoSolve = True
        quest.assignToCharacter(character)
        quest.activate()
        character.assignQuest(quest,active=True)

        # make charcter consume food (hack?)
        character.foodPerRound = 1

        duties = [ "room building",
                   "resource gathering",
                   "scrap hammering",
                   "mold farming",
                   "resource fetching",
                   "hauling",
                   "metal working",
                   "machine placing",
                   "maggot gathering",
                   "painting",
                   "cleaning",
                   "machine operation",
                   "manufacturing",
                   "scavenging",
                   "praying" ]
        character.duties = duties

        for duty in duties:
            character.dutyPriorities[duty] = random.randint(1,4)

        terrainPos = character.getTerrain().getPosition()
        characterPos = character.getBigPosition()
        character.registers["HOMEx"] = characterPos[0]
        character.registers["HOMEy"] = characterPos[1]
        character.registers["HOMETx"] = terrainPos[0]
        character.registers["HOMETy"] = terrainPos[1]

        self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"OO"})
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"OO"})

src.items.addType(Integrator)
