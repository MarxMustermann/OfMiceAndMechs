"""
the code for the characters belongs here
"""
import logging
import random

import config
import src.canvas
import src.chats
import src.gamestate
import src.interaction

urwid = None
logger = logging.getLogger(__name__)


class Character:
    """
    this is the class for characters meaning both npc and pcs.
    """

    def __init__(
        self,
        display=None,
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name=None,
        creator=None,
        characterId=None,
        seed=None,
    ):
        """
        sets basic info AND adds default behavior/items

        Parameters:
            display: how the character is rendered
            xPosition: obsolete, to be removed
            yPosition: obsolete, to be removed
            quests: obsolete, to be removed
            automated: obsolete, to be removed
            name: the name the character should have
            creator: obsolete, to be removed
            characterId: obsolete, to be removed
            seed: rng seed
        """
        if quests is None:
            quests = []

        self.addExhaustionOnHurt = False # flag to exhaustion if hurt
        self.removeExhaustionOnHeal = True # flag to remove exhaustion fully on heal
        self.reduceExhaustionOnHeal = False # flag to reduce exhaustion when healing
        self.reduceExhaustionBonus = 1 # bonus added when reducing exhaustion
        self.reduceExhaustionDividend = 10 # flag to reduce exhaustion when healing
        self.doubleDamageOnZeroExhaustion = False # flag to double damage with zero exhaustion
        self.bonusDamageOnLowerExhaustion = False # flag to deal bonus damage when attacker has lower exhaustion then the enemy
        self.reduceDamageOnAttackerExhausted = False # flag to reduce damage dealt when exhausted
        self.increaseDamageOnTargetExhausted = False # flag to increase damage when target is exhausted
        self.addRandomExhaustionOnAttack = False # flag to add random exhaustion when attacking
        self.addRandomExhaustionOnHurt = False # flag to add random exhaustion when getting hurt
        self.flatExhaustionAttackCost = 0 # constant cost for attacking
        self.healingModifier = 1.0 # multiplier for how much health healing adds
        self.healingThreashold = 1 # threashold regulating when healing triggers
        self.movementSpeed = 1 # the speed characters move with
        self.attackSpeed = 1 # the speed characters attack with

        self.disableCommandsOnPlus = False
        self.charType = "Character"
        self.disabled = False
        self.superior = None
        self.rank = None
        self.isStaff = False
        self.stepsOnMines = False
        self.implantLoad = 0
        self.hasFreeWill = False

        self.showThinking = False
        self.showGotCommand = False
        self.showGaveCommand = False

        self.rememberedMenu = []
        self.rememberedMenu2 = []

        self.pathCache = {}

        self.skills = []
        self.grievances = {}

        self.exhaustion = 0
        self.tag = None

        self.duties = []

        self.foodPerRound = 0

        super().__init__()

        if name is None and seed:
            firstName = config.names.characterFirstNames[
                    seed % len(config.names.characterFirstNames)
                ]
            lastName = config.names.characterLastNames[
                    (seed * 10) % len(config.names.characterLastNames)
                ]
            name = f"{firstName} {lastName}"

        if display is None and name is not None:
            display = src.canvas.displayChars.staffCharactersByLetter[name[0].lower()]

        if name is None:

            firstName = random.choice([
                "Siegfried","Ernst","Alfred","Herrmann","Friedrich","Helmut","Karl","Gunnar","Berthold","Dietrich",
                "Friedhelm","Horst","Edmund","Wilhelm","Albert","Johann","Herbert","Bertram","Hans","Jochen","Ludwig",
                "Raimund","Thorsten","Ulrich","Veit","Lutz","Anton","Alwin","Sigmund","Kurt","Heidrun","Elfriede",
                "Gunhilde","Hildegard","Gudrun","Gertrude","Brunhilde","Adelheid","Sieglinde","Kunigunde","Herta",
                "Frieda","Ursula","Katharina","Johanna","Clara","Isolde","Hermine","Berta","Gisela","Lina","Irmgard",
                "Marlene","Mathilde","Monika","Frieda","Gerlinde","Rita","Clementine","Brigitte","Adalbert","Jörg",
                "Moritz","Maximillian","Gundula","Renate","Udo","Fritz","Susanne","Guido"])

            mainNameCore = random.choice([
                "Berg","Stahl","Hammer","Kraut","Barren","Eichen","Sieben","Eisen","Bären","Hunde","Ketten","Felsen",
                "Feuer","Glut","Stein",
            ])

            postfix = random.choice([
                "brecher","wurst","schmidt","maier","bach","burg","treu","kraft","schmied","hans","schimmel",
                "hauer","schläger","feind","kranz","fels",
            ])

            name = firstName+" "+mainNameCore+postfix

        if display is None:
            display = src.canvas.displayChars.staffCharacters[0]

        self.setDefaultMacroState()

        self.macroStateBackup = None

        # set basic state
        self.specialRender = False
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        # NIY: not really used yet
        self.maxInventorySpace = 10
        self.watched = False
        self.listeners = {"default": []}
        self.path = []
        self.subordinates = []
        self.reputation = 0
        self.events = []
        self.room = None
        self.terrain = None
        self.xPosition = 0
        self.yPosition = 0
        self.zPosition = 0
        self.satiation = 1000
        self.dead = False
        self.deathReason = None
        self.questsToDelegate = []
        self.unconcious = False
        self.displayOriginal = display
        self.isMilitary = False
        self.hasFloorPermit = True
        # bad code: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []
        self.questsDone = []
        self.solvers = ["NaiveDropQuest","NaivePickUpQuest"]
        self.aliances = []
        self.stasis = False
        self.registers = {}
        self.doStackPop = False
        self.doStackPush = False
        self.timeTaken = 0
        self.personality = {}
        self.lastRoom = None
        self.lastTerrain = None
        self.health = 100 # the current health
        self.maxHealth = 100 # the maximum heath a character can have
        self.heatResistance = 0
        self.godMode = False
        self.submenue = None
        self.jobOrders = []
        self.hasOwnAction = 0
        self.doesOwnAction = True

        self.frustration = 0
        self.aggro = 0
        self.numAttackedWithoutResponse = 0

        self.weapon = None
        self.armor = None
        self.flask = None
        self.combatMode = None

        self.interactionState = {}
        self.interactionStateBackup = []

        self.baseDamage = 2
        self.randomBonus = 2
        self.bonusMultiplier = 1
        self.staggered = 0
        self.staggerResistant = False

        self.lastJobOrder = ""
        self.huntkilling = False
        self.guarding = 0

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False
        self.faction = "player"

        self.personality["idleWaitTime"] = random.randint(2, 100)
        self.personality["idleWaitChance"] = random.randint(2, 10)
        self.personality["frustrationTolerance"] = random.randint(-5000, 5000)
        self.personality["autoCounterAttack"] = True
        self.personality["abortMacrosOnAttack"] = True
        self.personality["autoFlee"] = True
        self.personality["autoAttackOnCombatSuccess"] = 0
        self.personality["annoyenceByNpcCollisions"] = random.randint(50, 150)
        self.personality["attacksEnemiesOnContact"] = True
        self.personality["doIdleAction"] = True
        self.personality["avoidItems"] = False
        self.personality["riskAffinity"] = random.random()
        self.personality["viewChar"] = "rank"
        self.personality["viewColour"] = "faction"
        self.personality["moveItemsOnCollision"] = False

        self.silent = False

        self.messages = []

        self.xPosition = xPosition
        self.yPosition = yPosition
        self.burnedIn = False

        self.dutyPriorities = {}

    def getRandomProtisedDuties(self):
        priotisedDuties = {}
        for duty in self.duties:
            priority = self.dutyPriorities.get(duty,1)
            if not priority in priotisedDuties:
                priotisedDuties[priority] = []
            priotisedDuties[priority].append(duty)

        for dutyList in priotisedDuties.values():
            random.shuffle(dutyList)

        resultList = []
        for key in reversed(sorted(priotisedDuties.keys())):
            resultList.extend(priotisedDuties[key])

        return resultList

    def showTextMenu(self,text):
        submenu = src.interaction.TextMenu(text)
        self.macroState["submenue"] = submenu

    def callIndirect(self, callback, extraParams=None):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if extraParams is None:
            extraParams = {}
        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

    def triggerAutoMoveFixedTarget(self,extraParam):
        extraParam["coordinate"] = extraParam["targetCoordinate"]
        self.triggerAutoMoveToTile(extraParam)

    def triggerAutoMoveToTile(self,extraParam):
        """
        makes the character auto move to a given tile
        parameters:
        extraParam["coordinate"]: the coordinate to go to
        """
        targetPosition = extraParam["coordinate"]
        targetPosition = (targetPosition[0],targetPosition[1],0)

        quest = src.quests.questMap["GoToTile"](targetPosition=targetPosition,paranoid=True)
        quest.selfAssigned = True
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()

        self.quests.insert(0,quest)

    def getEmergencyHealth(self):
        """
        gives the charachter an extra health boost, but reduces the characters max health
        """
        if self.maxHealth > 10:
            self.maxHealth -= 10
            self.heal(50)

    def addGrievance(self,grievance):
        """
        stores a grievance for later use
        paramters:
        grievance: the grievance to store
        """
        self.grievances[grievance] = src.gamestate.gamestate.tick

    def weightAttack(self,bigPos):
        """
        generates a rating for attacking a certain tile
        parameters:
        bigPos: the coordinate of the tiles to attack
        returns: the rating for attack. >0 pro attack <0 against attack
        """
        enemiesFound = []

        terrain = self.getTerrain()
        characters = terrain.charactersByTile.get(bigPos,[])

        for otherChar in characters:
            if otherChar == self:
                continue
            if otherChar.faction != self.faction:
                enemiesFound.append(otherChar)

        if enemiesFound:
            challengeRating = 0
            challengeRating -= self.health
            armorValue = 0
            if self.armor:
                armorValue = self.armor.armorValue
            completeDamage = 0
            completeHealth = 0
            for enemyFound in enemiesFound:
                completeDamage += max(0,enemyFound.baseDamage-armorValue)
                completeHealth += enemyFound.health
            ownDamage = self.baseDamage
            if self.weapon:
                ownDamage += self.weapon.baseDamage

            numTurns = completeHealth//ownDamage+1
            challengeRating += numTurns*completeDamage
            return challengeRating

        return -self.health

    def learnSkill(self,skill):
        """
        adds a skill to the characters skills
        (not actively used)
        parameters:
        skill: the skill to add
        """
        if skill not in self.skills:
            self.skills.append(skill)
        self.changed("learnedSkill",self)

    def getOffset(self,position):
        """
        get the offset to a given position
        parameters:
        position: the position to get the offset for
        returns: the offset
        """
        return (self.xPosition-position[0],self.yPosition-position[1],self.zPosition-position[2])

    def getDistance(self,position):
        """
        get the distance to a given position
        parameters:
        position: the position to get the distance to
        returns: the distance to the position
        """
        return abs(self.xPosition-position[0])+abs(self.yPosition-position[1])+abs(self.zPosition-position[2])

    def getBigDistance(self,position):
        """
        get the distance to a given tile
        parameters:
        position: the tile coordinate to get the distance to
        returns: the distance to the tile
        """
        if not isinstance(self.container, src.rooms.Room):
            return abs(self.xPosition//15-position[0])+abs(self.yPosition//15-position[1])+abs(self.zPosition/15-position[2])
        else:
            return abs(self.container.xPosition-position[0])+abs(self.container.yPosition-position[1])+abs(self.container.zPosition-position[2])

    def getFreeInventorySpace(self):
        """
        get the characters free inventory space
        returns: the number of free inventory slots
        """
        return 10-len(self.inventory)

    def getItemWalkable(self,item):
        """
        returns whether or not a given item is walkable or not for this character
        (the intention is to overwrite this)
        returns: whether or not the given item is walkable
        """
        return item.walkable

    def freeWillDecison(self,options,weights,localRandom=random):
        """
        make a decison ases on the characters personality
        (not really used)
        (random choice as placeholder)
        parameters:
            options: the possible options to choose from
            weights: the pre weighting of the options
            localRandom: a non default RNG to use
        returns: the chosen option
        """
        return localRandom.choices(options,weights=weights)

    def getTerrain(self):
        """
        get the terrain the character is on
        returns: the terrain the character is on
        """
        # handle invalid state
        if not self.container:
            return None

        # get the terrain
        if self.container.isRoom:
            terrain = self.container.container
        else:
            terrain = self.container

        # return the terrain
        return terrain

    def getHomeRoom(self):
        """
        fetch the home room for the character
        """

        # get the current terrain
        # (bug: it should not just take the current terrain)
        terrain = self.getTerrain()

        # get the home room
        homeRoom = terrain.getRoomByPosition((self.registers["HOMEx"],self.registers["HOMEy"]))[0]

        # return the home room
        return homeRoom

    def getRoom(self):
        """
        get the room the character is in
        returns: the room
        """

        # set default
        room = None

        # get containing room
        if isinstance(self.container,src.rooms.Room):
            room = self.container

        # return room
        return room

    def startGuarding(self,numTicks):
        """
        put the character into guard mode for som ticks
        parameters:
            numTicks: the number of ticks the character should guard
        """
        self.guarding = numTicks
        self.hasOwnAction += 1

    def getOwnAction(self):
        """
        get an action directly from character state.
        For example attack when guarding.
        This is rarely used.
        This overrides quests,macros and direct keypresses
        returns: the command to run
        """
        foundEnemy = None
        commands = []
        command = None
        if not self.container:
            self.hasOwnAction = 0
            return "."

        for character in self.container.characters:
            if character == self:
                continue
            if character.faction == self.faction:
                continue
            if character.xPosition // 15 != self.xPosition // 15 or character.yPosition // 15 != self.yPosition // 15:
                continue

            foundEnemy = character

            if abs(character.xPosition-self.xPosition) < 2 and abs(character.yPosition-self.yPosition) < 2 and ( abs(character.xPosition-self.xPosition) == 0 or abs(character.yPosition-self.yPosition) == 0):
                command = "m"
                break

            x = character.xPosition
            while x-self.xPosition > 0:
                commands.append("d")
                x -= 1
            x = character.xPosition
            while x-self.xPosition < 0:
                commands.append("a")
                x += 1
            y = character.yPosition
            while y-self.yPosition > 0:
                commands.append("s")
                y -= 1
            y = character.yPosition
            while y-self.yPosition < 0:
                commands.append("w")
                y += 1

        if not command and commands:
            command = random.choice(commands)

        if command == "d":
            pos = self.getPosition()
            if not self.container.getPositionWalkable((pos[0]+1,pos[1],pos[2]),character=self):
                command = "Kdl"
        elif command == "a":
            pos = self.getPosition()
            if not self.container.getPositionWalkable((pos[0]-1,pos[1],pos[2]),character=self):
                command = "Kal"
        elif command == "s":
            pos = self.getPosition()
            if not self.container.getPositionWalkable((pos[0],pos[1]+1,pos[2]),character=self):
                command = "Ksl"
        elif command == "w":
            pos = self.getPosition()
            if not self.container.getPositionWalkable((pos[0],pos[1]-1,pos[2]),character=self):
                command = "Kwl"

        if not foundEnemy:
            self.guarding -= 1
            if self.guarding == 0:
                self.hasOwnAction -= 1

            command = "."
        return command

    def getNearbyEnemies(self):
        """
        gets enemies near the character
        returns: a list of nearby enemies
        """
        return self.container.getEnemiesOnTile(self)

    def getBigPosition_test1(self,offset=None):
        """
        temporary (lol) structure for performance test
        """
        if self.container.isRoom:
            if offset:
                return (self.container.xPosition+offset[0],self.container.yPosition+offset[1],offset[2])
            else:
                return (self.container.xPosition,self.container.yPosition,0)
        else:
            if offset:
                return (self.xPosition//15+offset[0],self.yPosition//15+offset[1],offset[2])
            else:
                return (self.xPosition//15,self.yPosition//15,0)

    def getBigPosition_test2(self,offset=(0,0,0)):
        """
        temporary (lol) structure for performance test
        """
        if self.container.isRoom:
            return (self.container.xPosition+offset[0],self.container.yPosition+offset[1],offset[2])
        else:
            return (self.xPosition//15+offset[0],self.yPosition//15+offset[1],offset[2])

    def getBigPosition(self,offset=None):
        """
        get the coordinate of the tile the character is on
        parameters:
            offset: offset to shift the coordinate by
        """
        if offset:
            self.getBigPosition_test1(offset)
            return self.getBigPosition_test2(offset)
        else:
            self.getBigPosition_test1()
            return self.getBigPosition_test2()

    def getTerrainPosition(self,offset=(0,0,0)):
        """
        get the coordinate of the terrain the character is on
        parameters:
            offset: offset to shift the coordinate by
        """
        terrain = self.getTerrain()
        if not terrain:
            return None
        else:
            return (self.getTerrain().xPosition,self.getTerrain().yPosition,0)

    def huntkill(self):
        """
        set huntkilling mode
        not sure this is really used anymore
        """
        self.addMessage("should start huntkill now")
        self.huntkilling = True

    def doHuntKill(self):
        """
        not sure, it also seems completly dysfunctional
        TODO: wipe this
        """
        targets = []
        for character in self.container.characters:
            if character == self:
                continue
            if character.xPosition // 15 != self.xPosition // 15:
                continue
            if character.yPosition // 15 != self.yPosition // 15:
                continue
            if character.faction == self.faction:
                continue
            targets.append(character)

        if not targets:
            self.huntkilling = False
            return "."

        for target in targets:
            distance = abs(target.xPosition-self.xPosition)+abs(target.yPosition-self.yPosition)
        return None

    def doRangedAttack(self,direction):
        """
        execute a ranged attack
        parameters:
            direction: the direction to do the attack in
        """

        shift = None
        if direction == "w":
            shift = (0,-1)
        if direction == "s":
            shift = (0,1)
        if direction == "a":
            shift = (-1,0)
        if direction == "d":
            shift = (1,0)
        if not shift:
            return

        bolt = None
        for item in self.inventory:
            if item.type == "Bolt":
                bolt = item

        if not bolt:
            self.addMessage("you have no bolt to fire")
            return

        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("shot","actions")

        self.addMessage("you fire a bolt")
        self.inventory.remove(bolt)
        self.timeTaken += 1

        potentialTargets = []
        if direction == "w":
            for character in self.container.characters:
                if character.xPosition == self.xPosition and character.yPosition < self.yPosition and character.yPosition//15 == self.yPosition//15:
                    potentialTargets.append(character)
        if direction == "s":
            for character in self.container.characters:
                if character.xPosition == self.xPosition and character.yPosition > self.yPosition and character.yPosition//15 == self.yPosition//15:
                    potentialTargets.append(character)
        if direction == "a":
            for character in self.container.characters:
                if character.yPosition == self.yPosition and character.xPosition < self.xPosition and character.xPosition//15 == self.xPosition//15:
                    potentialTargets.append(character)
        if direction == "d":
            for character in self.container.characters:
                if character.yPosition == self.yPosition and character.xPosition > self.xPosition and character.xPosition//15 == self.xPosition//15:
                    potentialTargets.append(character)

        newPos = list(self.getPosition())
        newPos[0] += shift[0]
        newPos[1] += shift[1]

        while newPos[0]//15 == self.xPosition//15 and newPos[1]//15 == self.yPosition//15:
            if self.container.isRoom and (newPos[0] > 12 or newPos[1] > 12):
                break

            self.container.addAnimation(tuple(newPos),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"++")})

            for item in self.container.getItemByPosition(tuple(newPos)):
                if not item.walkable:
                    self.addMessage(f"the bolt hits {item.type}")
                    item.destroy()
                    return

            for character in potentialTargets:
                if character.getPosition() == tuple(newPos):
                    self.addMessage("the bolt hits somebody for 50 damage")
                    character.hurt(50,reason="got hit by a bolt",actor=character)
                    return

            newPos[0] += shift[0]
            newPos[1] += shift[1]

        self.addMessage("the bolt vanishes into the static")

    def setDefaultMacroState(self):
        """
        resets the macro automation state
        """

        import time

        self.macroState = {
            "commandKeyQueue": [],
            "state": [],
            "recording": False,
            "recordingTo": None,
            "replay": [],
            "loop": [],
            "number": None,
            "doNumber": False,
            "macros": {},
            "shownStarvationWarning": False,
            "lastLagDetection": time.time(),
            "lastRedraw": time.time(),
            "idleCounter": 0,
            "ignoreNextAutomated": False,
            "ticksSinceDeath": None,
            "footerPosition": 0,
            # "footerLength":len(footerText),
            "footerSkipCounter": 20,
            "itemMarkedLast": None,
            "lastMoveAutomated": False,
            "stealKey": {},
            "submenue": None,
        }

    def getPosition(self,offset=(0,0,0)):
        """
        returns the characters position

        Returns:
            the position
        """

        return self.xPosition+offset[0], self.yPosition+offset[1], self.zPosition+offset[2]

    def getTilePosition(self,offset=(0,0,0)):
        """
        returns the characters position

        Returns:
            the position
        """
        if self.container.isRoom:
            return self.container.getTilePosition(offset=offset)
        else:
            return (self.xPosition//15+offset[0], self.yPosition//15+offset[1], self.zPosition//15+offset[2])

    def getSpacePosition(self,offset=(0,0,0)):
        """
        returns the characters position

        Returns:
            the position
        """
        if not self.container:
            logger.error("getting position of character that is nowhere")
            return

        if self.container.isRoom:
            return (self.xPosition+offset[0], self.yPosition+offset[1], self.zPosition+offset[2])
        else:
            return (self.xPosition%15+offset[0], self.yPosition%15+offset[1], self.zPosition%15+offset[2])

    def searchInventory(self, itemType, extra=None):
        """
        return a list of items from the characters inventory that satisfy some conditions

        Parameters:
            itemType: the item type
            extra: extra conditions
        """

        if extra is None:
            extra = {}
        foundItems = []
        for item in self.inventory:
            if item.type != itemType:
                continue

            if extra.get("uses") and not item.uses >= extra.get("uses"):
                continue
            foundItems.append(item)
        return foundItems

    def addMessage(self, message):
        """
        add a message to the characters message log
        basically only for player UI

        Parameters:
            message: the message
        """

        self.messages.append(str(message))

    def convertCommandString(self,commandString,nativeKey=False, extraFlags=None):
        """
        convert a command sting into a list of commands
        !!! seems to not be in actual use, see convertCommandString2
        Parameters:
            commandString: the command to convert
            nativeKey: wether or not the keys should be handled as actual keypresses
            extraFlags: additional extra flags
        Returns:
            the list of converted commands
        """

        # convert command to macro data structure
        if nativeKey:
            flags = []
        else:
            flags = ["norecord"]
        if extraFlags:
            flags.extend(extraFlags)

        """
        convertedCommand = []
        for char in reversed(commandString):
            if char == "\n":
                char = "enter"

            convertedCommand.append((char, flags))
        """
        """

        self.flags = flags
        convertedCommand = list(map(self.convertSingleCommand,reversed(commandString)))
        self.flags = None
        """
        convertedCommand = list(map(lambda char: ("enter",flags) if char == "\n" else (char,flags), reversed(commandString)))
        return convertedCommand

    def convertCommandString2(self,commandString,nativeKey=False, extraFlags=None):
        """
        convert a command sting into a list of commands
        Parameters:
            commandString: the command to convert
            nativeKey: wether or not the keys should be handled as actual keypresses
            extraFlags: additional extra flags
        Returns:
            the list of converted commands
        """

        # convert command to macro data structure
        if extraFlags:
            if nativeKey:
                flags = []
            else:
                flags = ["norecord"]
            flags.extend(extraFlags)
            flags = tuple(flags)
        else:
            if nativeKey:
                flags = ()
            else:
                flags = ("norecord")

        """
        convertedCommand = []
        for char in reversed(commandString):
            if char == "\n":
                char = "enter"

            convertedCommand.append((char, flags))
        """
        """

        self.flags = flags
        convertedCommand = list(map(self.convertSingleCommand,reversed(commandString)))
        self.flags = None
        """
        convertedCommand = [(item,flags) for item in reversed(commandString)]
        return convertedCommand

    def runCommandString(self, commandString, clear=False, addBack=False, nativeKey=False, extraFlags=None, preconverted=False):
        """
        run a command using the macro automation

        Parameters:
            commandString: the command
            clear: wether or not to clear previous commands
            addBack: wether or not to add the commands to the back off the queue
            nativeKey: wether or not to register the command as actual keypress
            extraFlag: extra flags for the keypresses
            preconverted: wether or not the command is already in the internal format
        """

        if preconverted:
            convertedCommand = commandString
        else:
            convertedCommand = self.convertCommandString2(commandString,nativeKey,extraFlags)

        if not clear:
            oldCommand = self.macroState["commandKeyQueue"]
        else:
            oldCommand = []

        # add command to the characters command queue
        if not addBack:
            self.macroState["commandKeyQueue"] = oldCommand + convertedCommand
        else:
            self.macroState["commandKeyQueue"] = convertedCommand + oldCommand

        """
        if len(self.macroState["commandKeyQueue"]) > 100:
            self.macroState["commandKeyQueue"] = self.macroState["commandKeyQueue"][0:100]
        """

    def getCommandString(self):
        """
        returns the character command string
        probably disused

        Returns:
            the command string
        """

        return self.macroState["commandKeyQueue"]

    def clearCommandString(self):
        """
        clear macro automation command queue
        """
        self.macroState["commandKeyQueue"] = []

    def addJobOrder(self, jobOrder):
        """
        add a job order to the characters queue of job orders and run it

        Parameters:
            jobOrder: the job order to run
        """

        self.jobOrders.append(jobOrder)
        self.runCommandString("Jj.j")

    def hurt(self, damage, reason=None, actor=None):
        """
        hurt the character

        Parameters:
            damage: the amount of damage dealt
            reason: the reason damage was dealt
            actor: the character causing the damage
        """

        if self.disabled:
            self.disabled = False

        if self.addExhaustionOnHurt:
            self.exhaustion += damage//10+1
        if self.addRandomExhaustionOnHurt:
            #self.exhaustion += int(damage//4)
            self.exhaustion += int(random.random()*damage//2)

        if reason == "attacked":
            if self.aggro < 20:
                self.aggro += 5
            if self.personality.get("abortMacrosOnAttack") and not self.macroState["submenue"]:
                self.clearCommandString()
            if self.personality.get("autoCounterAttack") and not self.macroState["submenue"]:
                self.runCommandString("m")
            if self.personality.get("autoRun") and not self.macroState["submenue"]:
                self.runCommandString(random.choice(["a", "w", "s", "d"]))

            self.numAttackedWithoutResponse += 1
            #damage += self.numAttackedWithoutResponse

        if self.armor:
            damageAbsorbtion = self.armor.getArmorValue(reason)

            if self.combatMode == "defensive":
                damageAbsorbtion += 2
                self.addMessage("passive combat bonus")

            self.addMessage(f"your armor absorbs {damageAbsorbtion} damage")
            damage -= damageAbsorbtion

            self.container.addAnimation(self.getPosition(),"shielded",damageAbsorbtion,{})
            self.container.addAnimation(self.getPosition(),"shielded",damageAbsorbtion,{})


        if damage <= 0:
            return

        if self.health - damage > 0:
            if src.gamestate.gamestate.mainChar in self.container.characters:
                src.interaction.playSound("hurt","actions")

            staggerThreshold = self.health // 4 + 1

            self.container.addAnimation(self.getPosition(),"hurt",damage,{"maxHealth":self.maxHealth,"mainChar":self==src.gamestate.gamestate.mainChar,"health":self.health})

            self.health -= damage
            self.frustration += 10 * damage
            self.addMessage("you took " + str(damage) + f" damage. You have {self.health}/{self.maxHealth} health left")

            if self.combatMode == "defensive":
                staggerThreshold *= 2
            if damage > staggerThreshold:
                #self.addMessage("you stager")
                self.staggered += damage // staggerThreshold

            if reason:
                self.addMessage(f"reason: {reason}")

            """
            if self.health < self.maxHealth//10 or (self.health < 50 and self.health < self.maxHealth):
                self.addMessage("you are hurt you should heal")
                for item in self.inventory:
                    if not item.type == "Vial":
                        continue
                    if not item.uses:
                        continue
                    self.runCommandString("JH")
            """
        else:
            self.health = 0
            self.die(reason="you died from injuries")

    def getNumMaxPosSubordinates(self):
        """
        get the maximum number of subordinates allowed for this character
        return: the number of subordinates allowed
        """
        if self.rank == 5:
            return 1
        if self.rank == 4:
            return 2
        if self.rank == 3:
            return 3
        return 0

    def getNumSubordinates(self):
        """
        get the number of subordinates controlled by this character
        return: the number of subordinates
        """
        return len(self.subordinates)

    def getIsHome(self):
        """
        get wether or not this character is at home
        Returns:
            wether or not this character is at home
        """
        charPos = self.getBigPosition()
        return (self.registers.get("HOMEx"), self.registers.get("HOMEy"), 0) == charPos

    def selectSpecialAttack(self,target):
        """
        spawn the submenu to trigger a special attack
        Parameters:
            target: the target of the attack
        """

        attacksOffered = ["h","j","k","l"]

        attacksOffered.append(random.choice(["u","i","o","g","b"]))

        text = ""
        if "o" in attacksOffered:
            text += """
press o/O for attack of opportunity
-exhaustion: +1 -damage multiplier: 1.5
"""
        if "g" in attacksOffered:
            text += """
press g/G for gambling attack
-exhaustion: +2 -damage multiplier: random(0,3)
"""
        if "b" in attacksOffered:
            text += """
press b/B for bestial attack
-exhaustion: random(0,10) -damage multiplier: 2
"""
        if "n" in attacksOffered:
            text += """
press n/N for exhausting attack
-exhaustion: +4 -enemy exhaustion: +11 -damage multiplier: 0
"""
        if "i" in attacksOffered:
            text += """
press i/I for quick attack
-exhaustion: +1 -damage multiplier: 0.5 -attack speed multiplier: 0.5
"""
        if "u" in attacksOffered:
            text += """
press u/U for slow attack
-exhaustion: -1 -attack speed multiplier: 1.5
"""

        text += "\n"

        if "h" in attacksOffered:
            text += """
press h/H for heavy attack
-exhaustion: +3 -damage multiplier: 1.5
"""
        if "j" in attacksOffered:
            text += """
press j/J for ultraheavy attack
-exhaustion: +25 -damage multiplier: 3
requires: exhaustion < 10
"""
        if "k" in attacksOffered:
            text += """
press k/K for initial strike
-exhaustion: +1 -damage multiplier: 3
requires: no exhaustion
"""
        if "l" in attacksOffered:
            text += """
press l/L for light attack
-exhaustion: -5 -damage multiplier: 0.5
"""


        text += """

press any other key to attack normally"""
        submenu = src.interaction.OneKeystrokeMenu(text)

        self.macroState["submenue"] = submenu
        self.macroState["submenue"].followUp = {"container":self,"method":"doSpecialAttack","params":{"target":target}}
        self.runCommandString("~",nativeKey=True)

    def doSpecialAttack(self,extraParam):
        """
        do a special attack on a target
        this method assumes to be called by a submenu
        Parameters:
            extraParam["target"]: the target of the attack
            extraParam["KeyPressed"]: the type of the special attack
        """

        target = extraParam["target"]
        if 1==0:
            pass
        elif extraParam["keyPressed"] in ("o","O",):
            self.addMessage("you do an attack of opportunity")
            self.attack(target,opportunity=True)
        elif extraParam["keyPressed"] in ("g","G",):
            self.addMessage("you do an gambling attack")
            self.attack(target,gambling=True)
        elif extraParam["keyPressed"] in ("b","B",):
            self.addMessage("you do an bestial attack")
            self.attack(target,bestial=True)
        elif extraParam["keyPressed"] in ("n","N",):
            self.addMessage("you do a harassing attack")
            self.attack(target,harassing=True)
        elif extraParam["keyPressed"] in ("i","I",):
            self.addMessage("you do a quick attack")
            self.attack(target,quick=True)
        elif extraParam["keyPressed"] in ("u","U",):
            self.addMessage("you do a slow attack")
            self.attack(target,slow=True)
        elif extraParam["keyPressed"] in ("h","H",):
            self.addMessage("you do a heavy attack")
            self.attack(target,heavy=True)
        elif extraParam["keyPressed"] in ("j","J",):
            self.addMessage("you do a ultraheavy attack")
            self.attack(target,ultraheavy=True)
        elif extraParam["keyPressed"] in ("k","K",):
            self.addMessage("you do a initial strike")
            self.attack(target,initial=True)
        elif extraParam["keyPressed"] in ("l","L",):
            self.addMessage("you do a light attack")
            self.attack(target,light=True)
        else:
            self.addMessage("you do a normal attack")
            self.attack(target)

    def attack(self, target, heavy = False, quick = False, ultraheavy = False, initial=False, harassing=False, light=False, opportunity=False, gambling=False, bestial=False, slow=False):
        """
        make the character attack something

        Parameters:
            target: the target to attack
            heavy: wether or not the attack should be a heavy attack
            quick: wether or not the attack should be a quick attack
            ultraheavy: wether or not the attack should be a ultraheavy attack
            initial: wether or not the attack should be an initial attack
            harassing: wether or not the attack should be a harassing attack
            light: wether or not the attack should be a light attack
            opportunity: wether or not the attack should be a attack of opportunity
            gambling: wether or not the attack should be a gambling attack
            bestial: wether or not the attack should be a bestial attack
            slow: wether or not the attack should be a slow attack
        """
        if self.dead:
            return

        if target.dead:
            if not target.container:
                while target in self.container.characters:
                    self.container.characters.remove(target)

                if isinstance(self.container,src.terrains.Terrain):
                    cachedList = self.container.charactersByTile.get(self.getBigPosition(),[])
                    while target in cachedList:
                        cachedList.remove(target)
            else:
                self.container.removeCharacter(target)
            logger.error("killed ghost")
            return

        if initial and self.exhaustion > 0:
            self.addMessage("you are too exhausted to do an initial attack")
            initial = False

        if ultraheavy and self.exhaustion >= 10:
            self.addMessage("you are too exhausted to do an ultraheavy attack")
            ultraheavy = False

        speed = self.attackSpeed
        if quick:
            speed *= 0.5
        if slow:
            speed *= 1.5
        else:
            self.timeTaken += self.attackSpeed/2
        self.timeTaken += speed

        if self.numAttackedWithoutResponse > 2:
            self.numAttackedWithoutResponse = int(self.numAttackedWithoutResponse/2)
        else:
            self.numAttackedWithoutResponse = 0

        baseDamage = self.baseDamage

        if self.weapon:
            baseDamage += self.weapon.baseDamage
            modifier = 1
            if heavy:
                modifier += 10
            if ultraheavy:
                modifier += 20
            self.weapon.degrade(multiplier=modifier,character=self)

        if self.exhaustion > 10:
            baseDamage = baseDamage//2

        if heavy:
            baseDamage = int(baseDamage*1.5)

        if opportunity:
            baseDamage = int(baseDamage*1.5)

        if ultraheavy:
            baseDamage = int(baseDamage*3)

        if initial:
            baseDamage = int(baseDamage*3)

        if gambling:
            baseDamage = int(baseDamage*random.random()*3)

        if bestial:
            baseDamage = int(baseDamage*2)

        damage = baseDamage

        if self.bonusDamageOnLowerExhaustion and self.exhaustion < target.exhaustion:
            damage = damage + damage//2

        if self.doubleDamageOnZeroExhaustion and self.exhaustion == 0:
            damage = damage * 2

        if self.reduceDamageOnAttackerExhausted and self.exhaustion//10:
            damage = damage//(self.exhaustion//10+1)

        if self.increaseDamageOnTargetExhausted and target.exhaustion//10:
            damage = damage * (target.exhaustion//10+1)

        if quick:
            damage = damage//2
        if light:
            damage = damage//2
        if harassing:
            damage = 0

        self.container.addAnimation(target.getPosition(),"attack",damage,{})

        target.hurt(damage, reason="attacked", actor=self)
        self.addMessage(
            f"you attack the enemy for {damage} damage, the enemy has {target.health}/{target.maxHealth} health left"
        )

        if self.addRandomExhaustionOnAttack:
            self.exhaustion += random.randint(1,4)

        self.exhaustion += self.flatExhaustionAttackCost

        if heavy:
            self.exhaustion += 3
            #self.exhaustion += self.exhaustion*2
        if opportunity:
            self.exhaustion += 1
        if quick:
            self.exhaustion += 1
        if slow:
            self.exhaustion -= 1
        if ultraheavy:
            self.exhaustion += 25
        if initial:
            self.exhaustion += 1
        if harassing:
            self.exhaustion += 4
            target.exhaustion += 11
        if light:
            self.exhaustion = max(0,self.exhaustion-5)
        if gambling:
            self.exhaustion += 2
        if bestial:
            self.exhaustion += random.randint(0,10)

        if self.personality.get("autoAttackOnCombatSuccess") and not self.submenue and not self.charState["submenue"]:
            self.runCommandString(
                "m" * self.personality.get("autoAttackOnCombatSuccess")
            )
            self.addMessage("auto attack")

        self.addMessage(f"exhaustion: you {self.exhaustion} enemy {target.exhaustion}")

    def heal(self, amount, reason=None):
        """
        heal the character

        Parameters:
            amount: the amount of health healed
            reason: the reason why the character was healed
        """
        amount = int(amount*self.healingModifier)
        if not amount:
            return

        #if self.reduceExhaustionOnHeal:
        #    self.exhaustion = max(0,self.exhaustion-(amount//self.reduceExhaustionDividend+self.reduceExhaustionBonus))
        #if self.removeExhaustionOnHeal:
        #    self.exhaustion = 0

        if self.maxHealth - self.health < amount:
            amount = self.maxHealth - self.health

        self.health += amount
        self.addMessage(f"you heal for {amount} and have {self.health} health")

    # bad code: only works in a certain room type
    def collidedWith(self, other, actor=None):
        """
        handle collision with another character

        Parameters:
            other: the other character
            actor: the character triggering the collision
        """

        if other.faction != self.faction:
            if self.personality.get("attacksEnemiesOnContact") and actor == self:
                self.attack(other)
        else:
            if self.personality.get("annoyenceByNpcCollisions"):
                self.frustration += self.personality.get("annoyenceByNpcCollisions")

    def getRegisterValue(self, key):
        """
        load a value from the characters data store (register)

        Parameters:
            key: the name of the register to fetch
        """

        try:
            return self.registers[key][-1]
        except KeyError:
            return None

    def setRegisterValue(self, key, value):
        """
        set a value in the characters data store (register)

        Parameters:
            key: the name of the register to fetch
            value: the value to set in the register
        """
        if key not in self.registers:
            self.registers[key] = [0]
        self.registers[key][-1] = value

    # bad code: should just be removed
    @property
    def display(self):
        """
        proxy render method to display attribute
        """
        return self.render()

    def render(self):
        """
        render the character
        """
        if self.unconcious:
            return src.canvas.displayChars.unconciousBody
        else:
            return self.displayOriginal

    # bad code: should be actual attribute
    @property
    def container(self):
        """
        the object the character is in. Either room or terrain
        """
        if self.room:
            return self.room
        else:
            return self.terrain

    def getActiveQuest(self):
        """
        returns the currently active quest
        Returns:
            the active quest
        """
        if self.quests:
            return self.quests[0].getActiveQuest()
        return None

    def getActiveQuests(self):
        """
        returns the currently active quest and all its parents
        Returns:
            a list of the active quest and its parents
        """
        if self.quests:
            return self.quests[0].getActiveQuests()
        return []

    # bad code: should be removed
    def getQuest(self):
        """
        get a quest from the character (proxies room quest queue)
        """
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    def addEvent(self, event):
        """
        add an event to the characters event queue

        Parameters:
            event: the event to add
        """

        # get the position for this event
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1

        # add event at proper position
        self.events.insert(index, event)

    # bad code: should be removed
    def recalculatePath(self):
        """
        reset the path to the current quest
        """

        # log impossible state
        if not self.quests:
            logger.debug("recalculate path called without quests")
            self.path = []
            return

        # reset path
        self.setPathToQuest(self.quests[0])

    def removeEvent(self, event):
        """
        removes an event from the characters event queue

        Parameters:
            event: the event to remove
        """
        self.events.remove(event)

    # bad code: adds default chat options
    def getChatOptions(self, partner):
        """
        fetch the chat options the character offers

        Parameters:
            partner: the chat partner

        Returns:
            the chat options
        """

        # get the usual chat options
        chatOptions = self.basicChatOptions[:]

        if not self.silent:
            # add chat for recruitment
            if self not in partner.subordinates:
                chatOptions.append(src.chats.RecruitChat)
                pass
            if partner not in self.subordinates:
                chatOptions.append(
                    {
                        "dialogName": "may i serve you?",
                        "chat": src.chats.RoomDutyChat,
                        "params": {"superior": self},
                    }
                )
            else:
                chatOptions.append(
                    {
                        "dialogName": "can i do something for you?",
                        "chat": src.chats.RoomDutyChat2,
                        "params": {"superior": self},
                    }
                )
            if self.isMilitary:
                chatOptions.append(
                    {
                        "dialogName": "I want to join the military",
                        "chat": src.chats.JoinMilitaryChat,
                        "params": {"superior": self},
                    }
                )

        return chatOptions

    def awardReputation(self, amount=0, fraction=0, reason=None, carryOver=False):
        """
        give the character reputation (reward)

        Parameters:
            amount: how much fixed reputation was awarded
            fraction: how much relative reputation was awarded
            reason: the reason for awarding reputation
        """

        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation // fraction
        self.reputation += totalAmount

        text = "you were rewarded %i reputation" % totalAmount
        if reason:
            text += " for " + reason
        self.addMessage(text)

        if carryOver and hasattr(self,"superior") and self.superior:
            #newAmount = amount//4
            newAmount = amount
            self.superior.awardReputation(amount=newAmount,fraction=fraction,reason=reason,carryOver=carryOver)

    def revokeReputation(self, amount=0, fraction=0, reason=None, carryOver=False):
        """
        remove some of the character reputation (punishment)

        Parameters:
            amount: how much fixed reputation was removed
            fraction: how much relative reputation was removed
            reason: the reason for awarding reputation
        """

        totalAmount = amount
        if fraction and self.reputation:
            totalAmount += self.reputation // fraction
        self.reputation -= totalAmount

        text = "you lost %i reputation" % totalAmount
        if reason:
            text += " for " + reason
        self.addMessage(text)

        if carryOver and hasattr(self,"superior") and self.superior:
            #newAmount = amount//4
            newAmount = amount
            self.superior.revokeReputation(amount=newAmount,fraction=fraction,reason=reason,carryOver=carryOver)

    # obsolete: reintegrate
    # bad code: this is kind of incompatible with the meta quests
    def startNextQuest(self):
        """
        starts the next quest in the quest list
        """

        if len(self.quests):
            self.quests[0].recalculate()
            self.setPathToQuest(self.quests[0])

    def getDetailedInfo(self):
        """
        returns a string with detailed info about the character

        Returns:
            the string
        """

        return (
            "name: "
            + str(self.name)
            + "\nroom: "
            + str(self.room)
            + "\ncoordinate: "
            + str(self.xPosition)
            + " "
            + str(self.yPosition)
            + "\nsubordinates: "
            + str(self.subordinates)
            + "\nsat: "
            + str(self.satiation)
            + "\nreputation: "
            + str(self.reputation)
            + "\ntick: "
            + str(src.gamestate.gamestate.tick)
            + "\nfaction: "
            + str(self.faction)
        )

    # bad code: this is kind of incompatible with the meta quests
    # obsolete: reintegrate
    def assignQuest(self, quest, active=False):
        """
        adds a quest to the characters quest list

        Parameters:
            quest: the quest to add
            active: a flag indication if the quest should be added as active
        """

        if active:
            self.quests.insert(0, quest)
        else:
            self.quests.append(quest)
        quest.assignToCharacter(self)
        quest.activate()
        if active or len(self.quests) == 1:
            if self.quests[0] == quest:
                self.setPathToQuest(quest)

    # bad pattern: path should be determined by a quests solver
    # bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    # obsolete: probably should be rewritten
    def setPathToQuest(self, quest):
        """
        set the charactes path to a quest

        Parameters:
            quest: the quest to set the path from
        """
        self.path = [] # disabled
        return

        if hasattr(quest, "dstX") and hasattr(quest, "dstY") and self.container:
            self.path = self.container.findPath(
                (self.xPosition, self.yPosition), (quest.dstX, quest.dstY)
            )
        else:
            self.path = []

    def addToInventory(self, item, force=False):
        """
        add an item to the characters inventory

        Parameters:
            item: the item
            force: flag overriding sanity checks
        """

        if force or len(self.inventory) < self.maxInventorySpace:
            self.inventory.append(item)
        else:
            self.addMessage("inventory full")

    def removeItemFromInventory(self, item):
        """
        remove an item from the characters inventory

        Parameters:
            item: the item
        """

        self.removeItemsFromInventory([item])

    def removeItemsFromInventory(self, items):
        """
        remove items from the characters inventory

        Parameters:
            items: a list of items to remove
        """

        for item in items:
            self.inventory.remove(item)

    # obsolete: should probably rewritten
    # bad code: should be handled in quest
    def applysolver(self, solver=None):
        """
        this wrapper converts a character centered call to a solver centered call

        Parameters:
            solver: a custom solver to use
        """

        if self.disableCommandsOnPlus:

            hasComand = False
            quest = self.getActiveQuest()
            if quest.getSolvingCommandString(self):
                hasComand = True

            if hasComand:
                hasAutoSolve = False
                for quest in self.getActiveQuests():
                    if quest.autoSolve:
                        hasAutoSolve = True

                if not hasAutoSolve:
                    self.runCommandString(".")
                    return

        if not solver and self.quests:
            self.quests[0].solver(self)
            return
        return

    # bad code: obsolete
    def fallUnconcious(self):
        """
        make the character fall unconcious
        """

        self.unconcious = True
        if self.watched:
            self.addMessage("*thump,snort*")
        self.changed("fallen unconcious", self)

    # bad code: obsolete
    def wakeUp(self):
        """
        wake the character up
        """

        self.unconcious = False
        if self.watched:
            self.addMessage("*grown*")
        self.changed("woke up", self)

    def die(self, reason=None, addCorpse=True):
        """
        kill the character and do a bit of extra stuff like placing corpses

        Parameters:
            reason: the reason for dieing
            addCorpse: flag to control adding a corpse
        """
        self.changed("died_pre", {"character": self, "reason": reason})
        self.quests = []

        self.lastRoom = self.room
        self.lastTerrain = self.terrain

        if src.gamestate.gamestate.mainChar == self:
            src.interaction.playSound("playerDeath","importantActions")

        # replace character with corpse
        container = None
        if self.container:
            container = self.container
            pos = self.getPosition()
            container.removeCharacter(self)
            if addCorpse:
                for item in self.inventory:
                    container.addItem(item, pos)

                if self.weapon:
                    container.addItem(self.weapon, pos)
                    self.weapon = None
                if self.armor:
                    container.addItem(self.armor, pos)
                    self.armor = None
                if self.flask:
                    container.addItem(self.flask, pos)
                    self.flask = None

                corpse = src.items.itemMap["Corpse"]()
                container.addItem(corpse, pos)

            if src.gamestate.gamestate.mainChar in container.characters:
                src.interaction.playSound("enemyDied","actions")

        # log impossible state
        else:
            logger.debug("this should not happen, character died without being somewhere (%s)", self)

        self.macroState["commandKeyQueue"] = []

        # set attributes
        self.addMessage("you died.")
        self.dead = True
        if reason:
            self.deathReason = reason
            self.addMessage(f"cause of death: {reason}")
        self.path = []

        # notify listeners
        self.changed("died", {"character": self, "reason": reason})

        if container:
            # notify nearby characters
            for otherCharacter in container.characters:
                if otherCharacter.xPosition//15 == self.xPosition//15 and otherCharacter.yPosition//15 == self.yPosition//15:
                    otherCharacter.changed("character died on tile",{"deadChar":self,"character":otherCharacter})

    def canHeal(self):
        """
        check if the character can heal right now
        Returns:
            wether or not the character can heal right now
        """
        for item in self.inventory:
            if not isinstance(item,src.items.itemMap["Vial"]):
                continue
            if not item.uses:
                continue
            return True
        return False

    # obsolete: needs to be reintegrated
    # bad pattern: should be contained in quest solver
    def walkPath(self):
        """
        walk the predetermined path
        Returns:
            True when done
            False when not done
        """

        # smooth over impossible state
        if self.dead:
            logger.debug("dead men walking")
            return None
        if not self.path:
            self.setPathToQuest(self.quests[0])
            logger.debug("walking without path")

        # move along the predetermined path
        currentPosition = (self.xPosition, self.yPosition)
        if not (self.path and self.path != [currentPosition]):
            return True

        # get next step
        nextPosition = self.path[0]

        item = None
        # try to move within a room
        if self.room:
            # move naively within a room
            if (
                nextPosition[0] == currentPosition[0]
                and nextPosition[1] == currentPosition[1] - 1
            ):
                item = self.room.moveCharacterDirection(self, "north")
            if (
                nextPosition[0] == currentPosition[0]
                and nextPosition[1] == currentPosition[1] + 1
            ):
                item = self.room.moveCharacterDirection(self, "south")
            elif (
                nextPosition[0] == currentPosition[0] - 1
                and nextPosition[1] == currentPosition[1]
            ):
                item = self.room.moveCharacterDirection(self, "west")
            elif (
                nextPosition[0] == currentPosition[0] + 1
                and nextPosition[1] == currentPosition[1]
            ):
                item = self.room.moveCharacterDirection(self, "east")
            else:
                # smooth over impossible state
                if not src.interaction.debug:
                    # resorting to teleport
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                else:
                    logger.debug("character moved on non-continuous path")
        # try to move within a terrain
        else:
            # check if a room was entered
            # basically checks if a walkable space/door is within a room on the coordinate the character walks on. If there is something in the way, an item it will be saved for interaction.
            # bad pattern: collision detection and room teleportation should be done in terrain

            for room in self.terrain.rooms:
                """
                helper function to move a character into a direction
                """

                def moveCharacter(localisedEntry, direction):
                    if localisedEntry in room.walkingAccess:

                        # check whether the character walked into something
                        if localisedEntry in room.itemByCoordinates:
                            for listItem in room.itemByCoordinates[localisedEntry]:
                                if not listItem.walkable:
                                    return listItem

                        # teleport the character into the room
                        room.addCharacter(self, localisedEntry[0], localisedEntry[1])
                        self.terrain.characters.remove(self)
                        self.terrain = None
                        return None
                    else:
                        # show message the character bumped into a wall
                        # bad pattern: why restrict the player to standard entry points?
                        self.addMessage("you cannot move there (" + direction + ")")
                        return None

                # handle the character moving into the rooms boundaries
                # bad code: repetitive, confusing code
                # check north
                if (
                    room.yPosition * 15 + room.offsetY + room.sizeY
                    == nextPosition[1] + 1
                ) and (
                    room.xPosition * 15 + room.offsetX < self.xPosition
                    and room.xPosition * 15 + room.offsetX + room.sizeX
                    > self.xPosition
                ):
                    # try to move character
                    localisedEntry = (
                        self.xPosition % 15 - room.offsetX,
                        nextPosition[1] % 15 - room.offsetY,
                    )
                    item = moveCharacter(localisedEntry, "north")
                    break
                # check south
                if room.yPosition * 15 + room.offsetY == nextPosition[1] and (
                    room.xPosition * 15 + room.offsetX < self.xPosition
                    and room.xPosition * 15 + room.offsetX + room.sizeX
                    > self.xPosition
                ):
                    # try to move character
                    localisedEntry = (
                        (self.xPosition - room.offsetX) % 15,
                        ((nextPosition[1] - room.offsetY) % 15),
                    )
                    item = moveCharacter(localisedEntry, "south")
                    break
                # check east
                if (
                    room.xPosition * 15 + room.offsetX + room.sizeX
                    == nextPosition[0] + 1
                ) and (
                    room.yPosition * 15 + room.offsetY < self.yPosition
                    and room.yPosition * 15 + room.offsetY + room.sizeY
                    > self.yPosition
                ):
                    # try to move character
                    localisedEntry = (
                        (nextPosition[0] - room.offsetX) % 15,
                        (self.yPosition - room.offsetY) % 15,
                    )
                    item = moveCharacter(localisedEntry, "east")
                    break
                # check west
                if room.xPosition * 15 + room.offsetX == nextPosition[0] and (
                    room.yPosition * 15 + room.offsetY < self.yPosition
                    and room.yPosition * 15 + room.offsetY + room.sizeY
                    > self.yPosition
                ):
                    # try to move character
                    localisedEntry = (
                        (nextPosition[0] - room.offsetX) % 15,
                        (self.yPosition - room.offsetY) % 15,
                    )
                    item = moveCharacter(localisedEntry, "west")
                    break
            else:
                # move the char to the next position on path
                self.xPosition = nextPosition[0]
                self.yPosition = nextPosition[1]

        # handle bumping into an item
        if item:
            # open doors
            # bad pattern: this should not happen here
            if isinstance(item, src.items.Door):
                item.apply(self)
            return False

        # smooth over impossible state
        else:
            if not src.interaction.debug and (not self.path or nextPosition != self.path[0]):
                return False

            # remove last step from path
            if self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]:
                self.path = self.path[1:]
        return False

    def drop(self, item=None, position=None):
        """
        make the character drop an item

        Parameters:
            item: the item to drop
            position: the position to drop the item on
        """

        if not self.inventory:
            self.addMessage("no item to drop")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            if position:
                self.container.addAnimation(position,"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            return

        if not item:
            item = self.inventory[-1]

        foundScrap = None

        if not position:
            position = self.getPosition()

        itemList = self.container.getItemByPosition(position)

        if item.walkable is False and len(itemList):
            self.addMessage("you need a clear space to drop big items")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            if position:
                self.container.addAnimation(position,"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        if len(itemList) > 25:
            self.addMessage("you can not put more items there")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            if position:
                self.container.addAnimation(position,"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        foundBig = False

        for compareItem in itemList:
            if compareItem.type == "Scrap":
                foundScrap = compareItem
            if compareItem.walkable is False and not (
                compareItem.type == "Scrap" and compareItem.amount < 15
            ):
                foundBig = True
                break

        if foundBig:
            self.addMessage("there is no space to drop the item")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
            if position:
                self.container.addAnimation(position,"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
            return

        self.addMessage("you drop a %s" % item.type)

        # remove item from inventory
        self.inventory.remove(item)
        self.container.addAnimation(self.getPosition(),"charsequence",1,{"chars":["--",item.render()]})

        if src.gamestate.gamestate.mainChar in self.container.characters:
            src.interaction.playSound("itemDropped","actions")

        if foundScrap and item.type == "Scrap":
            foundScrap.amount += item.amount
            foundScrap.setWalkable()
            self.container.addAnimation(foundScrap.getPosition(),"scrapChange",1,{})
            item = foundScrap
        else:
            # add item to floor
            self.container.addItem(item, position, actor=self)
            self.container.addAnimation(position,"charsequence",1,{"chars":[item.render(),"++"]})

        self.changed("dropped",(self,item))

    def examinePosition(self, pos):
        """
        examine a position
        show a menu displaying a description

        Parameters:
            pos: the position to examine
        """
        text = f"you are examining the position: {pos}\n\n"

        if isinstance(self.container,src.rooms.Room):
            room = self.container

            text += "special fields:\n"
            found = False
            if pos in room.walkingSpace:
                found = True
                text += "is walking space\n"
            for inputSlot in room.inputSlots:
                if pos == inputSlot[0]:
                    found = True
                    text += f"is input slot for {inputSlot[1]} ({inputSlot[2]})\n"
            for outputSlot in room.outputSlots:
                if pos == outputSlot[0]:
                    found = True
                    text += f"is output slot for {outputSlot[1]} ({outputSlot[2]})\n"
            for storageSlot in room.storageSlots:
                if pos[0] == storageSlot[0][0] and pos[1] == storageSlot[0][1]:
                    found = True
                    text += f"is storage slot for {storageSlot[1]} ({storageSlot[2]})\n"
            for buildSite in room.buildSites:
                if pos == buildSite[0]:
                    found = True
                    text += f"is build site for {buildSite[1]} ({buildSite[2]})\n"
            if not found:
                text += "this field is not special\n"
            text += "\n"

        items = self.container.getItemByPosition(pos)
        mainItem = None
        if items:
            if len(items) == 1:
                text += f"there is a {items[0].name}:\n\n"
            else:
                text += f"there are {len(items)} items:\n"
                for item in items:
                    text += f"* {item.name}\n"
                text += "\nOn the top is:\n\n"
            mainItem = items[0]
        else:
            text += "there are no items"

        if mainItem:
            registerInfo = ""
            for (key, value) in mainItem.fetchSpecialRegisterInformation().items():
                self.setRegisterValue(key, value)
                registerInfo += f"{key}: {value}\n"

            # print info
            info = mainItem.getLongInfo()
            if info:
                text += info

            # notify listeners
            self.changed("examine", mainItem)

        self.submenue = src.interaction.OneKeystrokeMenu(text)
        self.macroState["submenue"] = self.submenue

    def examine(self, item):
        """
        make the character examine an item

        Parameters:
            item: the item to examine
        """

        registerInfo = ""
        for (key, value) in item.fetchSpecialRegisterInformation().items():
            self.setRegisterValue(key, value)
            registerInfo += f"{key}: {value}\n"

        # print info
        info = item.getLongInfo()
        if info:
            info += "\n\nregisterinformation:\n\n" + registerInfo
            self.submenue = src.interaction.OneKeystrokeMenu(info)
            self.macroState["submenue"] = self.submenue

        # notify listeners
        self.changed("examine", item)

    def advance(self,advanceMacros=False):
        """
        advance the character one tick
        Parameters:
            advanceMacros: wether or not to advance the character based on macros (True = advance)
        """

        if self.stasis or self.dead or self.disabled:
            return

        self.implantLoad = 0

        if advanceMacros:
            src.interaction.advanceChar(self,[])

        #HACK: sound effect
        """
        if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%4 == 1:
            src.interaction.pygame2.mixer.Channel(1).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%4 == 2:
            if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 2:
                src.interaction.pygame2.mixer.Channel(3).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
            else:
                src.interaction.pygame2.mixer.Channel(4).play(src.interaction.pygame2.mixer.Sound('../Downloads/Thip.ogg'))
        """
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 0:
        #    src.interaction.pygame2.mixer.Channel(0).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 1:
        #    src.interaction.pygame2.mixer.Channel(1).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 2:
        #    src.interaction.pygame2.mixer.Channel(2).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 3:
        #    src.interaction.pygame2.mixer.Channel(3).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 4:
        #    src.interaction.pygame2.mixer.Channel(4).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 5:
        #    src.interaction.pygame2.mixer.Channel(5).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 6:
        #    src.interaction.pygame2.mixer.Channel(6).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))
        #if src.gamestate.gamestate.mainChar == self and src.gamestate.gamestate.tick%8 == 7:
        #    src.interaction.pygame2.mixer.Channel(7).play(src.interaction.pygame2.mixer.Sound('../Downloads/Confirm8-Bit.ogg'))

        # smooth over impossible state
        while self.events and src.gamestate.gamestate.tick > self.events[0].tick:
            event = self.events[0]
            logger.debug("something went wrong and event %s was skipped", event)
            self.events.remove(event)

        # handle events
        while self.events and src.gamestate.gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            if event not in self.events:
                logger.debug("impossible state with events")
                continue
            self.events.remove(event)

        # handle satiation
        self.satiation -= self.foodPerRound
        if self.satiation < 100:
            if self.satiation < 10:
                self.frustration += 10
            self.frustration += 1
        if self.satiation < 0 and not self.godMode:
            self.die(
                reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "
                + config.commandChars.drink
                + " key"
            )
            return

        if self.health < self.maxHealth and (
                int(self.health) and (src.gamestate.gamestate.tick+10000)%int(self.health) < self.healingThreashold):
            self.heal(1,reason="time heals your wounds")

        #if self.satiation in (300 - 1, 200 - 1, 100 - 1, 30 - 1):
        if self.satiation < 300 and self.flask and self.flask.uses > 0:
            self.flask.apply(self)

        if self.satiation == 299:
            self.changed("thirst")

        if self.satiation < 30:
            for item in self.inventory:
                if isinstance(item, src.items.itemMap["GooFlask"]) and item.uses > 0:
                    item.apply(self)
                    break

                if (
                    isinstance(item, src.items.itemMap["BioMass"]) or isinstance(item, src.items.itemMap["Bloom"]) or (item, src.items.itemMap["PressCake"]) or (item, src.items.itemMap["SickBloom"])
                ):
                    item.apply(self)
                    if item in self.inventory:
                        self.inventory.remove(item)
                    break
                if isinstance(item, src.items.itemMap["Corpse"]):
                    item.apply(self)
                    break

        if self.satiation == 30 - 1:
            self.changed("severeThirst")

        if (
            self == src.gamestate.gamestate.mainChar
            and self.satiation < 300
            and self.satiation > -1
        ):
            self.addMessage(
                "you'll starve in "
                + str(src.gamestate.gamestate.mainChar.satiation)
                + " ticks!"
            )

        """
        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
        """

    # bad pattern: is repeated in items etc
    def addListener(self, listenFunction, tag="default"):
        """
        register a callback function for notifications
        if something wants to wait for the character to die it should register as listener

        Parameters:
            listenFunction: the function that should be called if the listener is triggered
            tag: a tag determining what kind of event triggers the listen function. For example "died"
        """
        # create container if container doesn't exist
        # bad performance: string comparison, should use enums. Is this slow in python?
        if tag not in self.listeners:
            self.listeners[tag] = []

        # added listener function
        if listenFunction not in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    # bad pattern: is repeated in items etc
    def delListener(self, listenFunction, tag="default"):
        """
        deregister a callback function for notifications

        Parameters:
            listenFunction: the function that would be called if the listener is triggered
            tag: a tag determining what kind of event triggers the listen function. For example "died"
        """

        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clear up dict
        # bad performance: probably better to not clean up and recreate
        if not self.listeners[tag]:
            del self.listeners[tag]

    # bad code: probably misnamed
    def changed(self, tag="default", info=None):
        """
        call callbacks functions that did register for listening to events

        Parameters:
            tag: the tag determining what kind of event triggers the listen function. For example "died"
            info: additional information
        """

        """
        if src.gamestate.gamestate.mainChar == self and tag == "entered room":
            if isinstance(info[1],src.rooms.WorkshopRoom):
                src.interaction.playSound("workshopRoom","roomMusic",loop=True)
            elif isinstance(info[1],src.rooms.TrapRoom):
                src.interaction.playSound("electroRoom","roomMusic",loop=True)
        """

        # do nothing if nobody listens
        if tag not in self.listeners:
            return

        # call each listener
        for listenFunction in self.listeners[tag]:
            if info is None:
                listenFunction()
            else:
                listenFunction(info)

    def startIdling(self):
        """
        run idle actions using the macro automation
        should be called when the character is bored for some reason
        """

        if not self.personality["doIdleAction"]:
            self.runCommandString(".")
            return

        waitString = str(random.randint(1, self.personality["idleWaitTime"])) + "."
        waitChance = self.personality["idleWaitChance"]

        if self.aggro:
            self.aggro -= 1
            if not self.container:
                return

            commands = []
            for character in self.container.characters:
                if character == self:
                    continue
                if character.faction == self.faction:
                    continue
                if character.xPosition // 15 != self.xPosition // 15 or character.yPosition // 15 != self.yPosition // 15:
                    continue

                if abs(character.xPosition-self.xPosition) < 2 and abs(character.yPosition-self.yPosition) < 2 and ( abs(character.xPosition-self.xPosition) == 0 or abs(character.yPosition-self.yPosition) == 0):
                    commands = ["m"]
                    break

                if character.xPosition-self.xPosition > 0:
                    commands.append("d")
                if character.xPosition-self.xPosition < 0:
                    commands.append("a")
                if character.yPosition-self.yPosition > 0:
                    commands.append("s")
                if character.yPosition-self.yPosition < 0:
                    commands.append("w")

            if not commands:
                command = "."
            else:
                command = random.choice(commands)
        elif (
            self.frustration < 1000 + self.personality["frustrationTolerance"]
            and random.randint(1, waitChance) != 1
        ):  # real idle
            command = waitString
            self.frustration -= 1
        elif (
            self.frustration < 4000 + self.personality["frustrationTolerance"]
            and random.randint(1, waitChance) != 1
        ):  # do mainly harmless stuff
            command = random.choice(
                [
                    "w" + waitString + "s",
                    "a" + waitString + "d",
                    "d" + waitString + "a",
                    "s" + waitString + "w",
                    "w" + waitString + "a" + waitString + "s" + waitString + "d",
                    "d" + waitString + "s" + waitString + "a" + waitString + "w",
                ]
            )
            self.frustration -= 10
        elif (
            self.frustration < 16000 + self.personality["frustrationTolerance"]
            and random.randint(1, waitChance) != 1
        ):  # do not so harmless stuff
            command = random.choice(
                [
                    "ls" + waitString + "wk",
                    "opf$=aa$=ww$=ss$=ddj$=da$=sw$=ws$=ad",
                    "j",
                    "ajd",
                    "wjs",
                    "dja",
                    "sjw",
                    "Ja",
                    "Jw",
                    "Js",
                    "Jd",
                    "J.",
                    "opn$=aaj$=wwj$=ssj$=ddj",
                    "opx$=aa$=ww$=ss$=dd",
                ]
            )
            self.frustration -= 100
        elif (
            self.frustration < 64000 + self.personality["frustrationTolerance"]
            and random.randint(1, waitChance) != 1
        ):  # bad stuff
            command = random.choice(
                [
                    "opf$=aa$=ww$=ss$=ddk",
                    "opf$=aa$=ww$=ss$=ddj$=da$=sw$=ws$=ad",
                ]
            )
            self.frustration -= 300
        else:  # run amok
            command = random.choice(
                [
                    "opc$=aa$=ww$=ss$=ddm",
                    "opc$=aa$=ww$=ss$=ddmk",
                ]
            )
            self.frustration -= 1000

        self.runCommandString(command)

    def removeSatiation(self, amount):
        """
        make the character more hungry

        Parameters:
            amount: how much hungryier the character should be
        """

        self.satiation -= amount
        if self.satiation < 0:
            self.die(reason="you starved")

    def addSatiation(self, amount, reason=None):
        """
        make the character less hungry

        Parameters:
            amount: how much the character should be less hungryier
        """

        self.addMessage(f"you gain {amount} satiation because you {reason}")

        self.satiation += amount
        if self.satiation > 1000:
            self.satiation = 1000


    def addFrustration(self, amount):
        """
        increase the characters frustration

        Parameters:
            amount: how much the frustration should increase
        """

        self.frustration += amount

    def removeFrustration(self, amount, reason=None):
        """
        decrease the characters frustration

        Parameters:
            amount: how much the frustration should be decreased
        """

        self.frustration -= amount

# bad code: animals should not be characters. This means it is possible to chat with a mouse
class Mouse(Character):
    """
    the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
    """


    def __init__(
        self,
        display="🝆 ",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Mouse",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting

        Parameters:
            display: how the mouse should look like
            xPosition: obsolete, ignore
            yPosition: obsolete, ignore
            quests: obsolete, ignore
            automated: obsolete, ignore
            name: obsolete, ignore
            creator: obsolete, ignore
            characterId: obsolete, ignore
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.charType = "Mouse"
        self.vanished = False

        self.personality["autoAttackOnCombatSuccess"] = 1
        self.personality["abortMacrosOnAttack"] = True
        self.health = 10
        self.faction = "mice"

        self.solvers.extend(["NaiveMurderQuest"])

        self.baseDamage = 1
        self.randomBonus = 0
        self.bonusMultiplier = 0
        self.staggerResistant = 0

    def vanish(self):
        """
        make the mouse disapear
        """
        # remove self from map
        self.container.removeCharacter(self)
        self.vanished = True

# bad code: there is very specific code in here, so it it stopped to be a generic class
class Monster(Character):
    """
    a class for a generic monster
    """

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Mouse",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting

        Parameters:
            display: what the monster should look like
            xPosition: obsolete, ignore
            yPosition: obsolete, ignore
            quests: obsolete, ignore
            automated: obsolete, ignore
            name: obsolete, ignore
            creator: obsolete, ignore
            characterId: obsolete, ignore
        """

        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.charType = "Monster"

        self.phase = 1

        self.faction = "monster"
        self.stepsOnMines = True

        self.personality["moveItemsOnCollision"] = True

        self.specialDisplay = None

        self.solvers.extend(["NaiveMurderQuest"])
        self.skills.append("fighting")

    def getItemWalkable(self,item):
        """
        """
        if item.type in ["Bush","EncrustedBush"]:
            return True
        return item.walkable

    # bad code: specific code in generic class
    def die(self, reason=None, addCorpse=True):
        """
        special handle corpse spawning
        """

        if not addCorpse:
            super().die(reason, addCorpse=False)
            return

        if self.phase == 1:
            if (
                self.xPosition
                and self.yPosition
                and (
                    not self.container.getItemByPosition(
                        (self.xPosition, self.yPosition, self.zPosition)
                    )
                )
            ):
                if isinstance(self.container,src.terrains.Terrain):
                    new = src.items.itemMap["Mold"]()
                    self.container.addItem(new, self.getPosition())
                    new.startSpawn()
                else:
                    self.container.damage()

            super().die(reason, addCorpse=False)
        else:
            new = src.items.itemMap["MoldFeed"]()
            if self.container:
                self.container.addItem(new, self.getPosition())
            super().die(reason, addCorpse=False)

    # bad code: very specific and unclear
    def enterPhase2(self):
        """
        enter a new evolution state and learn to pick up stuff
        """

        self.phase = 2
        if "NaivePickupQuest" not in self.solvers:
            self.solvers.append("NaivePickupQuest")

    # bad code: very specific and unclear
    def enterPhase3(self):
        """
        enter a new evolution state and start to kill people
        """

        self.phase = 3
        self.macroState["macros"] = {
            "s": list("opf$=aa$=ss$=ww$=ddj"),
        }
        self.macroState["macros"]["m"] = []
        for _i in range(8):
            self.macroState["macros"]["m"].extend(["_", "s"])
            self.macroState["macros"]["m"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["m"].append(random.choice(["a", "w", "s", "d"]))
        self.macroState["macros"]["m"].extend(["_", "m"])
        self.runCommandString("_m")

    def enterPhase4(self):
        """
        enter a new evolution state and start to hunt people
        """

        self.phase = 4
        self.macroState["macros"] = {
            "e": list("10jm"),
            "s": list("opM$=aa$=ww$=dd$=ss_e"),
            "w": [],
            "f": list("%c_s_w_f"),
        }
        for _i in range(4):
            self.macroState["macros"]["w"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["w"].append(random.choice(["a", "w", "s", "d"]))
        self.runCommandString("_f")

    def enterPhase5(self):
        """
        enter a new evolution state and start a new faction
        """

        self.phase = 5
        self.faction = ""
        for _i in range(5):
            self.faction += random.choice("abcdefghiasjlkasfhoiuoijpqwei10934009138402")
        self.macroState["macros"] = {
            "j": list(70 * "Jf" + "m"),
            "s": list("opM$=aa$=ww$=dd$=sskjjjk"),
            "w": [],
            "k": list("ope$=aam$=wwm$=ddm$=ssm"),
            "f": list("%c_s_w_k_f"),
        }
        for _i in range(8):
            self.macroState["macros"]["w"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["w"].append(random.choice(["a", "w", "s", "d"]))
            self.macroState["macros"]["w"].append("m")
        self.runCommandString("_f")

    # bad code: should listen to itself instead
    def changed(self, tag="default", info=None):
        """
        trigger evolutionary steps
        """

        if self.phase == 1 and self.satiation > 900:
            self.enterPhase2()
        if len(self.inventory) == 10:
            fail = False
            for item in self.inventory:
                if item.type != "Corpse":
                    fail = True
            if not fail:
                self.addMessage("do action")
                newChar = Monster(creator=self)

                newChar.solvers = [
                    "NaiveActivateQuest",
                    "ActivateQuestMeta",
                    "NaivePickupQuest",
                    "NaiveMurderQuest",
                ]

                newChar.faction = self.faction
                newChar.enterPhase5()

                toDestroy = self.inventory[0:5]
                for item in toDestroy:
                    item.destroy()
                    self.inventory.remove(item)
                self.container.addCharacter(newChar, self.xPosition, self.yPosition)

        super().changed(tag, info)

    def render(self):
        """
        render the monster depending on the evelutionary state
        """

        if self.specialDisplay:
            return self.specialDisplay

        render = src.canvas.displayChars.monster_spore
        if self.phase == 2:
            render = src.canvas.displayChars.monster_feeder

            if self.health > 150:
                colorHealth = "#f80"
            elif self.health > 140:
                colorHealth = "#e80"
            elif self.health > 130:
                colorHealth = "#d80"
            elif self.health > 120:
                colorHealth = "#c80"
            elif self.health > 110:
                colorHealth = "#b80"
            elif self.health > 100:
                colorHealth = "#a80"
            elif self.health > 90:
                colorHealth = "#980"
            elif self.health > 80:
                colorHealth = "#880"
            elif self.health > 70:
                colorHealth = "#780"
            elif self.health > 60:
                colorHealth = "#680"
            elif self.health > 50:
                colorHealth = "#580"
            elif self.health > 40:
                colorHealth = "#480"
            elif self.health > 30:
                colorHealth = "#380"
            elif self.health > 20:
                colorHealth = "#280"
            elif self.health > 10:
                colorHealth = "#180"
            else:
                colorHealth = "#080"

            if self.baseDamage > 15:
                colorDamage = "#f80"
            elif self.baseDamage > 14:
                colorDamage = "#e80"
            elif self.baseDamage > 13:
                colorDamage = "#d80"
            elif self.baseDamage > 12:
                colorDamage = "#c80"
            elif self.baseDamage > 11:
                colorDamage = "#b80"
            elif self.baseDamage > 10:
                colorDamage = "#a80"
            elif self.baseDamage > 9:
                colorDamage = "#980"
            elif self.baseDamage > 8:
                colorDamage = "#880"
            elif self.baseDamage > 7:
                colorDamage = "#780"
            elif self.baseDamage > 6:
                colorDamage = "#680"
            elif self.baseDamage > 5:
                colorDamage = "#580"
            elif self.baseDamage > 4:
                colorDamage = "#480"
            elif self.baseDamage > 3:
                colorDamage = "#380"
            elif self.baseDamage > 2:
                colorDamage = "#280"
            elif self.baseDamage > 1:
                colorDamage = "#180"
            else:
                colorDamage = "#080"

            render = [(urwid.AttrSpec(colorHealth, "#444"), "🝆"),(urwid.AttrSpec(colorDamage, "#444"), "-")]
        elif self.phase == 3:
            render = src.canvas.displayChars.monster_grazer
        elif self.phase == 4:
            render = src.canvas.displayChars.monster_corpseGrazer
        elif self.phase == 5:
            render = src.canvas.displayChars.monster_hunter

        return render

class Statue(Monster):
    """
    the class for animated statues
    intended as temple guards
    """

    def __init__(
        self,
        display="@@",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Statue",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting

        Parameters:
            display: how the mouse should look like
            xPosition: obsolete, ignore
            yPosition: obsolete, ignore
            quests: obsolete, ignore
            automated: obsolete, ignore
            name: obsolete, ignore
            creator: obsolete, ignore
            characterId: obsolete, ignore
        """
        if quests is None:
            quests = []

        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.charType = "Statue"
        self.specialDisplay = "@@"
        self.baseDamage = 10

    def die(self, reason=None, addCorpse=True):
        """
        die without leaving a corpse
        """
        super().die(reason, addCorpse=False)

class Statuette(Monster):
    """
    the class for a small statue
    is intended as temple guard
    """
    def __init__(
        self,
        display="st",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Statuette",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []

        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.charType = "Statuette"
        self.specialDisplay = "st"

    def die(self, reason=None, addCorpse=True):
        super().die(reason, addCorpse=False)

# bad code: there is very specific code in here, so it it stopped to be a generic class
class Guardian(Character):
    """
    a class for a generic monster
    """

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Guardian",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """

        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.faction = "monster"

        self.solvers.extend(["NaiveMurderQuest"])
        self.charType = "Guardian"

    def render(self):
        """
        render the monster depending on health and damage
        """

        render = src.canvas.displayChars.monster_feeder

        if self.health > 1500:
            colorHealth = "#f80"
        elif self.health > 1400:
            colorHealth = "#e80"
        elif self.health > 1300:
            colorHealth = "#d80"
        elif self.health > 1200:
            colorHealth = "#c80"
        elif self.health > 1100:
            colorHealth = "#b80"
        elif self.health > 1000:
            colorHealth = "#a80"
        elif self.health > 900:
            colorHealth = "#980"
        elif self.health > 800:
            colorHealth = "#880"
        elif self.health > 700:
            colorHealth = "#780"
        elif self.health > 600:
            colorHealth = "#680"
        elif self.health > 500:
            colorHealth = "#580"
        elif self.health > 400:
            colorHealth = "#480"
        elif self.health > 300:
            colorHealth = "#380"
        elif self.health > 200:
            colorHealth = "#280"
        elif self.health > 100:
            colorHealth = "#180"
        else:
            colorHealth = "#080"

        if self.baseDamage > 15:
            colorDamage = "#f80"
        elif self.baseDamage > 14:
            colorDamage = "#e80"
        elif self.baseDamage > 13:
            colorDamage = "#d80"
        elif self.baseDamage > 12:
            colorDamage = "#c80"
        elif self.baseDamage > 11:
            colorDamage = "#b80"
        elif self.baseDamage > 10:
            colorDamage = "#a80"
        elif self.baseDamage > 9:
            colorDamage = "#980"
        elif self.baseDamage > 8:
            colorDamage = "#880"
        elif self.baseDamage > 7:
            colorDamage = "#780"
        elif self.baseDamage > 6:
            colorDamage = "#680"
        elif self.baseDamage > 5:
            colorDamage = "#580"
        elif self.baseDamage > 4:
            colorDamage = "#480"
        elif self.baseDamage > 3:
            colorDamage = "#380"
        elif self.baseDamage > 2:
            colorDamage = "#280"
        elif self.baseDamage > 1:
            colorDamage = "#180"
        else:
            colorDamage = "#080"

        if self.faction == src.gamestate.gamestate.mainChar.faction:
            render = [(urwid.AttrSpec(colorHealth, "black"), "?"),(urwid.AttrSpec(colorDamage, "black"), "-")]
        else:
            render = [(urwid.AttrSpec(colorHealth, "black"), "!"),(urwid.AttrSpec(colorDamage, "black"), "-")]

        return render

class Exploder(Monster):
    """
    a monster that explodes on death
    """

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Mouse",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )

        self.charType = "Exploder"

        self.explode = True

    def render(self):
        """
        render the monster explecitly
        """
        return src.canvas.displayChars.monster_exploder

    def die(self, reason=None, addCorpse=True):
        """
        create an explosion on death

        Parameters:
            reason: the reason for dieing
            addCorpse: flag indicating wether a corpse should be added
        """

        if self.xPosition and self.container:
            new = src.items.itemMap["FireCrystals"]()
            self.container.addItem(new,self.getPosition())
            if self.explode:
                new.startExploding()

        super().die(reason=reason, addCorpse=False)

class Spider(Monster):
    """
    A spider
    should hang out in abandoned room and such
    """

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Spider",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )

        self.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "NaiveMurderQuest",
        ]

        self.defending = None

    def render(self):
        """
        force static render
        """
        return "ss"

    def startDefending(self):
        """
        start waiting for a victim
        """
        if not isinstance(self.container,src.rooms.Room):
            return
        self.container.addListener(self.killVisitor,"entered room")

    def hurt(self, damage, reason=None, actor=None):
        """
        reverse acid damage and kill when hurt
        """
        if reason == "acid burns":
            super().heal(damage, reason=reason)
        else:
            super().hurt(damage, reason=reason)
        self.runCommandString("gg")

    def killVisitor(self,character):
        """
        trigger killing visitors
        is expected to be called from an event
        Parameters:
            character: the character entering the room
        """
        character.addMessage("skreeeeee")
        self.runCommandString("gg")

class Ghoul(Character):
    """
    """

    def __init__(
        self,
        display="@ ",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Ghoul",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.solvers.append("NaiveActivateQuest")
        self.solvers.append("NaiveMurderQuest")

        self.charType = "Ghoul"

    def getOwnAction(self):
        """
        disable own actions
        """
        self.hasOwnAction = 0
        return "."

    def heal(self, amount, reason=None):
        """
        disable healing
        """
        self.addMessage("ghouls don't heal")

    def hurt(self, damage, reason=None, actor=None):
        """
        half the damage taken
        """
        super().hurt(max(1,damage//2),reason=reason,actor=actor)

class Maggot(Character):
    """
    A maggot
    intended as something to be hatched
    not really used right now
    """

    def __init__(
        self,
        display="o=",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Maggot",
        creator=None,
        characterId=None,
    ):
        """
        basic state setting
        """
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.solvers.append("NaiveActivateQuest")
        self.solvers.append("NaiveMurderQuest")
        self.maxHealth = random.randint(5,15)
        self.health = self.maxHealth

        self.satiation = 10

        self.charType = "Maggot"

    def advance(self,advanceMacros=False):
        """
        overwrite behavior to just kill everything else
        """

        if self.timeTaken > 1:
            return
        if src.gamestate.gamestate.tick % 2 != 0:
            return

        self.satiation -= 1
        if self.satiation < 0:
            self.die(reason="starved")
            return

        terrain = self.getTerrain()
        characters = terrain.charactersByTile.get(self.getBigPosition(),[])
        directions = []
        for character in characters:
            if character != self:
                if character.xPosition < self.xPosition:
                    directions.append("a")
                    directions.append("a")
                    directions.append("a")
                elif character.xPosition > self.xPosition:
                    directions.append("d")
                    directions.append("d")
                    directions.append("d")
                elif character.yPosition > self.yPosition:
                    directions.append("s")
                    directions.append("s")
                    directions.append("s")
                elif character.yPosition < self.yPosition:
                    directions.append("w")
                    directions.append("w")
                    directions.append("w")

        if not directions:
            directions = ["w","a","s","d"]

        direction = random.choice(directions)
        self.runCommandString(direction+"jm")

    def die(self, reason=None, addCorpse=True):
        """
        leave a special corpse
        """

        if self.xPosition and self.container:
            new = src.items.itemMap["VatMaggot"]()
            self.container.addItem(new,self.getPosition())

        super().die(reason=reason, addCorpse=False)



characterMap = {
    "Character": Character,
    "Monster": Monster,
    "Guardian": Guardian,
    "Exploder": Exploder,
    "Mouse": Mouse,
    "Spider": Spider,
    "Ghoul": Ghoul,
    "Maggot": Maggot,
}
