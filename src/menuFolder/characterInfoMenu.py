import json

import src

# bad code: should be abstracted
# bad code: uses global function to render
class CharacterInfoMenu(src.subMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "CharacterInfoMenu"

    def __init__(self, char=None):
        self.char = char
        self.skipKeypress = True
        super().__init__()
        self.page = 1

    def render(self,char):
        if char.dead:
            return ""

        text = ""

        armorValue = None
        if char.armor:
            armorValue = char.armor.armorValue
        weaponBaseDamage = None
        if char.weapon:
            weaponBaseDamage = char.weapon.baseDamage

        print(char.registers)

        text += "name:       %s\n" % char.name
        text += f"page: {self.page}\n"
        text += "\n"
        text += "\n"
        if self.page == 1:
            text += "health:       %s" % char.health + "\n"
            text += "max health:   %s" % char.adjustedMaxHealth + "\n"
            text += "exhaustion:   %s" % char.exhaustion + "\n"
            text += "\n"
            text += "baseDamage:   %s\n" % char.baseDamage
            text += "weapon:       %s\n" % weaponBaseDamage
            text += "armor:        %s\n" % armorValue
            text += "faction:      %s\n" % char.faction
            text += "time taken:   %s" % char.timeTaken + "\n"
            text += "combat value: %s" % char.getStrengthSelfEstimate() + "\n"

            if hasattr(char,"rank"):
                text += "rank:       %s\n" % char.rank
            if hasattr(char,"superior"):
                text += "superior:   %s\n" % char.superior
            text += "reputation: %s\n" % char.reputation
            flaskInfo = "-"
            if char.flask:
                flaskInfo = str(char.flask.uses)+" flask charges"
            text += f"satiation:  {char.satiation} ({flaskInfo})\n"

            statusEffectString = ""
            for statusEffect in char.statusEffects:
                statusEffectString += statusEffect.type + " (" + statusEffect.getShortCode() + "), "
            if not statusEffectString == "":
                statusEffectString = statusEffectString[:-2]
            text += f"status effects: %s\npress e to view a detailed buff list"%(statusEffectString,)
            
        if self.page == 2:
            text += "\n"
            text += f"movementSpeed:  {char.adjustedMovementSpeed}\n"
            text += f"attackSpeed:    {char.attackSpeed}\n"
            text += "\n"
            text += f"hasSpecialAttacks: {char.hasSpecialAttacks}\n"
            text += f"hasSwapAttack: {char.hasSwapAttack}\n"
            text += f"hasRun: {char.hasRun}\n"
            text += f"hasJump: {char.hasJump}\n"
            text += f"hasLineShot: {char.hasLineShot}\n"
            text += f"hasRandomShot: {char.hasRandomShot}\n"
            text += f"hasMovementSpeedBoost: {char.hasMovementSpeedBoost}\n"
            text += f"hasMaxHealthBoost: {char.hasMaxHealthBoost}\n"
            text += f"hasMagic: {char.hasMagic}\n"
            text += "\n"
            if char.lastMapSync:
                text += f"lastMapSync: {src.gamestate.gamestate.tick-char.lastMapSync}\n"
            text += "\n"
            for jobOrder in char.jobOrders:
                text += str(jobOrder.taskName)
                text += ": %s \n" % json.dumps(jobOrder.tasks)#,indent=4)
            text += "\n"
            text += "lastJobOrder: %s\n" % char.lastJobOrder
            text += "skills: %s\n" % char.skills
            if len(char.duties) < 5:
                text += "duties: %s\n" % ",\n".join(char.duties)
            else:
                text += "duties: "
                duties_to_show = char.duties[:]
                counter = 0
                while duties_to_show:
                    text += "%s" % duties_to_show.pop(0)
                    if duties_to_show:
                        if counter > 5:
                            text += ",\n      "
                            counter = 0
                        else:
                            text += ", "
                            counter += 1
                text += "\n" % char.duties
            text += "numAttackedWithoutResponse: %s\n" % char.numAttackedWithoutResponse
            text += f"position: {char.getSpacePosition()}\n"
            text += f"big position: {char.getBigPosition()}\n"
            text += f"terrain position: {char.getTerrainPosition()}\n"
            text += f"grievances: {char.grievances}\n"
            text += f"terrainName: %s\n" % char.getTerrain().tag
            text += f"disableCommandsOnPlus: %s\n" % char.disableCommandsOnPlus
            text += f"autoExpandQuests: %s\n" % char.autoExpandQuests
            text += f"autoExpandQuests2: %s\n" % char.autoExpandQuests2
            text += f"burnedIn: %s\n" % char.burnedIn
            tool_text = "no tool"
            if char.tool:
                tool_text = char.tool.name
            text += f"tool: %s\n" % tool_text

        text += "\n"
        text += "\n"
        text += "press a/d to change what information is shown"
        text += "\n"
        text += "\npress e to view the status effect on the character"
        text += "\npress s to view the character statistics"
        return text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # workaround bug
        if self.skipKeypress:
            self.skipKeypress = False
            key = "~"

        # exit the submenu
        if key in ("esc","v"):
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True
        if key == "e":
            submenue = src.menuFolder.statusEffectMenu.StatusEffectMenu(char=character)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender,character=character)
            return True

        if key == "s":
            submenue = src.menuFolder.characterStatsMenu.CharacterStatsMenu()
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender, character=character)
            return True

        if key == "d":
            self.page += 2
        if key == "a":
            self.page -= 2
        if self.page < 1:
            self.page = 2
        if self.page > 2:
            self.page = 1

        if key in ("t",):
            if not self.char.tool:
                character.addMessage("no tool to remove")
            else:
                tool = self.char.tool
                self.char.tool = None
                self.char.container.addItem(tool,self.char.getPosition())
                character.addMessage("you dropped your tool")
                return True

        char = self.char

        text = self.render(char)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ncharacter overview"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None
