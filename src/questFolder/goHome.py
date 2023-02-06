import src

class GoHome(src.quests.MetaQuestSequence):
    type = "GoHome"

    def __init__(self, description="go home", creator=None, paranoid=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.baseDescription = description
        # save initial state and register
        self.type = "GoHome"
        self.addedSubQuests = False
        self.paranoid = paranoid
        self.cityLocation = None

        self.attributesToStore.extend([
            "hasListener","addedSubQuests","paranoid"])

        self.tuplesToStore.append("cityLocation")

    def generateTextDescription(self):
        return """
Go home.

You consider the command center of the base your home.
That command centre holds the assimilator and
other important artworks like the quest artwork.

Many activities can be started from the command centre.
Go there and be ready for action.



Quests like this can be pretty boring.
Press c now to use auto move to complete this quest.
Be careful with auto move, while danger is nearby. 
Press crtl-d to stop your character from moving.
"""

    def triggerCompletionCheck(self, character=None):
        if not character:
            return
        if not self.cityLocation:
            return

        if character.getTerrainPosition() == self.terrainLocation and character.getBigPosition() == self.cityLocation:
            self.postHandler()
            return True
        return False

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return
        self.reroll()

        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        self.setHomeLocation(character)

        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")

        super().assignToCharacter(character)

    def setHomeLocation(self,character):
        self.cityLocation = (character.registers["HOMEx"],character.registers["HOMEy"],0)
        self.terrainLocation = (character.registers["HOMETx"],character.registers["HOMETy"],0)
        self.metaDescription = self.baseDescription+" %s/%s on %s/%s"%(self.cityLocation[0],self.cityLocation[1],self.terrainLocation[0],self.terrainLocation[1],)

    def generateSubquests(self,character):
        if self.subQuests:
            return

        if not character.getTerrainPosition() == self.terrainLocation:
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=self.terrainLocation)
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return
        elif not character.getBigPosition() == self.cityLocation:
            quest = src.quests.questMap["GoToTile"](paranoid=self.paranoid)
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            quest.setParameters({"targetPosition":(self.cityLocation[0],self.cityLocation[1])})
            return

    def solver(self, character):
        if self.generateSubquests(character):
            return False

        if self.subQuests:
            return super().solver(character)

        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        return False

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return self.subQuests[0].getSolvingCommandString(character,dryRun=dryRun)
        else:
            charPos = (character.xPosition%15,character.yPosition%15,0)
            if charPos in ((0,7,0),(0,6,0)):
                return "d"
            if charPos in ((7,14,0),(6,12,0)):
                return "w"
            if charPos in ((7,0,0),(6,0,0)):
                return "s"
            if charPos in ((14,7,0),(12,6,0)):
                return "a"

src.quests.addType(GoHome)
