import random

import src


class Fight(src.quests.MetaQuestSequence):
    '''
    quest for fighting within a tile
    '''
    type = "Fight"
    lowLevel = True
    def __init__(self, description="fight", creator=None, command=None, lifetime=None, weaponOnly=False, reason=None, suicidal=False, simpleOnly=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly
        self.reason = reason
        self.suicidal = suicidal
        self.simpleOnly = simpleOnly

        self.shortCode = "f"

    def generateTextDescription(self):
        '''
        generate a description text to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        return [f"""
Fight the enemies{reasonString}.

For simple attacks just bump into the enemies.
You will hit them and hopefully do some damage.

Advanced attacks are used by bumping into enemies while holding shift.

So if an enemy is to directly east of you:
* press d to do a normal attack
* press D to do a special attack
"""]

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest if completed
        '''
        if not character:
            return False

        if not character.getNearbyEnemies():
            if not dryRun:
                self.postHandler()
            return True

        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for enemy in character.getNearbyEnemies():
                    result.append((enemy.getPosition(),"target"))
        return result

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        generate next step towards solving this quest
        '''

        # do nothing if the quest has subquests
        if self.subQuests:
            return (None,None)

        character.personality["autoCounterAttack"] = False
        character.personality["autoFlee"] = False

        if not character.getNearbyEnemies():
            if not dryRun:
                self.postHandler()
            return (None,("+","end quest"))

        if character.health < character.maxHealth//2 and character.canHeal():
            return (None,("Jh","heal"))

        try:
            self.suicidal
        except:
            self.suicidal = False
        if (not self.suicidal) and (character.health < character.maxHealth//5):
            return self._solver_trigger_fail(dryRun,"low health")

        # make character drop tools to fight
        if character.tool:
            submenue = character.macroState.get("submenue")
            if not submenue:
                return (None,("v","open character menu"))
            if not isinstance(submenue,src.menuFolder.characterInfoMenu.CharacterInfoMenu):
                return (None,(["esc"],"close menu"))
            return (None,("t","drop tool"))

        if not ignoreCommands:
            submenue = character.macroState.get("submenue")
            if submenue and not submenue.tag == "specialAttackSelection":
                return (None,(["esc"],"exit the menu"))

        # check for direct attacks
        directEnemies = []
        for foundEnemy in character.getNearbyEnemies():
            if character.getDistance(foundEnemy.getPosition()) <= 1:
                directEnemies.append(foundEnemy)
        commands = []
        for enemy in directEnemies:
            direction = (enemy.xPosition-character.xPosition,enemy.yPosition-character.yPosition,enemy.zPosition-character.zPosition)

            directionCommand = None
            if direction == (1,0,0):
                directionCommand = "d"
            if direction == (-1,0,0):
                directionCommand = "a"
            if direction == (0,1,0):
                directionCommand = "s"
            if direction == (0,-1,0):
                directionCommand = "w"

            if not directionCommand:
                return (None,("m","attack enemy (below you)"))

            if not character.hasSpecialAttacks or self.simpleOnly:
                return (None,(directionCommand,"attack enemy"))

            specialAttack = None
            if character.exhaustion == 0:
                specialAttack = "k"
            elif character.exhaustion <= 7:
                specialAttack = "h"
            if not specialAttack:
                return (None,(directionCommand,"attack enemy"))

            if directionCommand == "d":
                directionCommand = "D"
            if directionCommand == "a":
                directionCommand = "A"
            if directionCommand == "s":
                directionCommand = "S"
            if directionCommand == "w":
                directionCommand = "W"

            if character.macroState.get("submenue") and character.macroState["submenue"].tag == "specialAttackSelection":
                directionCommand = ""

            return (None,(directionCommand+specialAttack,"attack enemy"))

        if character.exhaustion > 1:
            return (None,(".","catch breath"))

        if character.hasLineShot and character.searchInventory("Bolt") and not character.isOnHomeTerrain():
            for enemy in character.getNearbyEnemies():
                direction = None
                if enemy.xPosition == character.xPosition:
                    if enemy.yPosition > character.yPosition:
                        direction = "s"
                    else:
                        direction = "w"
                if enemy.yPosition == character.yPosition:
                    if enemy.xPosition > character.xPosition:
                        direction = "d"
                    else:
                        direction = "a"
                if direction:
                    fire_command = "f"
                    if "fireDirection" in character.interactionState:
                        fire_command = ""
                    return (None,(fire_command+direction,"shoot enemy"))

        # move toward enemies (smarter)
        if isinstance(character,src.characters.characterMap["Clone"]):
            shortestPath = None
            for enemy in character.getNearbyEnemies():
                if character.container.isRoom:
                    path = character.container.getPathTile(character.getPosition(),enemy.getPosition(),ignoreEndBlocked=True,character=character)
                else:
                    path = character.container.getPathTile(character.getBigPosition(),character.getSpacePosition(),enemy.getSpacePosition(),ignoreEndBlocked=True,character=character)

                if path and (shortestPath == None or len(shortestPath) > len(path)):
                    shortestPath = path

            if not shortestPath:
                for enemy in character.getNearbyEnemies():
                    if character.container.isRoom:
                        path = character.container.getPathTile(character.getPosition(),enemy.getPosition(),ignoreEndBlocked=True,character=character,ignoreUnbolted=True)
                    else:
                        path = character.container.getPathTile(character.getBigPosition(),character.getSpacePosition(),enemy.getSpacePosition(),ignoreEndBlocked=True,character=character,ignoreUnbolted=True)

                    if path and (shortestPath == None or len(shortestPath) > len(path)):
                        shortestPath = path

            if shortestPath:
                command = None
                step = shortestPath[0]
                if step == (-1,0):
                    command = "a"
                if step == (1,0):
                    command = "d"
                if step == (0,-1):
                    command = "w"
                if step == (0,1):
                    command = "s"

                if command == "d":
                    pos = character.getPosition()
                    if not character.container.getPositionWalkable((pos[0]+1,pos[1],pos[2]),character=character):
                        command = "Kd"+random.choice(["l","La","Ls","Lw","Ld"])
                elif command == "a":
                    pos = character.getPosition()
                    if not character.container.getPositionWalkable((pos[0]-1,pos[1],pos[2]),character=character):
                        command = "Ka"+random.choice(["l","La","Ls","Lw","Ld"])
                elif command == "s":
                    pos = character.getPosition()
                    if not character.container.getPositionWalkable((pos[0],pos[1]+1,pos[2]),character=character):
                        command = "Ks"+random.choice(["l","La","Ls","Lw","Ld"])
                elif command == "w":
                    pos = character.getPosition()
                    if not character.container.getPositionWalkable((pos[0],pos[1]-1,pos[2]),character=character):
                        command = "Kw"+random.choice(["l","La","Ls","Lw","Ld"])

                if command:
                    return (None,(command,"approach enemy"))

        commands = []
        command = None
        for foundEnemy in character.getNearbyEnemies():
            for offset in [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w"),((0,0,0),"m")]:
                if character.getPosition(offset=offset[0]) == foundEnemy.getPosition():
                    command = offset[1]
                    break

            x = foundEnemy.xPosition
            while x-character.xPosition > 0:
                commands.append("d")
                x -= 1
            x = foundEnemy.xPosition
            while x-character.xPosition < 0:
                commands.append("a")
                x += 1
            y = foundEnemy.yPosition
            while y-character.yPosition > 0:
                commands.append("s")
                y -= 1
            y = foundEnemy.yPosition
            while y-character.yPosition < 0:
                commands.append("w")
                y += 1

        if not command and commands:
            command = random.choice(commands)

        if random.random() < 0.1:
            command = random.choice(["w","a","s","d"])

        if command == "d":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0]+1,pos[1],pos[2]),character=character):
                command = "Kd"+random.choice(["l","La","Ls","Lw","Ld"])
        elif command == "a":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0]-1,pos[1],pos[2]),character=character):
                command = "Ka"+random.choice(["l","La","Ls","Lw","Ld"])
        elif command == "s":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0],pos[1]+1,pos[2]),character=character):
                command = "Ks"+random.choice(["l","La","Ls","Lw","Ld"])
        elif command == "w":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0],pos[1]-1,pos[2]),character=character):
                command = "Kw"+random.choice(["l","La","Ls","Lw","Ld"])

        if command is None:
            return (None,(".","stand around confused (no command found)"))

        return (None,(command,"approach enemy"))

# register the quest type
src.quests.addType(Fight)
