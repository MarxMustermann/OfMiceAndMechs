import random

import src


class Fight(src.quests.MetaQuestSequence):
    type = "Fight"

    def __init__(self, description="fight", creator=None, command=None, lifetime=None, weaponOnly=False, reason=None, suicidal=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly
        self.reason = reason
        self.suicidal = suicidal

        self.shortCode = "f"

    def generateTextDescription(self):
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

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if not character.getNearbyEnemies():
            self.postHandler()
            return True

        return None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        character.personality["autoCounterAttack"] = False
        character.personality["autoFlee"] = False

        if not character.getNearbyEnemies():
            self.postHandler()
            return (None,None)

        if character.health < character.maxHealth//5 and character.canHeal():
            return (None,("JH","heal"))

        try:
            self.suicidal
        except:
            self.suicidal = False
        if (not self.suicidal) and (character.health < character.maxHealth//5):
            self.fail()
            return (None,None)

        if not ignoreCommands:
            submenue = character.macroState.get("submenue")
            if submenue:
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

            if not character.hasSpecialAttacks:
                return (None,(directionCommand,"attack enemy"))

            specialAttack = None
            if character.exhaustion == 0:
                specialAttack = "k"
            elif character.exhaustion < 10:
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

            return (None,(directionCommand+specialAttack,"attack enemy"))

        # move toward enemies
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
                command = "Kdl"
        elif command == "a":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0]-1,pos[1],pos[2]),character=character):
                command = "Kal"
        elif command == "s":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0],pos[1]+1,pos[2]),character=character):
                command = "Ksl"
        elif command == "w":
            pos = character.getPosition()
            if not character.container.getPositionWalkable((pos[0],pos[1]-1,pos[2]),character=character):
                command = "Kwl"

        if command is None:
            return (None,None)

        return (None,(command,"fight"))

src.quests.addType(Fight)
