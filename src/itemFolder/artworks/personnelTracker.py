import src


class PersonnelTracker(src.items.Item):
    """
    """


    type = "PersonnelTracker"
    description = "Managment item to track the workers on the base"

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
        submenue = src.menues.menuMap["ViewNPCsMenu"](self)
        character.macroState["submenue"] = submenue
        self.faction = character.faction

src.items.addType(PersonnelTracker)
