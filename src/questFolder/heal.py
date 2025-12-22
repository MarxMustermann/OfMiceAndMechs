import src
import random

class Heal(src.quests.MetaQuestSequence):
    type = "Heal"
    lowLevel = True

    def __init__(self, description="heal",noWaitHeal=False,noVialHeal=False,reason=None):
        super().__init__()
        self.metaDescription = description
        self.noWaitHeal = noWaitHeal
        self.noVialHeal = noVialHeal
        self.reason = reason

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"""
You are hurt. Heal yourself{reasonString}.

You can heal yourself using vials.
Use vials to heal yourself.
Press JH to auto heal.

"""
        return text

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # handle menus
        if character.macroState["submenue"]:
            return (None,(["esc"],"close the menu"))

        # flee from enemies
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Flee"](reason="have the opportunity to heal")
            return ([quest],None)

        # properly enter rooms
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        # heal using vials
        try:
            self.noVialHeal
        except:
            self.noVialHeal = False
        if not self.noVialHeal:
            foundVial = None
            for item in character.inventory:
                if item.type == "Vial" and item.uses > 0:
                    foundVial = item
            if foundVial:
                return (None,("JH","drink from vial"))

        # activate correct item when marked
        action = self.generate_confirm_activation_command(allowedItems=("Regenerator","CoalBurner"))
        if action:
            return action

        # heal using coal burners
        terrain = character.getTerrain()
        rooms = terrain.rooms[:]
        if character.container.isRoom:
            rooms.insert(0,character.container)
        for room in rooms:
            items = room.getItemsByType("CoalBurner",needsBolted=True)
            foundBurners = []
            for item in items:
                if not item.getMoldFeed(character):
                    continue
                foundBurners.append(item)

            if not foundBurners:
                continue

            if not character.container == room:
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get to a CoalBurner")
                return ([quest],None)

            for item in foundBurners:
                direction = None
                if character.getPosition(offset=(1,0,0)) == item.getPosition():
                    direction = "d"
                if character.getPosition(offset=(-1,0,0)) == item.getPosition():
                    direction = "a"
                if character.getPosition(offset=(0,1,0)) == item.getPosition():
                    direction = "s"
                if character.getPosition(offset=(0,-1,0)) == item.getPosition():
                    direction = "w"

                if direction:
                    interactionCommand = "J"
                    if "advancedInteraction" in character.interactionState:
                        interactionCommand = ""
                    return (None,(interactionCommand+direction,"inhale smoke"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=random.choice(foundBurners).getPosition(),ignoreEndBlocked=True,reason="be able to use the CoalBurner")
            return ([quest],None)

        # heal by passing time
        if not self.noWaitHeal:
            if character.container.isRoom and character.container.tag == "temple":
                regenerator = character.container.getItemByType("Regenerator",needsBolted=True)
                if regenerator and regenerator.mana_charges:
                    direction = None
                    if character.getPosition(offset=(1,0,0)) == regenerator.getPosition():
                        direction = "d"
                    if character.getPosition(offset=(-1,0,0)) == regenerator.getPosition():
                        direction = "a"
                    if character.getPosition(offset=(0,1,0)) == regenerator.getPosition():
                        direction = "s"
                    if character.getPosition(offset=(0,-1,0)) == regenerator.getPosition():
                        direction = "w"

                    if direction:
                        interactionCommand = "J"
                        if "advancedInteraction" in character.interactionState:
                            interactionCommand = ""
                        return (None,(interactionCommand+direction,"activate the regenerator"))
                    else:
                        quest = src.quests.questMap["GoToPosition"](targetPosition=regenerator.getPosition(),ignoreEndBlocked=True,reason="be able to use the Regenerator")
                        return ([quest],None)
                else:
                    return (None,("..........","wait to heal"))
            for room in rooms:
                if room.tag == "temple":
                    quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get to the Regenerator")
                    return ([quest],None)

        # fail
        return self._solver_trigger_fail(dryRun,"no way to heal")

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.health < character.adjustedMaxHealth:
            return False

        if not dryRun:
            self.postHandler()
        return True


    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "healed")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return
    
        self.triggerCompletionCheck(self.character,dryRun=False)

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
                room = character.container
                items = room.getItemsByType("CoalBurner",needsBolted=True)
                foundBurners = []
                for item in items:
                    if not item.getMoldFeed(character):
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(Heal)
