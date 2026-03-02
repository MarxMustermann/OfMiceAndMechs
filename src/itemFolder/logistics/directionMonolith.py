import src


class DirectionMonolith(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "DirectionMonolith"
    def __init__(self):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ca0","#000"),"MO"))
        self.name = "direction monolith"
        self.description = "points into a direction"

        self.direction_name = None
        self.direction = None
        self.bolted = True
        self.walkable = False
        self.nodeName = ""

    def apply(self, character):
        """
        handle a character trying to use this item
        by showing some info

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage(f"{self.nodeName}")
        self.bolted = True

    # abstraction: should use super class functionality
    def configure(self, character):
        """
        handle a character trying to conigure this item
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the machine
        """

        options = [("setName", "set name")]
        self.submenue = src.menuFolder.selectionMenu.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        """
        handle a character having selected an action to do
        by running the action
        """

        if self.submenue.selection == "setName":
            self.submenue = src.menuFolder.inputMenu.InputMenu("enter node name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName

    # bad code: submenu shouldn't be attribute
    def setName(self):
        """
        set the name of the item
        """

        self.nodeName = self.submenue.text

    def getLongInfo(self, character=None):
        text = super().getLongInfo(character)

        text += f"""
name:
{self.nodeName}

"""


src.items.addType(DirectionMonolith)
