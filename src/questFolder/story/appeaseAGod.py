import src
import random

class AppeaseAGod(src.quests.MetaQuestSequence):
    type = "AppeaseAGod"

    def __init__(self, description="apease a god", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None,targetNumGods=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetNumGods = targetNumGods

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # pray if possible
        for checkRoom in character.getTerrain().rooms:
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            foundStatue = None
            for checkStatue in glassStatues:
                if checkStatue.hasItem:
                    continue
                if checkStatue.charges >= 5:
                    continue
                if not checkStatue.handleItemRequirements():
                    continue
                foundStatue = checkStatue

            if not foundStatue:
                continue

            quest = src.quests.questMap["Pray"](targetPosition=foundStatue.getPosition(),targetPositionBig=foundStatue.getBigPosition(),shrine=False)
            return ([quest],None)

        # saccrifice from inventory if possible
        for checkRoom in character.getTerrain().rooms:
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            foundStatue = None
            for checkStatue in glassStatues:
                if checkStatue.hasItem:
                    continue
                if checkStatue.charges >= 5:
                    continue

                saccrificeType = src.gamestate.gamestate.gods[checkStatue.itemID]["sacrifice"][0]

                for item in character.inventory:
                    if not item.type == saccrificeType:
                        continue
                    quest = src.quests.questMap["RestockRoom"](toRestock=saccrificeType,targetPositionBig=checkRoom.getPosition())
                    return ([quest],None)

        # fetch items from storage if possible
        saccrificesNeeded = []
        for checkRoom in character.getTerrain().rooms:
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            foundStatue = None
            for checkStatue in glassStatues:
                if checkStatue.hasItem:
                    continue
                if checkStatue.charges >= 5:
                    continue

                saccrificeType = src.gamestate.gamestate.gods[checkStatue.itemID]["sacrifice"][0]

                saccrificesNeeded.append(saccrificeType)
        for saccrificeType in saccrificesNeeded:
            for checkRoom in character.getTerrain().rooms:
                if checkRoom.getNonEmptyOutputslots(itemType=saccrificeType,allowStorage=True,allowDesiredFilled=True):
                    quest = src.quests.questMap["FetchItems"](toCollect=saccrificeType)
                    return ([quest],None)

        if random.random() < 0.5:
            quest = src.quests.questMap["BeUsefull"](endOnIdle=True)
            return ([quest],None)

        # fetch scrap
        if "Scrap" in saccrificesNeeded:
            quest = src.quests.questMap["GatherScrap"]()
            return ([quest],None)

        # produce items
        for saccrificeType in saccrificesNeeded:
            if saccrificeType in ("Corpse","MoldFeed","MetalBars",):
                continue
            quest = src.quests.questMap["MetalWorking"](amount=1,toProduce=saccrificeType,produceToInventory=True,reason="produce a saccrifice",tryHard=True)
            return ([quest],None)

        return (None,("...........","wait for something to happen"))


    def generateTextDescription(self):
        text = """
Apease a god, to gain access to gain quick access to its GlassHeart.
The GlassStatues in the temple can teleport you the Dungeon containing the gods GlassHeart.
It needs to have 5 charges to allow you to actually do that.

Add charges and apease the god by praying and sacrificing items.
Place the items in the temple and use the GlassStatue to pray.
Examine the GlassStatues to see how much and what type of resources need to be sacrificed.

A proper temple should be set up to apease all gods after some time,
as long as enough workers and ressources are available.
"""
        if self.targetNumGods:
            text = f"""
Your goal is to reach {self.targetNumGods} unlocked GlassStatues.
"""
        return [text]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleSpawn, "spawned clone")
        super().assignToCharacter(character)

    def handleSpawn(self,extraInfo=None):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def wrapedTriggerCompletionCheck(self,character=None):
        pass

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        try:
            self.targetNumGods
        except:
            self.targetNumGods = None

        numGlassStatues = 0
        for checkRoom in character.getTerrain().rooms:
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            for checkStatue in glassStatues:
                if checkStatue.charges < 5 and not checkStatue.hasItem:
                    continue
                numGlassStatues += 1

        print(numGlassStatues)

        if self.targetNumGods:
            if self.targetNumGods <= numGlassStatues:
                self.postHandler()
                return True
        else:
            if numGlassStatues:
                self.postHandler()
                return True
        return False

src.quests.addType(AppeaseAGod)
