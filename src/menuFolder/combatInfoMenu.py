import src

# bad code: should be abstracted
# bad code: uses global function to render
class CombatInfoMenu(src.subMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "CombatInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()
        self.sidebared = False
        self.skipKeypress = True

    def render(self):
        char = self.char

        if char.dead:
            return ""

        text = ""

        try:
            char.level
        except:
            char.level = None

        if not self.sidebared:
            text += "you: \n\n"
            text += f"name:        {char.name} {char.getSpacePosition()}\n"
            text += f"health:      {char.health}/{char.adjustedMaxHealth}\n"
            if char.level:
                text += f"level:       {char.level}\n"
            text += f"exhaustion:  {char.exhaustion}\n"
            text += f"timeTaken:   {round(char.timeTaken,2)}\n"
            text += f"movemmentsp: {char.adjustedMovementSpeed}\n"
            text += f"attacksp:    {char.attackSpeed}\n"
            text += "\n"

        text += """nearby enemies:
"""

        enemies = char.getNearbyEnemies()
        for enemy in enemies:
            text += "-------------  \n"
            text += f"name:        {enemy.name} {enemy.getSpacePosition()}\n"
            text += f"health:      {enemy.health}/{enemy.adjustedMaxHealth}\n"
            try:
                enamy.level
            except:
                enemy.level = None
            if enemy.level:
                text += f"level:       {enemy.level}\n"
            text += f"exhaustion:  {enemy.exhaustion}\n"
            text += f"timeTaken:   {round(enemy.timeTaken,2)}\n"
            text += f"movemmentsp: {enemy.adjustedMovementSpeed}\n"
            text += f"attacksp:    {enemy.attackSpeed}\n"

        text += """
subordinates:
"""
        for ally in char.subordinates:
            text += "-------------  \n"
            text += f"name:        {ally.name} {ally.getSpacePosition()}\n"
            text += f"health:      {ally.health}/{ally.adjustedMaxHealth}\n"
            try:
                ally.level
            except:
                ally.level = None
            if ally.level:
                text += f"level:       {ally.level}\n"
            text += f"exhaustion:  {ally.exhaustion}\n"
            text += f"timeTaken:   {round(ally.timeTaken,2)}\n"
            text += f"movemmentsp: {enemy.adjustedMovementSpeed}\n"
            text += f"attacksp:    {enemy.attackSpeed}\n"

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

        if self.skipKeypress:
            self.skipKeypress = False
            key = "~"

        # exit the submenu
        if key in ("esc","o",):
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            self.sidebared = True
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            self.sidebared = True
            return True

        text = self.render()

        # show info
        if src.interaction.main:
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        if src.interaction.header:
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None
