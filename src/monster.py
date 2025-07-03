import random

import src

# bad code: there is very specific code in here, so it it stopped to be a generic class
class Monster(src.characters.Character):
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

    def getCorpse(self):
        return src.items.itemMap["MoldFeed"]()

    # bad code: specific code in generic class
    def die(self, reason=None, addCorpse=True, killer=None):
        """
        special handle corpse spawning
        """
        if not addCorpse:
            super().die(reason, addCorpse=False, killer=killer)
            return

        corpse = self.getCorpse()
        if corpse is not None and self.container:
            self.container.addItem(corpse, self.getPosition())

        if addCorpse and hasattr(self.__class__,"lootTable"):
            lootTable = self.lootTable()
            loot = random.choices([item[0] for item in lootTable],[item[1] for item in lootTable])[0]
            if loot is not None:
                self.container.addItem(loot(),self.getPosition())

        super().die(reason, addCorpse=False, killer=killer)


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

    def color_for_multiplier(self, multiplier):
        range = self.multiplier_range(multiplier)

        color = (
            src.interaction.urwid.AttrSpec(
                src.interaction.urwid.AttrSpec.interpolate(
                    (255, 255, 255), (255, 16, 8), src.helpers.clamp(range, 0.0, 1.0)
                ),
                "black",
            ),
        )
        return color

    @staticmethod
    def get_random_multiplier():
        match src.gamestate.gamestate.difficulty:
            case "difficult":
                return random.uniform(1, 2 * 7)
            case "medium":
                return random.uniform(1, 1 * 4)
            case _:
                return random.uniform(1, 0.5 * 4)

    def multiplier_range(self, multiplier):
        match src.gamestate.gamestate.difficulty:
            case "difficult":
                range = multiplier / (2 * 7)
            case "easy":
                range = multiplier / (0.5 * 4)
            case _:
                range = multiplier / 4
        return range


src.characters.add_character(Monster)
