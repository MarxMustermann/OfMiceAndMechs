import src


class PersonnelTracker(src.items.Item):
    """
    """


    type = "PersonnelTracker"

    def __init__(self, name="PersonnelTracker", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="PT", name=name)

        self.applyOptions.extend(
                        [
                                                                ("viewNPCs", "view npcs"),
                        ]
                        )
        self.applyMap = {
                    "viewNPCs": self.viewNPCs,
                        }

        self.faction = ""

    def viewNPCs(self,character):
        submenue = src.menuFolder.viewNPCsMenu.ViewNPCsMenu(self)
        character.macroState["submenue"] = submenue
        self.faction = character.faction

    def apply(self,character):
        #if not character.rank or character.rank > 5:
        #    character.addMessage("you need to have be at least rank 5 to use this machine")
        #    return
        super().apply(character)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

src.items.addType(PersonnelTracker)
