import src
import random

class DelveDungeon(src.quests.MetaQuestSequence):
    type = "DelveDungeon"

    def __init__(self, description="delve dungeon",targetTerrain=None,itemID=None,storyText=None, directSendback=False, suicidal=False, walkToTarget=False):
        questList = []
        super().__init__(questList, creator=None)
        self.metaDescription = description
        self.targetTerrain = targetTerrain
        self.itemID = itemID
        self.storyText = storyText
        self.directSendback = directSendback
        self.suicidal = suicidal
        self.walkToTarget = walkToTarget

    def generateTextDescription(self):
        text = ""

        godname = src.gamestate.gamestate.gods[self.itemID]["name"]

        if self.storyText:
            text += f"""
{self.storyText}
"""
        text += f"Delve the dungeon on tile {self.targetTerrain} and retieve a GlassHeart.\n"

        if self.itemID:
            text += f"""
This dungeon is home of the god {godname} and holds its heart.
Remove the heart from the GlassStatue holding it.
"""
        else:
            text += """
Fetch any glass heart.
"""
        text += """
After fetching the glass heart return the glass heart to your base and set it into the glass statue.
"""
        if self.directSendback:
            text += """
directSendback"""
        if self.suicidal:
            text += """
suicidal"""
        return text

    def handleDelivery(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleDelivery, "deliveredSpecialItem")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None, dryRun=True):
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # hande weird edge cases
        if self.subQuests:
            return (None,None)

        # enter room properly
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
        
        # activate GlassStatue if marked
        activationCommand = "j"
        description = "activate glass statue"
        if self.directSendback:
            activationCommand = "cr"
            description = "return GlassHeart"
        command = self.generate_confirm_interaction_command(allowedItems=["GlassStatue"],activationCommand=activationCommand)
        if command:
            return command

        # navigate menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "GlassStatue":
                command = submenue.get_command_to_select_option("getSetHeart")
                if command:
                    return (None,(command,"get/set glass heart"))
            return (None,(["esc"],"exit submenu"))

        # close other menus
        if not ignoreCommands and character.macroState.get("submenue"):
            return (None,(["esc"],"exit submenu"))

        # check if the character has the glass heart
        hasSpecialItem = None
        for item in character.inventory:
            if item.type != "SpecialItem":
                continue
            hasSpecialItem = item

        terrain = character.getTerrain()

        # get the glass heart
        if not hasSpecialItem:
            # handle beeing hurt
            #if not self.suicidal and character.health < character.maxHealth*0.75:
            if character.health < character.maxHealth*0.75:
                # kill direct threats
                if character.getNearbyEnemies():
                    quest = src.quests.questMap["Fight"](suicidal=True,reason="protect yourself")
                    return ([quest],None)

                if character.canHeal():
                    quest = src.quests.questMap["Heal"](reason="be able to fight better")
                    return ([quest],None)

                # wait to heal
                #if character.health < character.maxHealth*0.75:
                #    return (None,("..............","wait to heal"))

                # abort
                #if not dryRun:
                #    self.fail("too hurt")
                #return (None,None)

            # kill direct threats
            if character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"](suicidal=True,reason="get rid of threats")
                return ([quest],None)

            # prepare for delving the dungeon
            currentTerrain = character.getTerrain()
            if currentTerrain == character.getHomeTerrain():

                # upgrade equipment
                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("SwordSharpener"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["SharpenPersonalSword"](reason="increase damage")
                            return ([quest],None)
                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("ArmorReinforcer"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["ReinforcePersonalArmor"](reason="be better protected")
                            return ([quest],None)

                # heal
                if character.health < character.adjustedMaxHealth:
                    readyCoalBurner = False
                    for room in currentTerrain.rooms:
                        for coalBurner in room.getItemsByType("CoalBurner"):
                            if not coalBurner.getMoldFeed(character):
                                continue
                            if not coalBurner.bolted:
                                continue
                            readyCoalBurner = True
                    if readyCoalBurner:
                        quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=True,reason="adventure in good health")
                        return ([quest],None)

                # make sure to be unencumbered
                for item in character.inventory:
                    if item.walkable == False:
                        quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="not be slowed down by big items")
                        return ([quest],None)

                # ensure basic equipment
                if not character.weapon or not character.armor:
                    quest = src.quests.questMap["Equip"](tryHard=True,reason="delve the dungeon well equipped")
                    return ([quest],None)

                # ensure clean traps
                for room in terrain.rooms:
                    if not room.tag == "trapRoom":
                        continue
                    numItems = 0
                    for item in room.itemsOnFloor:
                        if item.bolted == False:
                            if item.getPosition() not in room.walkingSpace:
                                continue
                            numItems += 1
                    if numItems > 4:
                        # clean the trap room yourself
                        quests = []
                        quest = src.quests.questMap["ClearTile"](targetPositionBig=room.getPosition(),reason="ensure the traps work")
                        quests.append(quest)

                        # ensure at least one Clone has Room building as highest prio
                        foundClone = False
                        for candidate in terrain.getAllCharacters():
                            if not candidate.faction == character.faction:
                                continue
                            if candidate == character:
                                continue
                            if not candidate.getRandomProtisedDuties():
                                continue
                            if not candidate.getRandomProtisedDuties()[0] == "cleaning":
                                continue
                            foundClone = True
                        if not foundClone:
                            quest = src.quests.questMap["EnsureMaindutyClone"](dutyType="cleaning",reason="have somebody clean up the traps")
                            quests.append(quest)

                        return (list(reversed(quests)),None)

                # wait for wave to pass
                if terrain.alarm:
                    remaining_time = 15*15*15-src.gamestate.gamestate.tick%(15*15*15)
                    if remaining_time < 1000:
                        quest = src.quests.questMap["BeUsefull"](lifetime=remaining_time,reason="wait for wave to pass")
                        return ([quest],None)

            # loot current room
            if currentTerrain != character.getHomeTerrain():
                if character.container.isRoom and character.getFreeInventorySpace() and isinstance(character,src.characters.characterMap["Clone"]):
                    for item in character.container.itemsOnFloor:
                        if not item.type in ("GooFlask","Vial","Bolt","Grindstone","Implant","Corpse","MemoryFragment","ChitinPlates",):
                            continue
                        quest = src.quests.questMap["LootRoom"](targetPositionBig=character.container.getPosition(),endWhenFull=True,reason="have more nice things")
                        return ([quest],None)

            # get to the terrain the dungeon is on
            if terrain.xPosition != self.targetTerrain[0] or terrain.yPosition != self.targetTerrain[1]:

                # try to teleport to the dungeon
                if self.itemID:
                    for room in terrain.rooms:
                        items = room.getItemsByType("GlassStatue")
                        for item in items:
                            if item.itemID != self.itemID:
                                continue
                            if item.charges < 5:
                                continue

                            quest = src.quests.questMap["ActivateGlassStatue"](targetPositionBig=room.getPosition(),targetPosition=item.getPosition(),reason="get to the dungeon")
                            return ([quest],None)

                # try to go to the dungeon using other means
                if not self.walkToTarget:
                    return self._solver_trigger_fail(dryRun,"no GlassStatue found")
                else:

                    # actually walk to the target terrain
                    quest = src.quests.questMap["GoToTerrain"](targetTerrain=(self.targetTerrain[0],self.targetTerrain[1],0),reason="reach the dungeon")
                    return ([quest],None)

            # check for exposed GlassHeart
            foundGlassHeart = None
            for room in terrain.rooms:
                for specialItem in room.getItemsByType("SpecialItem"):
                    if self.itemID and specialItem.itemID != self.itemID:
                        continue
                    foundGlassHeart = specialItem

            # eject GlassHeart
            if not foundGlassHeart:

                # find GlassStatue with GlassHeart
                foundGlassStatue = None
                for room in terrain.rooms:
                    for glassStatue in room.getItemsByType("GlassStatue"):
                        if not glassStatue.hasItem:
                            continue
                        if self.itemID and glassStatue.itemID != self.itemID:
                            continue
                        foundGlassStatue = glassStatue

                # fail on wierd state
                if not foundGlassStatue:
                    return self._solver_trigger_fail(dryRun,"no GlassStatue found")
            
                # go to GlassStatue
                if character.container != foundGlassStatue.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=foundGlassStatue.getBigPosition(),abortHealthPercentage=0.5,description="go to temple",reason="reach the GlassHeart")
                    quest.generatePath(character)
                    path = quest.path
                    if len(path):
                        return self.delveToRoomIfSafe(character,path,dryRun=dryRun)
                    return (None,None)
                if character.getDistance(foundGlassStatue.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=foundGlassStatue.getPosition(),ignoreEndBlocked=True,description="go to GlasStatue", reason="be able to extract the GlassHeart")
                    return ([quest],None)

                # activate GlassStatue
                directionCommand = None
                if character.getPosition(offset=(0,0,0)) == foundGlassStatue.getPosition():
                    directionCommand = "."
                if character.getPosition(offset=(1,0,0)) == foundGlassStatue.getPosition():
                    directionCommand = "d"
                if character.getPosition(offset=(0,1,0)) == foundGlassStatue.getPosition():
                    directionCommand = "s"
                if character.getPosition(offset=(-1,0,0)) == foundGlassStatue.getPosition():
                    directionCommand = "a"
                if character.getPosition(offset=(0,-1,0)) == foundGlassStatue.getPosition():
                    directionCommand = "w"
                if self.directSendback:
                    return (None,(directionCommand+"cr","return GlassHeart"))
                else:
                    activationCommand = "J"
                    if "advancedInteraction" in character.interactionState:
                        activationCommand = ""
                    return (None,(activationCommand+directionCommand,"eject GlassHeart"))

            # pick up GlassHeart
            if character.getPosition() != foundGlassHeart.getPosition():
                quest = src.quests.questMap["GoToPosition"](targetPosition=foundGlassHeart.getPosition(),description="go to GlassHeart",reason="be able to pick up the GlassHeart")
                return ([quest],None)
            if len(character.inventory) > 9:
                return (None,("L"+random.choice(["w","a","s","d"]),"clear inventory"))
            return (None,("k","pick up GlassHeart"))

        # go back home
        if terrain.xPosition != character.registers["HOMETx"] or terrain.yPosition != character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"](reason="go to your home territory")
            return ([quest],None)
        if not character.container.isRoom:
            quest = src.quests.questMap["GoHome"](reason="get into a room")
            return ([quest],None)

        # find GlassStatue to set the heart into
        foundGlassStatue = None
        for room in [character.container, *terrain.rooms]:
            for glassStatue in room.getItemsByType("GlassStatue"):
                if glassStatue.itemID == hasSpecialItem.itemID:
                    foundGlassStatue = glassStatue
                    break
            if foundGlassStatue:
                break

        # fail on weird state
        if not foundGlassStatue:
            return self._solver_trigger_fail(dryRun,"no GlassStatue found")

        # prepare to defend base
        if not terrain.alarm:
            quest = src.quests.questMap["ReadyBaseDefences"](reason="be prepared to the wave")
            return ([quest],None)

        # go to GlassStatue
        if foundGlassStatue.container != character.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=foundGlassStatue.getBigPosition(),description="go to temple",reason="be able to set the GlassHeart")
            return ([quest],None)
        if character.getDistance(glassStatue.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=glassStatue.getPosition(),ignoreEndBlocked=True,description="go to GlassStatue",reason="be able to set the GlassHeart")
            return ([quest],None)

        # activate GlassStatue
        directionCommand = None
        if character.getPosition(offset=(0,0,0)) == glassStatue.getPosition():
            directionCommand = "."
        if character.getPosition(offset=(1,0,0)) == glassStatue.getPosition():
            directionCommand = "d"
        if character.getPosition(offset=(0,1,0)) == glassStatue.getPosition():
            directionCommand = "s"
        if character.getPosition(offset=(-1,0,0)) == glassStatue.getPosition():
            directionCommand = "a"
        if character.getPosition(offset=(0,-1,0)) == glassStatue.getPosition():
            directionCommand = "w"
        activationCommand = "J"
        if "advancedInteraction" in character.interactionState:
            activationCommand = ""
        return (None,(activationCommand+directionCommand,"insert glass heart"))

    def delveToRoomIfSafe(self,character,path,dryRun=True):
        new_pos = character.getBigPosition()
        for direction in path:
            new_pos = (new_pos[0]+direction[0], new_pos[1]+direction[1], 0)
            rooms = character.getTerrain().getRoomByPosition(new_pos)
            if rooms:
                break

        tryNextTile = False
        if self.suicidal:
            tryNextTile = True

        rooms = character.getTerrain().getRoomByPosition(new_pos)
        if not rooms:
            tryNextTile = True
        
        if rooms and (not character.getStrengthSelfEstimate() < rooms[0].getEstimatedStrength()):
            tryNextTile = True

        if tryNextTile:
            quest = src.quests.questMap["GoToTile"](targetPosition=new_pos,description="go to temple",reason="reach the GlassHeart")
            return ([quest],None)

        if rooms:
            character.addMessage(f"char strength: {character.getStrengthSelfEstimate()}")
            character.addMessage(f"room strength: {rooms[0].getEstimatedStrength()}")

        if not dryRun:
            homeTerrain = src.gamestate.gamestate.terrainMap[character.registers["HOMETy"]][character.registers["HOMETx"]]
            for room in homeTerrain.rooms:
                for statue in room.getItemsByType("GlassStatue"):
                    if statue.itemID == self.itemID:
                        calculatedTries = int((rooms[0].getEstimatedStrength()-1)*10)

                        if statue.numTeleportsDone < calculatedTries:
                            statue.numTeleportsDone = calculatedTries

            text = """
The implant interrupts. This dungeon is too hard for you.

Become stronger and return."""
            character.macroState["submenue"] = src.menuFolder.textMenu.TextMenu(text)

        return self._solver_trigger_fail(dryRun,"dungeon too tough")

src.quests.addType(DelveDungeon)
