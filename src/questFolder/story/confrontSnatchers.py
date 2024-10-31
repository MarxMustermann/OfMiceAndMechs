import src

class ConfrontSnatchers(src.quests.MetaQuestSequence):
    type = "ConfrontSnatchers"

    def __init__(self, description="confront snatchers", creator=None, lifetime=None ,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.health < character.maxHealth/2:
            quest = src.quests.questMap["Heal"]()
            return ([quest],None)

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))

        targetPos = (5,6,0)
        if not character.getBigPosition() == targetPos:
            quest = src.quests.questMap["GoToTile"](targetPosition=targetPos, reason="to step outside of the base")
            return ([quest],None)

        enemies = character.getNearbyEnemies()
        if not enemies:
            return (None,("...........","wait for Snatchers"))

        characterPosition = character.getPosition()
        for enemy in enemies:
            enemyPosition = enemy.getPosition()
            if enemyPosition == (characterPosition[0]-1,characterPosition[1],characterPosition[2]):
                return (None,("a","attack Snatcher"))
            if enemyPosition == (characterPosition[0]+1,characterPosition[1],characterPosition[2]):
                return (None,("d","attack Snatcher"))
            if enemyPosition == (characterPosition[0],characterPosition[1]-1,characterPosition[2]):
                return (None,("w","attack Snatcher"))
            if enemyPosition == (characterPosition[0],characterPosition[1]+1,characterPosition[2]):
                return (None,("s","attack Snatcher"))
            if enemyPosition == characterPosition:
                return (None,("m","attack Snatcher"))

        return (None,(".","let Snatchers approach"))

    def generateTextDescription(self):
        result = [f"""
The outside of the base is still a dangerous place.
One of the reasons for that Snatchers will swarm and kill anybody that goes outside.
You need to confront and kill them, to make the outside accessible.

Use their swarming behaviour against them.
Just step outside of the base a little bit and retreat when you get overwhelmed.
The Snatchers will not follow you back into the base.
Rest and heal and repeat until all Snatchers are dead.

"""]
        return result

    def triggerCompletionCheck(self,character=None):
        print("triggerCompletionCheck")
        if not character:
            return False
        
        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if not otherChar.charType == "Snatcher":
                continue
            print(otherChar)
            print(otherChar.getBigPosition())
            return False

        self.postHandler()
        return True

src.quests.addType(ConfrontSnatchers)
