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

        # count the number of enemies/allies
        npcCount = 0
        enemyCount = 0
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction != character.faction:
                    enemyCount += 1
                    if not room.alarm:
                        quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True,description="kill enemies that breached the defences")
                        return ([quest],None)
                else:
                    if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                        npcCount += 1
        for otherChar in terrain.characters:
            if otherChar.faction != character.faction:
                enemyCount += 1
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)
            else:
                if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                    npcCount += 1
        if npcCount < 2:
            quest = src.quests.questMap["SpawnClone"]()
            return ([quest],None)

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

        # clear any input stockpiles with wrong content
        for checkRoom in character.getTerrain().rooms:
            glassStatues = checkRoom.getItemsByType("GlassStatue")
            if not glassStatues:
                continue

            for inputSlot in checkRoom.inputSlots:
                for item in checkRoom.getItemByPosition(inputSlot[0]):
                    if item.type != inputSlot[1]:
                        quest = src.quests.questMap["CleanSpace"](targetPosition=item.getPosition(),targetPositionBig=checkRoom.getPosition(),pickUpBolted=True)
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
            
            if not character.getTerrain().alarm:
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce=saccrificeType,produceToInventory=True,reason="produce a saccrifice",tryHard=True)
                return ([quest],None)

            hasScrap = False
            hasMetalBars = False
            for room in character.getTerrain().rooms:
                if room.getNonEmptyOutputslots("Scrap"):
                    hasScrap = True
                if room.getNonEmptyOutputslots("MetalBars"):
                    hasMetalbars = True

            if hasScrap and hasMetalBars:
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce=saccrificeType,produceToInventory=True,reason="produce a saccrifice",tryHard=True)
                return ([quest],None)

        if character.getTerrain().alarm:
            if src.gamestate.gamestate.tick%(15*15*15) < 2000 and src.gamestate.gamestate.tick%(15*15*15) > 10:
                quest = src.quests.questMap["LiftOutsideRestrictions"]()
                return ([quest],None)
            return (None,("...........","wait for the wave of enemies"))
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
            text += f"""
Your goal is to reach {self.targetNumGods} unlocked GlassStatues.
"""

        if self.lifetimeEvent:
            text += f"""\nlifetime: {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} / {self.lifetime}\n"""
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
