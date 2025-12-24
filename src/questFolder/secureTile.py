import random

import src


class SecureTile(src.quests.questMap["GoToTile"]):
    type = "SecureTile"

    def __init__(self, description="secure tile", toSecure=None, endWhenCleared=False, reputationReward=0,rewardText=None,strict=False,alwaysHuntDown=False,reason=None,story=None, wandering = False, lifetime=None, simpleAttacksOnly=False):
        super().__init__(description=description,targetPosition=toSecure,lifetime=lifetime)
        self.metaDescription = description
        self.endWhenCleared = endWhenCleared
        self.reputationReward = reputationReward
        self.rewardText = rewardText
        self.huntdownCooldown = 0
        self.strict = strict
        self.alwaysHuntDown = alwaysHuntDown
        self.reason = reason
        self.story = story
        self.wandering = wandering
        if toSecure is not None and (toSecure[0] > 13 or toSecure[1] > 13):
            raise Exception("Out of bounds" + str(toSecure))
        self.simpleAttacksOnly = simpleAttacksOnly

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = f", to {self.reason}"
        storyString = ""
        if self.story:
            storyString = self.story+"\n"
        text  = f"""{storyString}Secure the tile {self.targetPosition}{reasonString}.

This means you should go to the tile and kill all enemies you find."""
        if not self.endWhenCleared:
            text = "\n"+text+"\n\nStay there and kill all enemies arriving"
            if self.wandering:
                text += " and sweeping the area for any potential danger"
        else:
            text = "\n"+text+"\n\nThis quest will end after you do this"
        text += """

You can attack enemies by walking into them.
But you can use your environment to your advantage, too.
Try luring enemies into landmines or detonating some bombs."""

        return text

    def wrapedTriggerCompletionCheck2(self, extraInfo):
        if not self.active:
            return
        self.triggerCompletionCheck(extraInfo["character"],dryRun=False)

    def handleTileChange2(self,extraInfo={}):
        if not self.active:
            return
        self.triggerCompletionCheck(self.character,dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck2, "character died on tile")
        self.startWatching(character,self.handleTileChange2, "changedTile")

        super().assignToCharacter(character)

    def postHandler(self,character=None):
        if self.reputationReward and character:
            if self.rewardText:
                text = self.rewardText
            else:
                text = "securing a tile"
            character.awardReputation(amount=50, reason=text)
        super().postHandler()

    def triggerCompletionCheck(self,character=None,dryRun=True):

        if not character:
            return False

        if not self.endWhenCleared:
            return False

        if isinstance(character.container,src.rooms.Room):
            if character.container.xPosition == self.targetPosition[0] and character.container.yPosition == self.targetPosition[1]:
                if not character.getNearbyEnemies():
                    if not dryRun:
                        self.postHandler(character)
                    return True
        else:
            if character.xPosition//15 == self.targetPosition[0] and character.yPosition//15 == self.targetPosition[1]:
                if not character.getNearbyEnemies():
                    if not dryRun:
                        self.postHandler(character)
                    return True

        return False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        # handle most menues
        if character.macroState["submenue"] and character.macroState["submenue"].tag != "tileMovementmenu" and not ignoreCommands:
           return (None,(["esc"],"exit the menu")) 

        # heal
        if character.health < character.maxHealth - 20 and character.canHeal():
            return (None,("JH","heal"))

        # initiate actual combat
        if not self.strict:
            huntdownCooldown = self.huntdownCooldown
            huntdownCooldown -= 1
            if not dryRun:
                self.huntdownCooldown = huntdownCooldown
            if huntdownCooldown < 0:
                enemies = character.getNearbyEnemies()
                if enemies:
                    if self.alwaysHuntDown:
                        quest = src.quests.questMap["Huntdown"](target=random.choice(enemies),reason="ensure your enemy is dead")
                        return ([quest],None)
                    if not dryRun:
                        self.huntdownCooldown = 100
                    if random.random() < 0.3:
                        quest = src.quests.questMap["Huntdown"](target=random.choice(enemies),reason="ensure victory")
                        return ([quest],None)
                    else:
                        quest = src.quests.questMap["Fight"](simpleOnly=self.simpleAttacksOnly,reason="reduce danger")
                        return ([quest],None)
        enemies = character.getNearbyEnemies()
        if enemies:
            quest = src.quests.questMap["Fight"](simpleOnly=self.simpleAttacksOnly,reason="defend yourself")
            return ([quest],None)

        # go to the position to secure
        if character.getBigPosition() == self.targetPosition:

            # enter tiles properly
            pos = character.getSpacePosition()
            if pos == (0,7,0):
                return (None, ("d","enter tile"))
            if pos == (14,7,0):
                return (None, ("a","enter tile"))
            if pos == (7,0,0):
                return (None, ("s","enter tile"))
            if pos == (7,14,0):
                return (None, ("w","enter tile"))

            # wait for enemies
            enemies = character.getNearbyEnemies()
            if not enemies and not self.endWhenCleared:
                if self.wandering and random.random() < 0.2:
                    (x,y,_) = character.getSpacePosition()
                    x= src.helpers.clamp(x+int(random.uniform(-3,3)),2,11)
                    y= src.helpers.clamp(y+int(random.uniform(-3,3)),2,11)
                    quest = src.quests.questMap["GoToPosition"](targetPosition = (x,y),reason="get to a nicer spot",idleMovement=True)
                    return ([quest], None)
                if not character.rank and character.charType == "Clone":
                    return (None, ("....","wait"))
                else:
                    if character.xPosition == 0 or character.yPosition == 0 or character.xPosition == 12 or character.yPosition == 12:
                        (x,y,_) = character.getSpacePosition()
                        x= src.helpers.clamp(x+int(random.uniform(-3,3)),2,11)
                        y= src.helpers.clamp(y+int(random.uniform(-3,3)),2,11)
                        quest = src.quests.questMap["GoToPosition"](targetPosition = (x,y),idleMovement=True)
                        return ([quest], None)
                    return (None, (";","wait"))

        # let super class handle further details
        return super().getNextStep(character=character,ignoreCommands=ignoreCommands,dryRun=dryRun)

src.quests.addType(SecureTile)
