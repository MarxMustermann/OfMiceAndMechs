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

        if character.health < character.maxHealth/1.5:
            if not character.getNearbyEnemies():
                quest = src.quests.questMap["Heal"]()
                return ([quest],None)
            else:
                if character.getBigPosition() == (5,6,0):
                    quest = src.quests.questMap["GoTile"](targetPosition=(5,7,0))
                    return ([quest],None)
                if character.getBigPosition() == (5,7,0):
                    quest = src.quests.questMap["GoTile"](targetPosition=(6,7,0))
                    return ([quest],None)
                if character.getBigPosition() == (6,7,0):
                    quest = src.quests.questMap["Fight"]()
                    return ([quest],None)
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)

        if character.macroState["submenue"] and not ignoreCommands:
            if character.macroState["submenue"].tag != "specialAttackSelection":
                return (None,(["esc"],"to close menu"))

        targetPos = (5,6,0)
        if not character.getBigPosition() == targetPos:
            quest = src.quests.questMap["GoToTile"](targetPosition=targetPos, reason="to step outside of the base")
            return ([quest],None)

        enemies = character.getNearbyEnemies()
        if not enemies:
        
            terrain = character.getTerrain()
            foundSnatcher = False
            for otherChar in terrain.characters:
                if not otherChar.charType == "Snatcher":
                    continue
                foundSnatcher = True
                break

            if foundSnatcher:
                if not character.container.isRoom:
                    if character.xPosition%15 == 0:
                        return (None,("d","enter tile"))
                    if character.xPosition%15 == 14:
                        return (None,("a","enter tile"))
                    if character.yPosition%15 == 0:
                        return (None,("s","enter tile"))
                    if character.yPosition%15 == 14:
                        return (None,("w","enter tile"))

                return (None,("...........","wait for Snatchers"))

            if not dryRun:
                self.postHandler()
            return (None,None)

        characterPosition = character.getPosition()

        numDirectNeighbours = 0
        for enemy in enemies:
            if character.getDistance(enemy.getPosition()) > 1:
                continue
            numDirectNeighbours += 1
        if numDirectNeighbours > 2:
            return (None,("s","retreat"))

        for enemy in enemies:
            enemyPosition = enemy.getPosition()
            if enemyPosition == characterPosition:
                return (None,("m","attack Snatcher (bellow you)"))
            
            direction = None
            if enemyPosition == (characterPosition[0]-1,characterPosition[1],characterPosition[2]):
                direction = "a"
            if enemyPosition == (characterPosition[0]+1,characterPosition[1],characterPosition[2]):
                direction = "d"
            if enemyPosition == (characterPosition[0],characterPosition[1]-1,characterPosition[2]):
                direction = "w"
            if enemyPosition == (characterPosition[0],characterPosition[1]+1,characterPosition[2]):
                direction = "s"
            if direction:
                hasBerserk = False
                for statusEffect in character.statusEffects:
                    if not statusEffect.type == "Berserk":
                        continue
                    hasBerserk = True

                if not hasBerserk:
                    interactionCommand = direction.upper()
                    if character.macroState.get("submenue") and character.macroState["submenue"].tag == "specialAttackSelection":
                        interactionCommand = ""

                    if character.exhaustion < 1:
                        return (None,(interactionCommand+"k","attack Snatcher"))
                    if character.exhaustion < 10:
                        return (None,(interactionCommand+"h","attack Snatcher"))
                return (None,(direction,"attack Snatcher"))

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
        if not character:
            return False
        
        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if not otherChar.charType == "Snatcher":
                continue
            return False

        self.postHandler()
        return True

src.quests.addType(ConfrontSnatchers)
