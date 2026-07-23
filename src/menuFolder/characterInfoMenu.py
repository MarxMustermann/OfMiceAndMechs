import json

import src

# bad code: should be abstracted
# bad code: uses global function to render
class CharacterInfoMenu(src.menues.SubMenu):
    """
    menu to show the players attributes
    """

    type = "CharacterInfoMenu"

    def __init__(self, char=None):
        self.char = char
        self.skipKeypress = True
        super().__init__()
        self.page = 1

        self.min_lines = 8
        self.min_cols = 50

    def getTitle(self):
        return "CHARACTER INFORMATION"

    def _get_text_dimensions(self,text):
        lines = text.split("\n")
        max_line = 0
        for line in lines:
            max_line = max(max_line,len(line))
        return (len(lines),max_line)

    def render(self):

        char = self.char

        if char.dead:
            return ""

        text = []

        text.append(f"name:      {char.name}\n")
        text.append(f"faction:   {char.faction}\n")
        if hasattr(char,"rank"):
            text.append(f"rank:      {char.rank}\n")
        text.append("\n")
        text.append([f"page: ",src.interaction.ActionMeta(payload="a",content="<"),f" {self.page}/3 ",src.interaction.ActionMeta(payload="d",content=">"),"\n"])
        text.append("\n")
        if self.page == 1:
            text.append(f"health:       {char.health}\n")
            text.append(f"max health:   {char.adjustedMaxHealth}\n")
            text.append(f"exhaustion:   {char.exhaustion}\n")
            text.append(f"time taken:   {char.timeTaken}\n")
            text.append("\n")
            text.append("weapon:       ")
            weaponBaseDamage = None
            if char.weapon:
                text.append(char.weapon.name)
                text.append(f" ({char.weapon.baseDamage})")
            else:
                text.append("no weapon")
            text.append("\n")
            text.append("armor:        ")
            armorValue = None
            if char.armor:
                text.append(char.armor.name)
                text.append(f" ({char.armor.armorValue})")
            else:
                text.append("no armor")
            text.append("\n")
            tool_text = "no tool"
            if char.tool:
                tool_text = char.tool.name
                text.append(f"tool:         {tool_text}\n")
            text.append("\n")
            text.append(f"baseDamage:     {char.baseDamage}\n")
            text.append(f"movementSpeed:  {char.adjustedMovementSpeed}\n")
            text.append(f"attackSpeed:    {char.attackSpeed}\n")
            text.append("\n")
            text.append(f"position:          {char.getSpacePosition()}\n")
            text.append(f"big position:      {char.getBigPosition()}\n")
            text.append(f"terrain position:  {char.getTerrainPosition()}\n")
            text.append("\n")

            statusEffectString = ""
            for statusEffect in char.statusEffects:
                statusEffectString += statusEffect.type + " (" + statusEffect.getShortCode() + "), "
            if not statusEffectString == "":
                statusEffectString = statusEffectString[:-2]
            statusEffectString = "[]"
            text.append(f"status effects: {statusEffectString}\npress e to view a detailed buff list\n")
            
        if self.page == 2:
            if len(char.duties) < 5:
                dutyString = ",\n        ".join(char.duties)
                text.append(f"duties: {dutyString}\n")
            else:
                text.append("duties: ")
                duties_to_show = char.duties[:]
                counter = 0
                while duties_to_show:
                    duty_to_show = duties_to_show.pop(0)
                    text += f"{duty_to_show}"
                    if duties_to_show:
                        if counter > 5:
                            text += ",\n      "
                            counter = 0
                        else:
                            text += ", "
                            counter += 1
                text.append("\n")
            text.append("\n")
            text.append(f"skills:      {char.skills}\n")
            text.append(f"grievances:  {char.grievances}\n")
        
        if self.page == 3:
            if hasattr(char,"superior"):
                text.append(f"superior:   {char.superior}\n")
            text.append(f"reputation: {char.reputation}\n")
            flaskInfo = "-"
            if char.flask:
                flaskInfo = str(char.flask.uses)+" flask charges"
            text.append(f"satiation:  {char.satiation} ({flaskInfo})\n")
            text.append("\n")
            text.append(f"hasSpecialAttacks:      {char.hasSpecialAttacks}\n")
            text.append(f"hasSwapAttack:          {char.hasSwapAttack}\n")
            text.append(f"hasRun:                 {char.hasRun}\n")
            text.append(f"hasJump:                {char.hasJump}\n")
            text.append(f"hasLineShot:            {char.hasLineShot}\n")
            text.append(f"hasRandomShot:          {char.hasRandomShot}\n")
            text.append(f"hasMovementSpeedBoost:  {char.hasMovementSpeedBoost}\n")
            text.append(f"hasMaxHealthBoost:      {char.hasMaxHealthBoost}\n")
            text.append(f"hasMagic:               {char.hasMagic}\n")
            text.append("\n")
            if char.lastMapSync:
                text.append(f"lastMapSync: {src.gamestate.gamestate.tick-char.lastMapSync}\n")
                text.append("\n")
            for jobOrder in char.jobOrders:
                text.append(str(jobOrder.taskName))
                text.append(": %s \n" % json.dumps(jobOrder.tasks))
            text.append(f"combat value:                {char.getStrengthSelfEstimate()}\n")
            text.append(f"numAttackedWithoutResponse:  {char.numAttackedWithoutResponse}\n")
            text.append(f"terrainName:                 {char.getTerrain().tag}\n")
            text.append(f"disableCommandsOnPlus:       {char.disableCommandsOnPlus}\n")
            text.append(f"autoExpandQuests:            {char.autoExpandQuests}\n")
            text.append(f"autoExpandQuests2:           {char.autoExpandQuests2}\n")
            text.append(f"burnedIn:                    {char.burnedIn}\n")

        text.append("\n")

        dimensions = self._get_text_dimensions(src.interaction.stringifyUrwid(text))
        if dimensions[0]+5 <= self.min_lines:
            text.append("\n"*(self.min_lines-(dimensions[0]+5)))
        else:
            self.min_lines = dimensions[0]+5

        text.append("\n")
        text.append(src.interaction.ActionMeta(payload="a",content="press a"))
        text.append("/")
        text.append(src.interaction.ActionMeta(payload="d",content="d to change what information is shown"))
        text.append("\n")
        text.append("\n")
        text.append(src.interaction.ActionMeta(payload="e",content="press e to view the status effect on the character"))
        text.append("\n")
        text.append(src.interaction.ActionMeta(payload="s",content="press s to view the character statistics"))
        text.append("\n")

        if dimensions[1] <= self.min_cols:
            text.append(" "*(self.min_cols-dimensions[1]))
        else:
            self.min_cols = dimensions[1]

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

        character.changed("opened character menu",{})
        src.gamestate.gamestate.stern["opened character menu"] = True

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
            submenue = src.menuFolder.characterStatsMenu.CharacterStatsMenu(character)
            character.macroState["submenue"] = submenue
            submenue.handleKey("~", noRender=noRender, character=character)
            return True

        if key == "d":
            self.page += 1
        if key == "a":
            self.page -= 1
        if self.page < 1:
            self.page = 3
        if self.page > 3:
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

        text = self.render()

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ncharacter overview"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None

# register the menu type
src.menues.add_menu(CharacterInfoMenu)
