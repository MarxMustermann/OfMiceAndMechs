import src


class DutyArtwork(src.items.Item):
    """
    ingame item that allows the player to set duties for npcs of that city
    """

    type = "DutyArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=(src.interaction.urwid.AttrSpec("#ff0","#000"),"DA"))

        self.name = "duty artwork"

        self.applyOptions.extend(
                                                [
                                                    ("showMatrix", "show matrix based"),
                                                ]
                                )

        self.applyMap = {
                                    "showMatrix": self.showMatrix,
                                }

        self.description = """allows to manage the duties of clones in this base"""
        self.usageInfo = """
Use it by activating it and selecting in what mode you want to set the duties.
After changing the duties the clones should change their behaviour after completing their current task."""

    def changeCharges(self,delta):
        self.charges += delta

    def showMatrix(self, character):

        #if not character.rank < 4:
        #    character.addMessage("you need to have rank 3 to do this. You can see the overview though.")
        #    return
        self.submenue = src.menuFolder.jobAsMatrixMenu.JobAsMatrixMenu(self)
        character.macroState["submenue"] = self.submenue

src.items.addType(DutyArtwork)
