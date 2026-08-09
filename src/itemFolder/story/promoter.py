import src
import random

class Promoter(src.items.Item):
    '''
    ingame item for marking official progress in the hierarchy
    '''
    type = "Promoter"
    description = "Allows to get promotions"
    name = "promoter"
    def __init__(self,):
        super().__init__(display="PR")
        self.faction = None
        self.walkable = False
        self.bolted = True

    def apply(self,character):
        '''
        handle activation by trying to promote the user
        '''

        text = [f"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You put your head into the machine."),"""

Its tendrils reach out and touch your implant.
"""]
        submenue = character.showTextMenu(text, do_not_scale=True, tag="promotionIntro")
        submenue.followUp = {
            "container": self,
            "method": "promotion_loop",
            "params": {"character":character},
        }

    def promotion_loop(self,extraInfo):
        '''
        handle activation by trying to promote the user
        '''

        # unpack parameters
        character = extraInfo["character"]

        # filter input
        if not self.faction:
            self.faction = character.faction

        # check if promotion to rank 5 applies
        highestAllowed = None
        if not character.rank or character.rank > 5:
            numCharacters = 0
            terrain = character.getTerrain()
            for checkChar in terrain.getAllCharacters():
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
                    character.changed("failed promotion",{"rank":5})

                    src.gamestate.gamestate.stern["rank5promotionfailed"] = True

                    text = ["""

""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Promotions from rank 6 to rank 5 are blocked."),"""

There need to be at least 1 clone besides you on the base to allow any promptions.
"""]
                    character.showTextMenu(text, do_not_scale=True)

                    character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                    return
            else:
                highestAllowed = 5

        # check if promotion to rank 4 applies
        if not character.rank or character.rank > 4:
            terrain = character.getTerrain()
            if len(terrain.rooms) < 7:
                if not highestAllowed:
                    character.addMessage(f"promotions locked")
                    character.changed("failed promotion",{"rank":4})

                    src.gamestate.gamestate.stern["rank4promotionfailed"] = True

                    text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Promotions from rank 5 to rank 4 are blocked."),"""

The base needs to consist out of at least 6 rooms.
Build more rooms.
"""]
                    character.showTextMenu(text, do_not_scale=True)
                    character.changed("promotion blocked",{"reason":"needs base with at least 6 rooms"})
                    return
            elif highestAllowed == 5 or character.rank == 5:
                highestAllowed = 4

        # check if promotion to rank 3 applies
        if not character.rank or character.rank > 3:
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

            if numCharacters < 4:
                if not highestAllowed:
                    character.addMessage(f"promotions locked")
                    character.changed("failed promotion",{"rank":3})

                    src.gamestate.gamestate.stern["rank3promotionfailed"] = True

                    text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Promotions from rank 4 to rank 3 are blocked."),"""
Enemies are nearby.

There need to be at least 3 clones besides you on the base to allow any promptions.
"""]
                    character.showTextMenu(text, do_not_scale=True)
                    character.changed("promotion blocked",{"reason":"terrain needs cleared from enemies"})
                    return
            elif highestAllowed == 4 or character.rank == 4:
                highestAllowed = 3

        # check if promotion to rank 2 applies
        if not character.rank or character.rank > 2:
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
                    character.changed("failed promotion",{"rank":2})

                    src.gamestate.gamestate.stern["rank2promotionfailed"] = True

                    text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Promotions from rank 3 to rank 2 are blocked."),"""

Kill all enemies on this terrain, to unlock the promotions to rank 2.
"""]
                    character.showTextMenu(text, do_not_scale=True)

                    character.changed("promotion blocked",{"reason":"needs 4 clones on base"})
                    return
            elif highestAllowed == 3 or character.rank == 3:
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

        if not character.rank:
            character.rank = 6

        while character.rank > highestAllowed:
            options = []
            extraDescriptions = {}
            text = None
            if character.rank == 6:
                options.append(("special attacks","special attacks"))
                extraDescriptions["special attacks"] = "your alternate attack is a selection of special attacks"
                options.append(("swap attacks","swap attack"))
                extraDescriptions["swap attacks"] = "your alternate attack allows you to switch places the character that was attacked"
                text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You are getting promoted for rank 6 to rank 5."),"""
Only 4 ranks are left before reaching rank 1.

As a reward you may select a close combat perk.
You can only have one close combat perk
"""]
            if character.rank == 5:
                options.append(("endurance run","endurance run"))
                extraDescriptions["endurance run"] = "your alternate movement only costs 80% time, but costs 1 exhaustion"
                options.append(("jump","jump"))
                extraDescriptions["jump"] = "your alternate movement only costs 50% time, but costs 5 exhaustion"
                text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You are getting promoted for rank 5 to rank 4."),"""
Only 3 ranks are left before reaching rank 1.

As a a reward you may select a special movement perk.
You can only have one special movement perk 
"""]
            if character.rank == 4:
                options = []
                extraDescriptions = {}
                options.append(("line shot","line shot"))
                extraDescriptions["line shot"] = "your ranged attach is shooting in a straight line north south west or east"
                options.append(("ramdom target shot","ramdom target shot"))
                extraDescriptions["ramdom target shot"] = "your ranged attach is shooting in random target in the roon"
                text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You are getting promoted for rank 4 to rank 3."),"""
Only 2 ranks are left before reaching rank 1.

As a reward you may select a ranged attack perk.
You can only have one ranged attack perk 
"""]
            if character.rank == 3:
                options.append(("max health boost","max health boost"))
                extraDescriptions["max health boost"] = "2 times the maxHP"
                options.append(("movement speed boost","movement speed boost"))
                extraDescriptions["movement speed boost"] = "movement and attacks only costs 50% time"
                text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You are getting promoted for rank 3 to rank 2."),"""
Only 1 ranks are left before reaching rank 1.

As a a reward for getting promoted from rank 3 to rank 2 you can select a attribute perk.
You can only have one attribute perk 
"""]

            if options:

                text.extend(["""

""",(src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"What do you choose as your reward?"),"""
"""])
                submenu = src.menues.menuMap["SelectionMenu"](
                    text = text,
                    options=options,
                    targetParamName="rewardType",
                    extraDescriptions=extraDescriptions,
                    tag="promotionRewardSelection",
                )
                submenu.do_not_scale = True

                character.add_submenu(submenu)
                submenu.followUp = {
                    "container": self,
                    "method": "get_rank_reward",
                    "params": extraInfo,
                }
                character.runCommandString("~",nativeKey=True)
                src.interaction.send_tracking_ping(f"got rank {character.rank-1} promotion")
                return

            self.do_promotion(extraInfo)

        text = [f"""
The tendrils retreat.

""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),f"You are rank {character.rank} now."),"""
"""]
        character.showTextMenu(text, do_not_scale=True)

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

        rewardType = extraInfo.get("rewardType")
        del extraInfo["rewardType"]

        rewardText = None
        specialAttackText = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You got an attack perk."),"""

You can do an alternative attack by pressing shift when attacking.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""
For example d will attack an enemy to the east normally and 
pressing D will do an alternative attack to an enemy to the east."""),"""

The alternative attacks usually cost exhaustion.
If you have more than 10 exhaustion you will do much less damage.
So try not to exeed 10 exhaustion.


"""]
        if rewardType == "special attacks":
            rewardText = [specialAttackText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose \"special attacks\" as alternate attack."),"""

You will be able to choose from a variety of attacks.
Each attack has a different costs and advantages.
You will figure it out.
"""]
        if rewardType == "swap attacks":
            rewardText = [specialAttackText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose a \"swap attack\" as alternate attack."),"""

This allows you to swap places with an enemy.
This should allow you to get out of tricky situations
"""]

        specialMomenemtText = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You got a special movement perk."),"""

You can do special movements by pressing shift when walking.
Bumping into enemies will not do a special movement!

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""
For example d will move you to the east normally and 
pressing D will do a special movement towards the east."""),"""

"""]
        if rewardType == "jump":
            rewardText = [specialMomenemtText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose \"jump\" as special movement."),"""

This means you can move a fast a few times.

You will move 50% faster, but each jump will cost you 5 exhaustion.
You cannot jump, if you have 10 or more exhaustion.
"""]
        if rewardType == "endurance run":
            rewardText = [specialMomenemtText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose \"endurance run\" as special movement."),"""

This means you can move a bit faster but for a relatively long time.

Each step you take will be 20% faster, but will cost you 1 exhaustion.
You cannot run, if you have 10 or more exhaustion.
"""]

        rangedCombatText = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You got a ranged combat perk."),"""

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"You can do a ranged combat attack by pressing f."),"""

"""]
        if rewardType == "line shot":
            rewardText = [rangedCombatText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose \"line shot\" as your ranged combat perk."),"""

This means you can shoot in a straight line from your character.
This means you can target your shot, but only target a few spots.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"After pressing f you will be promted for what direction you want to fire in."),"""
Each shot will cost you 1 Bolt.
"""]
        if rewardType == "ramdom target shot":
            rewardText = [rangedCombatText,"""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You chose \"random target shot\" as your ranged combat perk."),"""
Simple, but not ineffective.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"You press f and somebody gets shot."),"""
A random enemy is targeted.
Each shot will cost you 1 Bolt.
"""]

        attributeBonusText = ["""
You got an attribute bonus perk. 

This is an improvement on one of your stats.
You don't need to activate this perk.

"""]

        if rewardType == "max health boost":
            rewardText = [attributeBonusText,"""
You have twice as much max HP now!
"""]
        if rewardType == "movement speed boost":
            rewardText = [attributeBonusText,"""
You move twice as fast now.
"""]

        if rewardText:
            submenu = character.showTextMenu(rewardText)
            submenu.followUp = {
                "container": self,
                "method": "do_promotions",
                "params": extraInfo,
            }
            return
    
        self.do_promotions(extraInfo)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

# register item type
src.items.addType(Promoter)
