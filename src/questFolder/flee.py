import random

import src


class Flee(src.quests.MetaQuestSequence):
    '''
    quest to flee from enemies
    '''
    type = "Flee"
    lowLevel = True

    def __init__(self, description="Flee", creator=None, command=None, lifetime=None, weaponOnly=False, returnHome=False, reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

        self.shortCode = "f"
        self.returnHome = returnHome
        self.startTick = None

        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        return [f"""Flee from your enemies{reasonString}."""]

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest if completed
        '''
        if not character:
            return False

        if not self.active:
            return False

        try:
            self.returnHome
        except:
            self.returnHome = False

        if not character.getNearbyEnemies():
            bigPos = character.getBigPosition()
            homePos = character.getHomeRoomCord()
            if self.returnHome and bigPos != homePos:
                return False
            if not dryRun:
                self.postHandler()
            return True

        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        calculate the next step towards solving this quest
        '''

        # wait for subquests to complete
        if self.subQuests:
            return (None,None)

        # run for a random exit after a while
        if src.gamestate.gamestate.tick-self.startTick > 50:
            if not dryRun:
                self.startTick = src.gamestate.gamestate.tick
            pos = random.choice([(6,0,0),(0,6,0),(12,6,0),(6,12,0)])
            quest = src.quests.questMap["GoToPosition"](targetPosition=pos,reason="reach escape spot")
            return ([quest],None)

        # return home after initial esscape 
        if not character.getNearbyEnemies():
            bigPos = character.getBigPosition()
            homePos = character.getHomeRoomCord()
            if self.returnHome and bigPos != homePos:
                quest = src.quests.questMap["GoHome"](reason="get back to safety")
                return ([quest],None)
            if not dryRun:
                self.postHandler()
            return (None,("+","end quest"))

        # heal
        if character.health < character.maxHealth//5 and character.canHeal():
            return (None,"JH","heal")

        # close other menus
        if not ignoreCommands:
            submenue = character.macroState.get("submenue")
            if submenue:
                return (None,(["esc"],"exit the menu"))

        # weight escape directions
        commands = []
        command = None
        for foundEnemy in character.getNearbyEnemies():
            if character.getPosition() == foundEnemy.getPosition():
                command = "m"
                break
            for offset in [((1,0,0),"a"),((-1,0,0),"d"),((0,1,0),"w"),((0,-1,0),"s")]:
                if character.getPosition(offset=offset[0]) == foundEnemy.getPosition():
                    if random.random() < 0.3:
                        return (None,("m","fight"))
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

        # get random escape direction
        if not command and commands:
            command = random.choice(commands)

        # add picking up items to the command
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

        # hang up AI at invalid direction :-P
        if command is None:
            return (None,(".","stand around confused"))

        # run the command
        return (None,(command,"flee"))

    def assignToCharacter(self, character):
        '''
        assign quest to character
        '''
        if self.character:
            return None

        self.startTick = src.gamestate.gamestate.tick

        return super().assignToCharacter(character)

# add the quest type
src.quests.addType(Flee)
