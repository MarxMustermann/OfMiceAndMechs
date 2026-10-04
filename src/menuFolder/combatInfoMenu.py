import src

# bad code: should be abstracted
# bad code: uses global function to render
class CombatInfoMenu(src.menues.SubMenu):
    """
    menu to show the players attributes
    """

    type = "CombatInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()
        self.sidebared = False
        self.skipKeypress = True

    def getTitle(self):
        return "COMBAT INFORMATION"

    def render(self,size=None):
        char = self.char

        if char.dead:
            return ""

        text = []

        if not self.sidebared:
            name = char.charType
            if isinstance(char,src.characters.characterMap["Clone"]):
                name = char.name

            text.append("you: \n\n")
            text.append(f"name:        {name} {char.getSpacePosition()}\n")
            text.append(f"health:      {char.health}/{char.adjustedMaxHealth}\n")
            if char.level:
                text.append(f"level:       {char.level}\n")
            text.append(f"exhaustion:  {char.exhaustion}\n")
            text.append(f"timeTaken:   {round(char.timeTaken,2)}\n")
            text.append(f"movemmentsp: {char.adjustedMovementSpeed}\n")
            text.append(f"attacksp:    {char.attackSpeed}\n")
            text.append("\n")

        enemies = char.getNearbyEnemies()
        if not self.sidebared or enemies:
            text.append("""nearby enemies:
""")
        for enemy in enemies:
            name = enemy.charType
            if isinstance(enemy,src.characters.characterMap["Clone"]):
                name = enemy.name

            if not self.sidebared:
                text.append("-------------  \n")
                text.append(f"name:        {name} {enemy.getSpacePosition()}\n")
                text.append(f"health:      {enemy.health}/{enemy.adjustedMaxHealth}\n")
                if enemy.level:
                    text.append(f"level:       {enemy.level}\n")
                text.append(f"exhaustion:  {enemy.exhaustion}\n")
                text.append(f"timeTaken:   {round(enemy.timeTaken,2)}\n")
                text.append(f"movemmentsp: {enemy.adjustedMovementSpeed}\n")
                text.append(f"attacksp:    {enemy.attackSpeed}\n")
            else:
                text.append(f"{name} {enemy.getSpacePosition()} hp:{enemy.health}/{enemy.adjustedMaxHealth} ex:{enemy.exhaustion} tt:{round(enemy.timeTaken,2)} ms:{enemy.adjustedMovementSpeed} as:{enemy.attackSpeed}\n")

        if not self.sidebared or char.subordinates:
            text.append("""
subordinates:
""")
        for ally in char.subordinates:
            name = ally.charType
            if isinstance(ally,src.characters.characterMap["Clone"]):
                name = ally.name

            if not self.sidebared:
                text.append("-------------  \n")
                text.append(f"name:        {name} {ally.getSpacePosition()}\n")
                text.append(f"health:      {ally.health}/{ally.adjustedMaxHealth}\n")
                if ally.level:
                    text.append(f"level:       {ally.level}\n")
                text.append(f"exhaustion:  {ally.exhaustion}\n")
                text.append(f"timeTaken:   {round(ally.timeTaken,2)}\n")
                text.append(f"movemmentsp: {ally.adjustedMovementSpeed}\n")
                text.append(f"attacksp:    {ally.attackSpeed}\n")
            else:
                text.append(f"{name} {ally.getSpacePosition()} hp:{ally.health}/{ally.adjustedMaxHealth} ex:{ally.exhaustion} tt:{round(ally.timeTaken,2)} ms:{ally.adjustedMovementSpeed} as:{ally.attackSpeed}\n")

        text.append("\n")

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

# register the menu type
src.menues.add_menu(CombatInfoMenu)
