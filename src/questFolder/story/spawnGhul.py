import src


class SpawnGhul(src.quests.MetaQuestSequence):
    type = "SpawnGhul"

    def __init__(self, description="spawn ghul", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        numGhuls = 0
        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if otherChar.charType != "Ghul":
                continue
            numGhuls += 1
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.charType != "Ghul":
                    continue
                numGhuls += 1

        if numGhuls:
            self.postHandler()
            return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # no actions with sub quests
        if self.subQuests:
            return (None,None)
        
        # close open menues
        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))

        # use hardcoded target positions
        targetPosBig = (6,7,0)
        targetPos = (2,11,0)

        # get target CorpseAnimator
        rooms = character.getTerrain().getRoomByPosition(targetPosBig)
        if not rooms:
            if dryRun:
                self.fail("targetRoom not found")
            return (None,None)
        items = rooms[0].getItemByPosition(targetPos)
        corpseAnimator = None
        for item in items:
            if item.type != "CorpseAnimator":
                continue
            corpseAnimator = item

        # fail if CorpseAnimator is missing
        if not corpseAnimator:
            if dryRun:
                self.fail("CorpseAnimator missing")
            return (None,None)
        
        # spawn Ghul if CorpseAnimator is ready
        if corpseAnimator.filled:
            
            if character.getBigPosition() != targetPosBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=targetPosBig,description="go to a CorpseAnimator",reason="be able to spawn a Ghul")
                return ([quest],None)

            if not character.container.isRoom:
                pos = character.getSmallPosition()
                if pos == (14,7,0):
                    return (None,("a","enter room"))
                if pos == (0,7,0):
                    return (None,("d","enter room"))
                if pos == (7,14,0):
                    return (None,("w","enter room"))
                if pos == (7,0,0):
                    return (None,("s","enter room"))
                if dryRun:
                    self.fail("unable to enter room")
                return (None,None)
            
            if character.getDistance(targetPos) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=targetPos,ignoreEndBlocked=True,description="go to the CorpseAnimator",reason="be able to spawn a Ghul")
                return ([quest],None)

            pos = character.getPosition()
            direction = "."
            if (pos[0]-1,pos[1],pos[2]) == targetPos:
                direction = "a"
            if (pos[0]+1,pos[1],pos[2]) == targetPos:
                direction = "d"
            if (pos[0],pos[1]-1,pos[2]) == targetPos:
                direction = "w"
            if (pos[0],pos[1]+1,pos[2]) == targetPos:
                direction = "s"

            return (None,("J"+direction,"spawn ghul"))

        # ensure corpse in inventory
        corpses = character.searchInventory("Corpse")
        if not corpses:

            # fetch corpses from storage
            for room in character.getTerrain().rooms:
                if room.getNonEmptyOutputslots("Corpse"):
                    quest = src.quests.questMap["FetchItems"](toCollect="Corpse",amount=1)
                    return ([quest],None)

            for room in character.getTerrain().rooms:
                corpse = room.getItemByType("Corpse")
                if not corpse:
                    continue
                
                quest = src.quests.questMap["CleanSpace"](description="grab enemy remains", targetPositionBig=room.getPosition(), targetPosition=corpse.getPosition(), reason="have a corpse to reanimate", abortOnfullInventory=False)
                return ([quest],None)
            
            if dryRun:
                self.fail("no ghul")
            return (None,None)
        
        if character.getBigPosition() != targetPosBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=targetPosBig,description="go to a CorpseAnimator",reason="be able to spawn a Ghul")
            return ([quest],None)

        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
            if dryRun:
                self.fail("unable to enter room")
            return (None,None)
        
        if character.getDistance(targetPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=targetPos,ignoreEndBlocked=True,description="go to the CorpseAnimator",reason="be able to spawn a Ghul")
            return ([quest],None)

        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == targetPos:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == targetPos:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == targetPos:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == targetPos:
            direction = "s"

        return (None,("J"+direction,"fill the CorpseAnimator"))

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

Cleaning the TrapRoom is a dull and repetetive task.
It will keep you busy while you could do more useful work.
It still needs to be done or the TrapRoom will fail.

Ghouls can't do much, but they can do repetetive tasks.
As reanimated dead they cant think and only follow very detailed instructions.
Those instructions are held in commands (c#) and can be recorded from Sheets (+#).

This base has a automation set up to clear the TrapRoom using ghouls.
Fetch a Corpse and spawn a Ghoul to do that task.
"""]
        return text


src.quests.addType(SpawnGhul)
