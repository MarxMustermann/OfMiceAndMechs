import src

"""
"""


class PathingNode(src.items.Item):
    type = "PathingNode"

    """
    call superclass constructor with modified paramters
    """

    def __init__(self):
        super().__init__(display=";;")
        self.name = "pathing node"

        self.bolted = False
        self.walkable = True
        self.nodeName = ""

        self.attributesToStore.extend(
            [
                "nodeName",
            ]
        )

    """
    collect items
    """

    def apply(self, character):
        character.addMessage("This is the pathingnode: %s" % (self.nodeName,))
        self.bolted = True

    def configure(self, character):
        options = [("setName", "set name")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("enter node name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName

    def setName(self):
        self.nodeName = self.submenue.text

    def getLongInfo(self):
        text = """
item: PathingNode

name:
%s

description:
the basis for semi smart pathing
""" % (
            self.nodeName,
        )


src.items.addType(PathingNode)
