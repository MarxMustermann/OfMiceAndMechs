import src

# bad code: should be abstracted
# bad code: uses global function to render
class CombatInfoMenu(src.SubMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "CombatInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()

    def render(self,char):
        if char.dead:
            return ""

        text = ""

        text += "you: \n\n"
        text += "name:        %s\n" % char.name
        text += "health:      %s\n" % char.health
        text += "exhaustion:  %s\n" % char.exhaustion
        text += "timeTaken:   %f\n" % char.timeTaken

        text += """

nearby enemies:

"""

        enemies = char.getNearbyEnemies()
        for enemy in enemies:
            text += "-------------  \n"
            text += "name:        %s\n" % enemy.name
            text += "health:     %s\n" % enemy.health
            text += "exhaustion:  %s\n" % enemy.exhaustion
            timeTaken = enemy.timeTaken
            if timeTaken > 1:
                timeTaken -= 1
            text += f"timeTaken:   {timeTaken:f}\n"

        text += """

subordinates:

"""
        for ally in char.subordinates:
            text += "-------------  \n"
            text += "name:        %s\n" % ally.name
            text += "health:     %s\n" % ally.health
            text += "exhaustion:  %s\n" % ally.exhaustion
            timeTaken = ally.timeTaken
            if timeTaken > 1:
                timeTaken -= 1
            text += f"timeTaken:   {timeTaken:f}\n"

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
