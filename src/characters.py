"""
the code for the characters belongs here
"""
# import basic libs
import json

# import the other internal libs
import src.items
import src.saveing
import src.quests
import src.chats
import src.events
import src.canvas
import src.interaction
import config
import random
import src.logger
import src.gamestate


class Character(src.saveing.Saveable):
    """
    this is the class for characters meaning both npc and pcs.
    """

    charType = "Character"

    def __init__(
        self,
        display=None,
        xPosition=0,
        yPosition=0,
        quests=[],
        automated=True,
        name=None,
        creator=None,
        characterId=None,
        seed=None,
    ):
        """
        sets basic info AND adds default behaviour/items

        Parameters:
            display: how the character is rendered
            xPosition: obsolete, to be removed
            yPosition: obsolete, to be removed
            quests: obsolete, to be removed
            automated: obsolete, to be removed
            name: the name the character should have
            creator: osolete, to be removed
            characterId: osolete, to be removed
            seed: rng seed
        """
        super().__init__()

        if name is None and seed:
            name = (
                config.names.characterFirstNames[
                    seed % len(config.names.characterFirstNames)
                    ]
                + " "
                + config.names.characterLastNames[
                    (seed * 10) % len(config.names.characterLastNames)
                    ]
            )

        if display is None and name is not None:
            display = src.canvas.displayChars.staffCharactersByLetter[name[0].lower()]

        if name is None:
            name = "Person"
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
        self.solvers = ["NaiveDropQuest"]
        self.aliances = []
        self.stasis = False
        self.registers = {}
        self.doStackPop = False
        self.doStackPush = False
        self.timeTaken = 0
        self.personality = {}
        self.lastRoom = None
        self.lastTerrain = None
        self.health = 100
        self.heatResistance = 0
        self.godMode = False
        self.submenue = None
        self.jobOrders = []

        self.frustration = 0
        self.aggro = 0
        self.numAttackedWithoutResponse = 0

        self.weapon = None
        self.armor = None
        self.combatMode = None

        self.interactionState = {}
        self.interactionStateBackup = []

        self.baseDamage = 2
        self.randomBonus = 2
        self.bonusMultiplier = 1
        self.staggered = 0
        self.staggerResistant = False

        self.lastJobOrder = ""

        # generate the id for this object
        if characterId:
            self.id = characterId
        else:
            import uuid

            self.id = uuid.uuid4().hex

        # mark attributes for saving
        self.attributesToStore.extend(
            [
                "gotBasicSchooling",
                "gotMovementSchooling",
                "gotInteractionSchooling",
                "gotExamineSchooling",
                "xPosition",
                "yPosition",
                "zPosition",
                "name",
                "satiation",
                "unconcious",
                "reputation",
                "tutorialStart",
                "isMilitary",
                "hasFloorPermit",
                "dead",
                "deathReason",
                "automated",
                "watched",
                "solvers",
                "questsDone",
                "stasis",
                "registers",
                "doStackPop",
                "doStackPush",
                "timeTaken",
                "personality",
                "health",
                "heatResistance",
                "godMode",
                "frustration",
                "combatMode",
                "numAttackedWithoutResponse",
                "baseDamage",
                "randomBonus",
                "bonusMultiplier",
                "staggered",
                "staggerResistant",
                "lastJobOrder",
            ]
        )
        self.objectsToStore.append("serveQuest")
        self.objectsToStore.append("room")

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False
        self.faction = "player"

        import random

        self.personality["idleWaitTime"] = random.randint(2, 100)
        self.personality["idleWaitChance"] = random.randint(2, 10)
        self.personality["frustrationTolerance"] = random.randint(-5000, 5000)
        self.personality["autoCounterAttack"] = True
        self.personality["abortMacrosOnAttack"] = True
        self.personality["autoFlee"] = True
        self.personality["autoAttackOnCombatSuccess"] = 0
        self.personality["annoyenceByNpcCollisions"] = random.randint(50, 150)
        self.personality["attacksEnemiesOnContact"] = True

        self.silent = False

        self.messages = []

        self.xPosition = xPosition
        self.yPosition = yPosition

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

    def getPosition(self):
        """
        returns the characters position

        Returns:
            the position
        """

        return self.xPosition, self.yPosition, self.zPosition

    def searchInventory(self, itemType, extra={}):
        """
        return a list of items from the characters inventory that statisfy some conditions

        Parameters:
            itemType: the item type
            extra: extra condidtions
        """

        foundItems = []
        for item in self.inventory:
            if not item.type == itemType:
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

        self.messages.append(message)

    def runCommandString(self, commandString):
        """
        run a command using the macro automation

        Parameters:
            commandString: the command
        """

        # convert command to macro data structure
        convertedCommand = []
        for char in commandString:
            convertedCommand.append((char, "norecord"))

        # add command to the characters command queue
        self.macroState["commandKeyQueue"] = (
            convertedCommand + self.macroState["commandKeyQueue"]
        )

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

    def hurt(self, damage, reason=None):
        """
        hurt the character

        Parameters:
            damage: the amout of damage dealt
            reason: the reason damage was dealt
        """

        if reason == "attacked":
            if self.aggro < 20:
                self.aggro += 5
            if self.personality.get("abortMacrosOnAttack"):
                self.clearCommandString()
            if self.personality.get("autoCounterAttack"):
                self.runCommandString("m")
            if self.personality.get("autoRun"):
                self.runCommandString(random.choice(["a", "w", "s", "d"]))

            self.numAttackedWithoutResponse += 1
            damage += self.numAttackedWithoutResponse

        if self.armor:
            damageAbsorbtion = self.armor.getArmorValue(reason)

            if self.combatMode == "defensive":
                damageAbsorbtion += 2
                self.addMessage("passive combat bonus")

            self.addMessage("your armor absorbs %s damage" % (damageAbsorbtion,))
            damage -= damageAbsorbtion

        if damage <= 0:
            return

        if self.health - damage > 0:
            staggerThreshold = self.health // 4 + 1

            self.health -= damage
            self.frustration += 10 * damage
            self.addMessage("you took " + str(damage) + " damage")

            if self.combatMode == "defensive":
                staggerThreshold *= 2
            if damage > staggerThreshold:
                self.addMessage("you stager")
                self.staggered += damage // staggerThreshold

            if reason:
                self.addMessage("reason: %s" % (reason,))
        else:
            self.health = 0
            self.die(reason="you died from injuries")

    def attack(self, target):
        """
        make the character attack something

        Parameters:
            target: the target to attack
        """

        if self.numAttackedWithoutResponse > 2:
            self.numAttackedWithoutResponse -= 2
        else:
            self.numAttackedWithoutResponse = 0

        baseDamage = self.baseDamage
        randomBonus = self.randomBonus
        bonusMultiplier = self.bonusMultiplier

        if self.weapon:
            baseDamage = self.weapon.baseDamage
            randomBonus = 7

        if self.combatMode == "agressive":
            bonusMultiplier += 2

        damage = baseDamage + random.randint(0, randomBonus) * bonusMultiplier
        target.hurt(damage, reason="attacked")
        self.addMessage(
            "you attack the enemy for %s damage, the enemy has %s health left"
            % (damage, target.health)
        )

        if self.personality.get("autoAttackOnCombatSuccess"):
            self.runCommandString(
                "m" * self.personality.get("autoAttackOnCombatSuccess")
            )
            self.addMessage("auto attack")

    def heal(self, amount, reason=None):
        """
        heal the character

        Parameters:
            amount: the amount of health healed
            reason: the reason why the character was healed
        """

        if 100 - self.health < amount:
            amount = 100 - self.health

        self.health += amount
        self.addMessage("you heal for %s and have %s health" % (amount, self.health))

    # bad code: only works in a certain room type
    def collidedWith(self, other):
        """
        handle collision with another character
        Parameters:
            other: the other character
        """

        if not other.faction == self.faction:
            if self.personality.get("attacksEnemiesOnContact"):
                self.runCommandString("m")
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
            event: the event
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
            src.logger.debugMessages.append("reacalculate path called without quests")
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

    def getState(self):
        """
        returns the characters state
        used for saving things

        Returns:
            the characters state as json serialisable dictionary
        """
        # fetch base state

        state = super().getState()

        import copy

        state["macroState"] = copy.deepcopy(self.macroState)
        if not state["macroState"]["itemMarkedLast"] is None and not isinstance(
            state["macroState"]["itemMarkedLast"], str
        ):
            state["macroState"]["itemMarkedLast"] = state["macroState"][
                "itemMarkedLast"
            ].id
        if "submenue" in state["macroState"] and state["macroState"]["submenue"]:
            state["macroState"]["submenue"] = state["macroState"]["submenue"].getState()

        state["registers"] = self.registers

        # add simple structures
        state.update(
            {
                "inventory": {},
                "quests": {},
                "path": self.path,
            }
        )

        # store equipment
        if self.weapon:
            state["weapon"] = self.weapon.getState()
        if self.armor:
            state["armor"] = self.armor.getState()

        # store inventory
        inventoryIds = []
        inventoryStates = {}
        for item in self.inventory:
            inventoryIds.append(item.id)
            inventoryStates[item.id] = item.getState()
        state["inventory"]["inventoryIds"] = inventoryIds
        state["inventory"]["states"] = inventoryStates

        # store quests
        questIds = []
        questStates = {}
        for quest in self.quests:
            questIds.append(quest.id)
            questStates[quest.id] = quest.getState()
        state["quests"]["questIds"] = questIds
        state["quests"]["states"] = questStates

        # store events
        eventIds = []
        eventStates = {}
        for event in self.events:
            eventIds.append(event.id)
            eventStates[event.id] = event.getState()
        state["eventIds"] = eventIds
        state["eventStates"] = eventStates

        # store serve quest
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat, dict):
                chatOptions.append(chat.id)
            else:
                option = {"chat": chat["chat"].id, "dialogName": chat["dialogName"], "params": {}}
                if "params" in chat:
                    chatOptions.append(option)
        state["chatOptions"] = chatOptions

        state["type"] = self.charType

        # store submenu
        if self.submenue is None:
            state["submenue"] = self.submenue
        else:
            state["submenue"] = self.submenue.getState()

        jobOrderState = []
        for jobOrder in self.jobOrders:
            jobOrderState.append(jobOrder.getState())
        state["jobOrders"] = jobOrderState

        return state

    def setState(self, state):
        """
        setter for the players state
        used for loading the game

        Parameters:
            state: a dictionary containing the state that should be loaded
        """

        # set basic state
        super().setState(state)

        if "personality" in state:
            personality = state["personality"]
            if "idleWaitTime" not in personality:
                self.personality["idleWaitTime"] = 10
            if "idleWaitChance" not in personality:
                self.personality["idleWaitChance"] = 3
            if "frustrationTolerance" not in personality:
                self.personality["frustrationTolerance"] = 0
            if "autoCounterAttack" not in personality:
                self.personality["autoCounterAttack"] = True
            if "autoFlee" not in personality:
                self.personality["autoFlee"] = True
            if "abortMacrosOnAttack" not in personality:
                self.personality["abortMacrosOnAttack"] = True
            if "annoyenceByNpcCollisions" not in personality:
                self.personality["annoyenceByNpcCollisions"] = True
            if "autoAttackOnCombatSuccess" not in personality:
                self.personality["autoAttackOnCombatSuccess"] = 0
            if "attacksEnemiesOnContact" not in personality:
                self.personality["attacksEnemiesOnContact"] = True

        # store equipment
        if state.get("weapon"):
            self.weapon = src.items.getItemFromState(state["weapon"])
        if state.get("armor"):
            self.armor = src.items.getItemFromState(state["armor"])

        if "loop" not in state["macroState"]:
            state["macroState"]["loop"] = []

        self.macroState = state["macroState"]

        if not self.macroState["itemMarkedLast"] is None:
            def setParam(instance):
                self.macroState["itemMarkedLast"] = instance

            src.saveing.loadingRegistry.callWhenAvailable(
                self.macroState["itemMarkedLast"], setParam
            )
        if "submenue" in self.macroState and self.macroState["submenue"]:
            self.macroState["submenue"] = src.interaction.getSubmenuFromState(
                self.macroState["submenue"]
            )

        if "registers" in state:
            self.registers = state["registers"]

        # set unconscious state
        if "unconcious" in state:
            if self.unconcious:
                self.fallUnconcious()

        # set path
        if "path" in state:
            self.path = state["path"]

        # set inventory
        if "inventory" in state:
            if "inventoryIds" in state["inventory"]:
                for inventoryId in state["inventory"]["inventoryIds"]:
                    item = src.items.getItemFromState(
                        state["inventory"]["states"][inventoryId]
                    )
                    self.inventory.append(item)
            else:
                self.loadFromList(
                    state["inventory"], self.inventory, src.items.getItemFromState
                )

        # set quests
        if "quests" in state:

            # deactivate the quest that will be removed later
            if "removed" in state["quests"]:
                for quest in self.quests[:]:
                    if quest.id in state["quests"]["removed"]:
                        quest.deactivate()
                        quest.completed = True

            # load quests using the saving class
            self.loadFromList(
                state["quests"], self.quests, src.quests.getQuestFromState
            )

            # load a fixed set of quests
            if "questIds" in state["quests"]:

                # tear down current quests
                for quest in self.quests[:]:
                    quest.deactivate()
                    quest.completed = True
                    self.quests.remove(quest)

                # add new quests
                for questId in state["quests"]["questIds"]:
                    quest = src.quests.getQuestFromState(
                        state["quests"]["states"][questId]
                    )
                    self.quests.append(quest)

        # set chat options
        # bad code: storing the Chat options as class instead of object complicates things
        # bad code: probably broken
        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                if not isinstance(chatType, dict):
                    chatOptions.append(src.chats.chatMap[chatType])
                else:
                    option = {
                        "chat": src.chats.chatMap[chatType["chat"]],
                        "dialogName": chatType["dialogName"]
                    }
                    if "params" in chatType:
                        params = {}
                        for (key, value) in chatType["params"].items():
                            """
                            set value
                            """

                            def setParam(instance):
                                params[key] = instance

                            loadingRegistry.callWhenAvailable(value, setParam)
                        option["params"] = params
                    chatOptions.append(option)
            self.basicChatOptions = chatOptions

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = src.events.getEventFromState(eventState)
                self.addEvent(event)

        if "submenue" in state:
            if state["submenue"] is None:
                self.submenue = state["submenue"]
            else:
                self.submenue = src.interaction.getSubmenuFromState(state["submenue"])

        self.jobOrders = []
        if "jobOrders" in state:
            for jobOrder in state["jobOrders"]:
                self.jobOrders.append(src.items.getItemFromState(jobOrder))

        if "frustrationTolerance" not in self.personality:
            self.personality["frustrationTolerance"] = 0

        return state

    # obsolete: remove or reintegrate
    def awardReputation(self, amount=0, fraction=0, reason=None):
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
        if self.watched:
            text = "you were rewarded %i reputation" % totalAmount
            if reason:
                text += " for " + reason
            self.addMessage(text)

    # obsolete: remove or reintegrate
    def revokeReputation(self, amount=0, fraction=0, reason=None):
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
        if self.watched:
            text = "you lost %i reputation" % totalAmount
            if reason:
                text += " for " + reason
            self.addMessage(text)

    # obsolete: reintegrate
    # bad code: this is kind of incompatible with the meta quests
    def startNextQuest(self):
        """
        starts the next quest in the quest list
        """

        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                src.logger.debugMessages.append("setting path to quest failed")
                pass

    def getDetailedInfo(self):
        """
        returns a string with detailed info about the character

        Returns:
            the string
        """

        return (
            "\nname: "
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
            try:
                if self.quests[0] == quest:
                    self.setPathToQuest(quest)
            except:
                # bad pattern: exceptions should be logged
                pass

    # bad pattern: path should be determined by a quests solver
    # bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    # obsolete: probably should be rewritten
    def setPathToQuest(self, quest):
        """
        set the charactes path to a quest

        Parameters:
            quest: the quest to set the path from
        """

        if hasattr(quest, "dstX") and hasattr(quest, "dstY") and self.container:
            self.path = self.container.findPath(
                (self.xPosition, self.yPosition), (quest.dstX, quest.dstY)
            )
        else:
            self.path = []

    def addToInventory(self, item):
        """
        add an item to the characters inventory

        Parameters:
            item: the item
        """

        self.inventory.append(item)

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
    def applysolver(self, solver):
        """
        this wrapper converts a character centered call to a solver centered call
        """

        if not self.unconcious and not self.dead:
            solver(self)

    def fallUnconcious(self):
        """
        make the character fall unconcious
        """

        self.unconcious = True
        if self.watched:
            self.addMessage("*thump,snort*")
        self.changed("fallen unconcious", self)

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

        self.lastRoom = self.room
        self.lastTerrain = self.terrain

        # replace character with corpse
        if self.container:
            container = self.container
            container.removeCharacter(self)
            if addCorpse:
                corpse = src.items.itemMap["Corpse"]()
                container.addItem(corpse, self.getPosition())
        # log impossible state
        else:
            src.logger.debugMessages.append(
                "this should not happen, character died without beeing somewhere ("
                + str(self)
                + ")"
            )

        self.macroState["commandKeyQueue"] = []

        # set attributes
        self.addMessage("you died.")
        self.dead = True
        if reason:
            self.deathReason = reason
            self.addMessage("cause of death: %s" % (reason,))
        self.path = []

        # notify listeners
        self.changed("died", {"character": self, "reason": reason})

        # notify listeners
        self.changed()

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
            src.logger.debugMessages.append("dead men walking")
            return
        if not self.path:
            self.setPathToQuest(self.quests[0])
            src.logger.debugMessages.append("walking without path")

        # move along the predetermined path
        currentPosition = (self.xPosition, self.yPosition)
        if not (self.path and not self.path == [currentPosition]):
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
                    self.changed()
                else:
                    src.logger.debugMessages.append(
                        "character moved on non continious path"
                    )
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
                        self.changed()
                        return
                    else:
                        # show message the character bumped into a wall
                        # bad pattern: why restrict the player to standard entry points?
                        self.addMessage("you cannot move there (" + direction + ")")
                        return

                # handle the character moving into the rooms boundaries
                # bad code: repetitive, confusing code
                # check north
                if (
                    room.yPosition * 15 + room.offsetY + room.sizeY
                    == nextPosition[1] + 1
                ):
                    if (
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
                if room.yPosition * 15 + room.offsetY == nextPosition[1]:
                    if (
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
                ):
                    if (
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
                if room.xPosition * 15 + room.offsetX == nextPosition[0]:
                    if (
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
                self.changed()

        # handle bumping into an item
        if item:
            # open doors
            # bad pattern: this should not happen here
            if isinstance(item, src.items.Door):
                item.apply(self)
            return False

        # smooth over impossible state
        else:
            if not src.interaction.debug:
                if not self.path or not nextPosition == self.path[0]:
                    return False

            # remove last step from path
            if self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]:
                self.path = self.path[1:]
        return False

    def drop(self, item, position=None):
        """
        make the character drop an item

        Parameters:
            item: the item to drop
            position: the position to drop the item on
        """

        foundScrap = None

        if not position:
            position = self.getPosition()

        itemList = self.container.getItemByPosition(position)

        if item.walkable == False and len(itemList):
            self.addMessage("you need a clear space to drop big items")
            return

        foundBig = False

        for compareItem in itemList:
            if compareItem.type == "Scrap":
                foundScrap = compareItem
            if compareItem.walkable == False and not (
                compareItem.type == "Scrap" and compareItem.amount < 15
            ):
                foundBig = True
                break

        if foundBig:
            self.addMessage("there is no space to drop the item")
            return

        self.addMessage("you drop a %s" % item.type)

        # remove item from inventory
        self.inventory.remove(item)

        if foundScrap and item.type == "Scrap":
            foundScrap.amount += item.amount
            foundScrap.setWalkable()
        else:
            # add item to floor
            self.container.addItem(item, position)

        self.changed()

    def examine(self, item):
        """
        make the character examine an item

        Parameters:
            item: the item to examine
        """

        registerInfo = ""
        for (key, value) in item.fetchSpecialRegisterInformation().items():
            self.setRegisterValue(key, value)
            registerInfo += "%s: %s\n" % (
                key,
                value,
            )

        # print info
        info = item.getLongInfo()
        if info:
            self.addMessage("go show a menu")
            info += "\n\nregisterinformation:\n\n" + registerInfo
            self.submenue = src.interaction.OneKeystrokeMenu(info)
            self.macroState["submenue"] = self.submenue

        # notify listeners
        self.changed("examine", item)

    def advance(self):
        """
        advance the character one tick
        """

        if self.stasis or self.dead:
            return

        # smooth over impossible state
        while self.events and src.gamestate.gamestate.tick > self.events[0].tick:
            event = self.events[0]
            src.logger.debugMessages.append(
                "something went wrong and event" + str(event) + "was skipped"
            )
            self.events.remove(event)

        # handle events
        while self.events and src.gamestate.gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            if event not in self.events:
                src.logger.debugMessages.append("impossible state with events")
                continue
            self.events.remove(event)

        # handle satiation
        self.satiation -= 1
        if self.satiation < 100:
            if self.satiation < 10:
                self.frustration += 10
            self.frustration += 1
        self.changed()
        if self.satiation < 0 and not self.godMode:
            self.die(
                reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "
                       + config.commandChars.drink
                       + " key"
            )
            return

        if self.satiation in (300 - 1, 200 - 1, 100 - 1, 30 - 1):
            self.changed("thirst")
            self.macroState["commandKeyQueue"] = [
                                                     ("|", ["norecord"]),
                                                     (">", ["norecord"]),
                                                     ("_", ["norecord"]),
                                                     ("j", ["norecord"]),
                                                     ("|", ["norecord"]),
                                                     ("<", ["norecord"]),
                                                 ] + self.macroState["commandKeyQueue"]

        if self.satiation == 30 - 1:
            self.changed("severeThirst")

        if (
            self == src.gamestate.gamestate.mainChar
            and self.satiation < 30
            and self.satiation > -1
        ):
            self.addMessage(
                "you'll starve in "
                + str(src.gamestate.gamestate.mainChar.satiation)
                + " ticks!"
            )

        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()

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

        waitString = str(random.randint(1, self.personality["idleWaitTime"])) + "."
        waitChance = self.personality["idleWaitChance"]

        if self.aggro:
            self.aggro -= 1
            command = random.choice(
                [
                    "ope$=aa$=ww$=ss$=ddm",
                    "ope$=aa$=ww$=ss$=ddmk",
                ]
            )
        elif (
            self.frustration < 1000 + self.personality["frustrationTolerance"]
            and not random.randint(1, waitChance) == 1
        ):  # real idle
            command = waitString
            self.frustration -= 1
        elif (
            self.frustration < 4000 + self.personality["frustrationTolerance"]
            and not random.randint(1, waitChance) == 1
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
            and not random.randint(1, waitChance) == 1
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
            and not random.randint(1, waitChance) == 1
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

        parsedCommand = []
        for char in command:
            parsedCommand.append((char, ["norecord"]))

        self.macroState["commandKeyQueue"] = parsedCommand

    def removeSatiation(self, amount):
        """
        make the character more hungry

        Parameters:
            amount: how much the character should be hungryier
        """

        self.satiation -= amount
        if self.satiation < 0:
            self.die(reason="you starved")

    def addSatiation(self, amount):
        """
        make the character less hungry

        Parameters:
            amount: how less the character should be hungryier
        """

        self.satiation += amount
        if self.satiation > 1000:
            self.satiation = 1000


# bad code: animals should not be characters. This means it is possible to chat with a mouse
class Mouse(Character):
    """
    the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
    """

    charType = "Mouse"

    def __init__(
        self,
        display="🝆 ",
        xPosition=0,
        yPosition=0,
        quests=[],
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
        self.vanished = False
        self.attributesToStore.extend(
            [
                "vanished",
            ]
        )
        self.initialState = self.getState()

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

    charType = "Monster"

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=[],
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
        self.phase = 1
        self.attributesToStore.extend(
            [
                "phase",
            ]
        )
        self.initialState = self.getState()
        self.faction = "monster"

        self.solvers.extend(["NaiveMurderQuest"])

    # bad code: specific code in generic class
    def die(self, reason=None, addCorpse=True):
        """
        kill the monster

        Parameters:
            reason: how the moster was killed
            addCorpse: a flag determining wether or not a corpse should be added
        """

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
                new = src.items.itemMap["Mold"]()
                self.container.addItem(new, self.getPosition())
                new.startSpawn()

            super().die(reason, addCorpse=False)
        else:
            super().die(reason, addCorpse)

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
            "s": [
                "o",
                "p",
                "f",
                "$",
                "=",
                "a",
                "a",
                "$",
                "=",
                "s",
                "s",
                "$",
                "=",
                "w",
                "w",
                "$",
                "=",
                "d",
                "d",
                "j",
            ]
        }
        self.macroState["macros"]["m"] = []
        for i in range(0, 8):
            self.macroState["macros"]["m"].extend(["_", "s"])
            self.macroState["macros"]["m"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["m"].append(random.choice(["a", "w", "s", "d"]))
        self.macroState["macros"]["m"].extend(["_", "m"])
        self.macroState["commandKeyQueue"] = [("_", []), ("m", [])]

    def enterPhase4(self):
        """
        enter a new evolution state and start to hunt people
        """

        self.phase = 4
        self.macroState["macros"] = {
            "e": ["1", "0", "j", "m"],
            "s": [
                "o",
                "p",
                "M",
                "$",
                "=",
                "a",
                "a",
                "$",
                "=",
                "w",
                "w",
                "$",
                "=",
                "d",
                "d",
                "$",
                "=",
                "s",
                "s",
                "_",
                "e",
            ],
            "w": [],
            "f": ["%", "c", "_", "s", "_", "w", "_", "f"],
        }
        for i in range(0, 4):
            self.macroState["macros"]["w"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["w"].append(random.choice(["a", "w", "s", "d"]))
        self.macroState["commandKeyQueue"] = [("_", []), ("f", [])]

    def enterPhase5(self):
        """
        enter a new evolution state and start a new faction
        """

        self.phase = 5
        self.faction = ""
        for i in range(0, 5):
            self.faction += random.choice("abcdefghiasjlkasfhoiuoijpqwei10934009138402")
        self.macroState["macros"] = {
            "j": 70 * ["J", "f"] + ["m"],
            "s": [
                "o",
                "p",
                "M",
                "$",
                "=",
                "a",
                "a",
                "$",
                "=",
                "w",
                "w",
                "$",
                "=",
                "d",
                "d",
                "$",
                "=",
                "s",
                "s",
                "k",
                "j",
                "j",
                "j",
                "k",
            ],
            "w": [],
            "k": [
                "o",
                "p",
                "e",
                "$",
                "=",
                "a",
                "a",
                "m",
                "$",
                "=",
                "w",
                "w",
                "m",
                "$",
                "=",
                "d",
                "d",
                "m",
                "$",
                "=",
                "s",
                "s",
                "m",
            ],
            "f": ["%", "c", "_", "s", "_", "w", "_", "k", "_", "f"],
        }
        for i in range(0, 8):
            self.macroState["macros"]["w"].append(str(random.randint(0, 9)))
            self.macroState["macros"]["w"].append(random.choice(["a", "w", "s", "d"]))
            self.macroState["macros"]["w"].append("m")
        self.macroState["commandKeyQueue"] = [("_", []), ("f", [])]

    # bad code: should listen to itself instead
    def changed(self, tag="default", info=None):
        """
        call callbacks for events and trigger evolutionary steps

        Parameters:
            tag: the type of event triggered
            info: additional information
        """

        if self.phase == 1 and self.satiation > 900:
            self.enterPhase2()
        if len(self.inventory) == 10:
            fail = False
            for item in self.inventory:
                if not item.type == "Corpse":
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

        Returns:
            what the monster looks like
        """

        if self.phase == 2:
            return src.canvas.displayChars.monster_feeder
        elif self.phase == 3:
            return src.canvas.displayChars.monster_grazer
        elif self.phase == 4:
            return src.canvas.displayChars.monster_corpseGrazer
        elif self.phase == 5:
            return src.canvas.displayChars.monster_hunter
        return src.canvas.displayChars.monster_spore


class Exploder(Monster):
    """
    a monster that explodes on death
    """

    charType = "Exploder"

    def __init__(
        self,
        display="🝆~",
        xPosition=0,
        yPosition=0,
        quests=[],
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

        self.explode = True
        self.attributesToStore.extend(["explode"])

    def render(self):
        """
        render the monster

        Returns:
            what the moster looks like
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
            new = src.items.itemMap["FireCrystals"](creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.container.addItems([new])
            if self.explode:
                new.startExploding()

        super().die(reason=reason, addCorpse=False)


characterMap = {
    "Character": Character,
    "Monster": Monster,
    "Exploder": Exploder,
    "Mouse": Mouse,
}


def getCharacterFromState(state):
    """
    get item instances from dict state
    """

    character = characterMap[state["type"]](characterId=state["id"])
    src.saveing.loadingRegistry.register(character)
    character.setState(state)
    return character
