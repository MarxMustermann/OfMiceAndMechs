import json

from src.menuFolder.SubMenu import SubMenu

import src

# bad code: should be abstracted
# bad code: uses global function to render
class CharacterInfoMenu(SubMenu):
    """
    menu to show the players attributes
    """

    type = "CharacterInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()

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

        text += "name:       %s\n" % char.name
        text += "\n"
        text += "\n"
        text += "health:     %s" % char.health + "\n"
        text += "max health: %s" % char.adjustedMaxHealth + "\n"
        text += "exhaustion: %s" % char.exhaustion + "\n"
        text += "\n"
        text += "baseDamage: %s\n" % char.baseDamage
        text += "weapon:     %s\n" % weaponBaseDamage
        text += "armor:      %s\n" % armorValue
        text += "faction:    %s\n" % char.faction
        text += "time taken: %s" % char.timeTaken + "\n"

        if hasattr(char,"rank"):
            text += "rank:       %s\n" % char.rank
        if hasattr(char,"superior"):
            text += "superior:   %s\n" % char.superior
        text += "reputation: %s\n" % char.reputation
        flaskInfo = "-"
        if char.flask:
            flaskInfo = str(char.flask.uses)+" flask charges"
        text += f"satiation:  {char.satiation} ({flaskInfo})\n"

        text += "\n"
        text += f"movementSpeed:  {char.movementSpeed}\n"
        text += f"attackSpeed:    {char.attackSpeed}\n"
        text += "\n"
        for jobOrder in char.jobOrders:
            text += str(jobOrder.taskName)
            text += ": %s \n" % json.dumps(jobOrder.tasks)#,indent=4)
        text += "\n"
        text += "lastJobOrder: %s\n" % char.lastJobOrder
        text += "skills: %s\n" % char.skills
        if len(char.duties) > 5:
            text += "duties: %s\n" % ",\n".join(char.duties)
        else:
            text += "duties: %s\n" % char.duties
        text += "numAttackedWithoutResponse: %s\n" % char.numAttackedWithoutResponse
        text += f"position: {char.getSpacePosition()}\n"
        text += f"big position: {char.getBigPosition()}\n"
        text += f"terrain position: {char.getTerrainPosition()}\n"
        text += f"grievances: {char.grievances}\n"
        text += f"registers: {char.registers}\n"
        text += f"terrainName: %s\n" % char.getTerrain().tag
        text += f"disableCommandsOnPlus: %s\n" % char.disableCommandsOnPlus
        text += f"autoExpandQuests: %s\n" % char.autoExpandQuests
        text += f"autoExpandQuests2: %s\n" % char.autoExpandQuests2
        text += f"burnedIn: %s\n" % char.burnedIn
        text += f"tool: %s\n" % char.tool

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

        # exit the submenu
        if key == "esc":
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        char = self.char

        text = self.render(char)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ncharacter overview"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None
