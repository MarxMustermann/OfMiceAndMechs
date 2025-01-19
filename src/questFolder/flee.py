import random

import src


class Flee(src.quests.MetaQuestSequence):
    type = "Flee"

    def __init__(self, description="Flee", creator=None, command=None, lifetime=None, weaponOnly=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

        self.shortCode = "f"

    def generateTextDescription(self):
        return ["""
run,run,run!!!
"""]

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not self.active:
            return False

        if not character.getNearbyEnemies():
            self.postHandler()
            return True

        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        if not character.getNearbyEnemies():
            if not dryRun:
                self.postHandler()
            return (None,None)

        if character.health < character.maxHealth//5 and character.canHeal():
            return (None,"JH","heal")

        if not ignoreCommands:
            submenue = character.macroState.get("submenue")
            if submenue:
                return (None,(["esc"],"exit the menu"))

        commands = []
        command = None
        for foundEnemy in character.getNearbyEnemies():
            for offset in [((1,0,0),"a"),((-1,0,0),"d"),((0,1,0),"w"),((0,-1,0),"s")]:
                if character.getPosition(offset=offset[0]) == foundEnemy.getPosition():
                    command = offset[1]
                    break

            x = foundEnemy.xPosition
            while x-character.xPosition > 0:
                commands.append("a")
                x -= 1
            x = foundEnemy.xPosition
            while x-character.xPosition < 0:
                commands.append("d")
                x += 1
            y = foundEnemy.yPosition
            while y-character.yPosition > 0:
                commands.append("w")
                y -= 1
            y = foundEnemy.yPosition
            while y-character.yPosition < 0:
                commands.append("s")
                y += 1

        if not command and commands:
            command = random.choice(commands)

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

        return (None,(command,"flee"))

src.quests.addType(Flee)
