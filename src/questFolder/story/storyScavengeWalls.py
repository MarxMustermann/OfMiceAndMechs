import src

class StoryScavengeWalls(src.quests.MetaQuestSequence):
    '''
    story quest pretending to gather walls for the for 
    '''
    type = "StoryScavengeWalls"
    def __init__(self, description="get building materials", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step toward solving the quest
        '''

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        quest = src.quests.questMap["Scavenge"](toCollect="Wall",ignoreAlarm=True)
        return ([quest],None)

    def generateTextDescription(self):
        reason_string = ""
        if self.reason:
            reason_string = f", to {self.reason}"
        return [f"""
Scavange for Walls{reason_string}.
"""]

    def triggerCompletionCheck(self,character=None, dryRun=True):
        if not character:
            return False

        if character.getFreeInventorySpace() <= 0:
            if not dryRun:
                self.postHandler()
            return True

        numWallsMissing = 0
        roomPos = (8,7,0)
        for x in range(1,14):
            for y in range(1,14):
                if x not in (1,13) and y not in (1,13):
                    continue
                if x == 7 or y == 7:
                    continue

                items = character.getTerrain().getItemByPosition((x+roomPos[0]*15,y+roomPos[1]*15,0))
                if items and items[0].type == "Wall":
                    continue
                
                numWallsMissing += 1

        if numWallsMissing <= len(character.searchInventory("Wall")):
            if not dryRun:
                self.postHandler()
            return True

        print("numWallsMissing")
        print(numWallsMissing,"/",len(character.searchInventory("Wall")))

        return False

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character, self.droppedItem, "dropped")
        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def droppedItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

src.quests.addType(StoryScavengeWalls)
