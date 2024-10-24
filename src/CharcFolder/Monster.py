import random

import src
import src.characters


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

    # bad code: specific code in generic class
    def die(self, reason=None, addCorpse=True, killer=None):
        """
        special handle corpse spawning
        """

        if not addCorpse:
            super().die(reason, addCorpse=False, killer=killer)
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

            super().die(reason, addCorpse=False, killer=killer)
        else:
            new = src.items.itemMap["MoldFeed"]()
            if self.container:
                self.container.addItem(new, self.getPosition())
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

            render = [(src.characters.urwid.AttrSpec(colorHealth, "#444"), "🝆"),(src.characters.urwid.AttrSpec(colorDamage, "#444"), "-")]
        elif self.phase == 3:
            render = src.canvas.displayChars.monster_grazer
        elif self.phase == 4:
            render = src.canvas.displayChars.monster_corpseGrazer
        elif self.phase == 5:
            render = src.canvas.displayChars.monster_hunter

        return render

src.characters.add_character(Monster)
