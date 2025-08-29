import src
import random

class Promoter(src.items.Item):
    '''
    ingame item for marking official progress in the hierarchy
    '''
    type = "Promoter"
    def __init__(self,):
        super().__init__(display="PR")
        self.faction = None
        self.walkable = False
        self.bolted = True

    def apply(self,character):
        '''
        handle activation by trying to promote the user
        '''

        submenu = src.menuFolder.textMenu.TextMenu(f"""
You put your head into the machine.

Its tendrils reach out and touch your implant.

""")
        character.macroState["submenue"] = submenu
        submenu.followUp = {
            "container": self,
            "method": "promotion_loop",
            "params": {"character":character},
        }
        character.runCommandString("~",nativeKey=True)

    def promotion_loop(self,extraInfo):
        '''
        handle activation by trying to promote the user
        '''

        # unpack parameters
        character = extraInfo["character"]

        # filter input
        if not character.rank:
            character.addMessage("you need a rank to use this machine")
            return
        if not self.faction:
            self.faction = character.faction

        # check if promotion to rank 5 applies
        highestAllowed = None
        if character.rank > 5:
            numCharacters = 0
            terrain = character.getTerrain()
            for checkChar in terrain.characters:
                if not checkChar.faction == character.faction:
                    continue
                if not checkChar.charType == "Clone":
                    continue
                if checkChar.burnedIn:
                    continue
                numCharacters += 1
            for room in terrain.rooms:
                for checkChar in room.characters:
                    if not checkChar.faction == character.faction:
                        continue
                    if not checkChar.charType == "Clone":
                        continue
                    if checkChar.burnedIn:
                        continue
                    numCharacters += 1

            if numCharacters < 2:
                if not highestAllowed:
                    character.addMessage(f"promotions locked")

                    submenu = src.menuFolder.textMenu.TextMenu("""
Promotions to rank 5 are blocked.

There need to be at least 1 clone besides you on the base to allow any promptions.
""")
                    character.macroState["submenue"] = submenu
                    character.runCommandString("~",nativeKey=True)

                    character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                    return
            else:
                highestAllowed = 5

        # check if promotion to rank 4 applies
        if character.rank > 4:
            terrain = character.getTerrain()
            if len(terrain.rooms) < 7:
                if not highestAllowed:
                    character.addMessage(f"promotions locked")

                    submenu = src.menuFolder.textMenu.TextMenu("""
Promotions to rank 4 are blocked.

The base needs to consist out of at least 6 rooms.
Build more rooms.
""")
                    character.macroState["submenue"] = submenu
                    character.runCommandString("~",nativeKey=True)

                    character.changed("promotion blocked",{"reason":"needs base with at least 6 rooms"})
                    return
            else:
                highestAllowed = 4

        # check if promotion to rank 2 applies
        if character.rank > 2:
            foundEnemies = []
            terrain = self.getTerrain()
            for otherChar in terrain.characters:
                if otherChar.faction == character.faction:
                    continue
                foundEnemies.append(otherChar)

            for room in terrain.rooms:
                for otherChar in room.characters:
                    if otherChar.faction == character.faction:
                        continue
                    foundEnemies.append(otherChar)

            if foundEnemies:
                if not highestAllowed:
                    character.addMessage(f"promotions locked")

                    submenu = src.menuFolder.textMenu.TextMenu("""
Promotions to rank 2 are blocked.
Enemies are nearby.

Kill all enemies on this terrain, to unlock the promotions to rank 2.
""")
                    character.macroState["submenue"] = submenu
                    character.runCommandString("~",nativeKey=True)

                    character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                    return
            else:
                highestAllowed = 2

        # abort if there is no update
        if highestAllowed is None:
            return

        # do the actual promotions
        extraInfo["highestAllowed"] = highestAllowed
        self.do_promotions(extraInfo)

    def do_promotions(self,extraInfo):
        '''
        show the UI for actually getting the promotions
        '''

        # unpack parameters
        character = extraInfo["character"]
        highestAllowed = extraInfo["highestAllowed"]

        while character.rank > highestAllowed:
            if character.rank == 6:
                options = []
                options.append(("special attacks","special attacks"))
                options.append(("swap attacks","swap attacks"))
                text = """
As a a reward for reaching rank 5 you can select a close combat perk.

You can only have one close combat perk
"""
                submenu = src.menuFolder.selectionMenu.SelectionMenu(
                    text = text,
                    options=options,
                    targetParamName="rewardType"
                )

                character.macroState["submenue"] = submenu
                submenu.followUp = {
                    "container": self,
                    "method": "get_rank_reward",
                    "params": extraInfo,
                }
                character.runCommandString("~",nativeKey=True)
                return
            if character.rank == 5:
                options = []
                options.append(("endurance run","endurance run"))
                options.append(("jump","jump"))
                text = """
As a a reward for reaching rank 4 you can select a special movement perk.

You can only have one special movement perk 
"""
                submenu = src.menuFolder.selectionMenu.SelectionMenu(
                    text = text,
                    options=options,
                    targetParamName="rewardType"
                )

                character.macroState["submenue"] = submenu
                submenu.followUp = {
                    "container": self,
                    "method": "get_rank_reward",
                    "params": extraInfo,
                }
                character.runCommandString("~",nativeKey=True)
                return
            if character.rank == 4:
                options = []
                options.append(("line shot","line shot"))
                options.append(("ramdom target shot","ramdom target shot"))
                text = """
As a a reward for reaching rank 3 you can select a ranged attack perk.

You can only have one ranged attack perk 
"""
                submenu = src.menuFolder.selectionMenu.SelectionMenu(
                    text = text,
                    options=options,
                    targetParamName="rewardType"
                )

                character.macroState["submenue"] = submenu
                submenu.followUp = {
                    "container": self,
                    "method": "get_rank_reward",
                    "params": extraInfo,
                }
                character.runCommandString("~",nativeKey=True)
                return
            if character.rank == 3:
                options = []
                options.append(("max health boost","max health boost"))
                options.append(("movement speed boost","movement speed boost"))
                text = """
As a a reward for reaching rank 2 you can select a attribute perk.

You can only have one attribute perk 
"""
                submenu = src.menuFolder.selectionMenu.SelectionMenu(
                    text = text,
                    options=options,
                    targetParamName="rewardType"
                )

                character.macroState["submenue"] = submenu
                submenu.followUp = {
                    "container": self,
                    "method": "get_rank_reward",
                    "params": extraInfo,
                }
                character.runCommandString("~",nativeKey=True)
                return
            self.do_promotion(extraInfo)

        submenu = src.menuFolder.textMenu.TextMenu(f"""
The tendrils retrive.

You are rank {character.rank} now.
""")
        character.macroState["submenue"] = submenu
        character.runCommandString("~",nativeKey=True)

    def get_rank_reward(self, extraInfo):
        '''
        dispense a reward for getting promoted
        '''

        # unpack parameters
        character = extraInfo["character"]
        rewardType = extraInfo["rewardType"]

        if rewardType is None:
            return

        if rewardType == "special attacks":
            character.hasSpecialAttacks = True
        if rewardType == "swap attacks":
            character.hasSwapAttack = True
        if rewardType == "endurance run":
            character.hasRun = True
        if rewardType == "jump":
            character.hasJump = True
        if rewardType == "line shot":
            character.hasLineShot = True
        if rewardType == "ramdom target shot":
            character.hasRandomShot = True
        if rewardType == "max health boost":
            character.hasMaxHealthBoost = True
        if rewardType == "movement speed boost":
            character.hasMovementSpeedBoost = True
        self.do_promotion(extraInfo)

    def do_promotion(self,extraInfo):
        '''
        do an individual rank upgrade
        '''
        # unpack parameters
        character = extraInfo["character"]

        character.rank -= 1
        character.addMessage(f"you were promoted to rank {character.rank}")
        character.changed("got promotion",{})

        self.do_promotions(extraInfo)

# register item type
src.items.addType(Promoter)
