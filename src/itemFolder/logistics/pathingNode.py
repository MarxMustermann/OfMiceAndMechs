import src

class PathingNode(src.items.Item):
    """
    ingame item used to mark waypoints
    used for pathfinding
    intended to be used by the player to mark waypoints
    """

    type = "PathingNode"

    def __init__(self):
        """
        initialise own state
        """

        super().__init__(display=";;")
        self.name = "pathing node"
        self.description = "marks a waypoint"

        self.bolted = False
        self.walkable = True
        self.nodeName = ""

    def apply(self, character):
        """
        handle a character trying to use this item
        by showing some info

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage(f"This is the pathingnode: {self.nodeName}")
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
        self.submenue = src.interaction.SelectionMenu(
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
            self.submenue = src.interaction.InputMenu("enter node name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName

    # bad code: submenu shouldn't be attribute
    def setName(self):
        """
        set the name of the item
        """

        self.nodeName = self.submenue.text

    def getLongInfo(self):
        text = super().getLongInfo()

        text += f"""
name:
{self.nodeName}

"""


src.items.addType(PathingNode)
