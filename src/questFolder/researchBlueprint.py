import src

class ResearchBluePrint(src.quests.MetaQuestSequence):
    type = "ResearchBluePrint"

    def __init__(self, description="research blueprint", creator=None, command=None, lifetime=None, targetPosition=None, itemType=None, tryHard=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.shortCode = "M"
        self.targetPosition = targetPosition
        self.itemType = itemType
        self.tryHard = tryHard

    def generateTextDescription(self):
        text = """
research a blueprint for %s.

"""%(self.itemType,)
        
        neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
        text += """
Blueprints are produced by a blueprinter (sX).
%s is needed to research a blueprint for %s.
You also need a sheet to print the blueprint on.
Examine the blueprinter for more details.
"""%(", ".join(self.getNeededResources()),self.itemType,)

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
If you miss resources, produce them.
"""

        return text

    def getNeededResources(self):
        itemMap = {
                    "Case"            :["Frame","MetalBars"],
                    "Frame"           :["Rod","MetalBars"],
                    "Rod"             :["Rod"],
                    "ScrapCompactor"  :["Scrap"],
                  }
        return itemMap.get(self.itemType,["MetalBars"])

    def solver(self, character):
        if not self.subQuests:
            room = character.getTerrain().getRoomByPosition((7,7,0))[0]
            items = room.getItemByPosition((8,7,0))
            if not items or not items[-1].type == "Sheet":
                if not character.inventory or not character.inventory[-1].type == "Sheet":
                    if self.tryHard:
                        quest = src.quests.questMap["FetchItems"](toCollect="Sheet",tryHard=self.tryHard,takeAnyUnbolted=True,amount=1)
                        self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                        self.addQuest(quest)
                        return ([quest], None)

                    self.fail(reason="missing Sheet to print on")
                    return
                if not character.getBigPosition() == (7,7,0):
                    self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0)))
                    return
                if not character.getPosition() == (8,7,0):
                    self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(8,7,0)))
                    return
                character.runCommandString("l")
                return

            neededResources = self.getNeededResources()

            counter = 0
            for neededResource in neededResources:
                items = room.getItemByPosition((7,8,0))
                if (not len(items) > counter) or (not items[-1-counter].type == neededResource):
                    if not character.inventory or not character.inventory[-1].type == neededResource:
                        if self.tryHard:
                            quest = src.quests.questMap["FetchItems"](toCollect=neededResource,tryHard=self.tryHard,takeAnyUnbolted=True,amount=1)
                            self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                            self.addQuest(quest)
                            return ([quest], None)

                        self.fail(reason="missing ressource %s"%(neededResource,))
                        return
                    if not character.getBigPosition() == (7,7,0):
                        self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0)))
                        return
                    if not character.getPosition() == (7,8,0):
                        self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(7,8,0)))
                        return
                    character.runCommandString("l")
                    return
                counter += 1


            if not character.getBigPosition() == (7,7,0):
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=(7,7,0)))
                return
            if character.getDistance((8,8,0)) > 1:
                self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=(8,8,0),ignoreEndBlocked=True))
                return

            directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
            directionFound = None
            for direction in directions:
                if character.getPosition(offset=direction[0]) == (8,8,0):
                    character.runCommandString("J"+direction[1])
                    return (None,"J"+direction[1])
            1/0 

        return super().solver(character)
    
    def triggerCompletionCheck(self,character=None):
        return False

    def producedBlueprint(self,extraInfo):
        print(extraInfo)
        print(self.itemType)
        if extraInfo["itemType"] == self.itemType:
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.producedBlueprint, "producedBlueprint")
        super().assignToCharacter(character)

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(ResearchBluePrint)
