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
            return None

        if not character.getNearbyEnemies():
            self.postHandler()
            return True

        return None

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return nextStep[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        character.personality["autoCounterAttack"] = False
        character.personality["autoFlee"] = False

        if not character.getNearbyEnemies():
            self.postHandler()
            return (None,None)

        if character.health < character.maxHealth//5 and character.canHeal():
            return (None,"JH","to heal")

        if character.health > character.maxHealth//2:
            self.fail()
            return (None,None)

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

        if command == None:
            return (None,None)

        return (None,(command,"flee"))

src.quests.addType(Flee)
