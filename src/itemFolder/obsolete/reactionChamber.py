import src


class ReactionChamber(src.items.Item):
    type = "ReactionChamber"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.reactionChamber)

        self.name = "reaction chamber"
        self.contains = ""

    def apply(self, character):

        options = []
        options.append(("add", "add"))
        options.append(("boil", "boil"))
        options.append(("mix", "mix"))
        self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
            "select the item to produce", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

    def doAction(self):
        selection = self.submenue.selection
        if selection == "add":
            # self.add()
            pass
        if selection == "mix":
            self.mix()
        if selection == "boil":
            self.boil()

    def add(self, chemical):
        if len(self.contains) >= 10:
            self.character.addMessage("the reaction chamber is full")
            return

        self.character.addMessage(
            "you add a " + chemical.type + " to the reaction chamber"
        )

    def mix(self, granularity=9):
        if len(self.contains) < 10:
            self.character.addMessage("the reaction chamber is not full")
            return

        self.character.addMessage(
            "the reaction chambers contents are mixed with granularity %s"
            % (granularity)
        )

    def boil(self):

        self.character.addMessage("the reaction chambers contents are boiled")
        self.contents = self.contents[19] + self.contents[0:19]

    def getLongInfo(self):

        text = (
            """

A raction chamber. It is used to mix chemicals together.

contains:

"""
            + self.contains
        )

        return text


src.items.addType(ReactionChamber)
