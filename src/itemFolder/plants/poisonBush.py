import src

class PoisonBush(src.items.Item):
    type = "PoisonBush"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.poisonBush,xPosition,yPosition,creator=creator,name="poison bush")
        self.walkable = False
        self.charges = 0
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        self.charges += 1
        if 100 > character.satiation:
            character.satiation = 0
        else:
            character.satiation -= 100

        if self.charges > 10:

            new = itemMap["EncrustedPoisonBush"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])

            self.container.removeItem(self)

        character.addMessage("you give your blood to the poison bush")

    def spawn(self,distance=1):
        if not (self.xPosition and self.yPosition):
            return
        direction = (2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%4
        direction = (random.randint(1,distance+1),random.randint(1,distance+1))
        newPos = (self.xPosition+direction[0]-5,self.yPosition+direction[1]-5)

        if newPos[0] < 1 or newPos[1] < 1 or newPos[0] > 15*15-2 or newPos[1] > 15*15-2:
            return

        if not (newPos in self.container.itemByCoordinates and len(self.container.itemByCoordinates[newPos])):
            new = itemMap["PoisonBloom"](creator=self)
            new.xPosition = newPos[0]
            new.yPosition = newPos[1]
            self.container.addItems([new])

    def getLongInfo(self):
        return "poison charges: %s"%(self.charges)

    def getLongInfo(self):
        return """
item: Poison Bush

description:
This a cluster of blooms with a network veins connecting them. Its spore sacks shriveled and are covered in green slime.

actions:
You can use it to loose 100 satiation.
"""

    def destroy(self, generateSrcap=True):
        new = itemMap["FireCrystals"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])

        character = characters.Exploder(creator=self)

        character.solvers = [
                  "NaiveActivateQuest",
                  "ActivateQuestMeta",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                  "NaivePickupQuest",
                  "NaiveMurderQuest",
                  "DrinkQuest",
                  "NaiveExamineQuest",
                  "ExamineQuestMeta",
                ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                    splittedCommand.append(char)
            return splittedCommand

        command = ""
        if src.gamestate.gamestate.tick%4 == 0:
            command += "A"
        if src.gamestate.gamestate.tick%4 == 1:
            command += "W"
        if src.gamestate.gamestate.tick%4 == 2:
            command += "S"
        if src.gamestate.gamestate.tick%4 == 3:
            command += "D"

        if self.xPosition%4 == 0:
            command += "A"
        if self.xPosition%4 == 1:
            command += "W"
        if self.xPosition%4 == 2:
            command += "S"
        if self.xPosition%4 == 3:
            command += "D"

        if self.yPosition%4 == 0:
            command += "A"
        if self.yPosition%4 == 1:
            command += "W"
        if self.yPosition%4 == 2:
            command += "S"
        if self.yPosition%4 == 3:
            command += "D"

        character.macroState["macros"]["m"] = splitCommand(command+"_m")

        character.macroState["commandKeyQueue"] = [("_",[]),("m",[])]
        character.satiation = 100
        self.container.addCharacter(character,self.xPosition,self.yPosition)

        super().destroy(generateSrcap=False)

src.items.addType(PoisonBush)
