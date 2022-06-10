import src
import random


class DutyArtwork(src.items.Item):
    """
    ingame item that allows the player to set duties for npcs of that city
    """

    type = "DutyArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="DA")

        self.name = "duty artwork"
                
        self.applyOptions.extend(
                                                [
                                                    ("showRankBased", "show rank based"),
                                                    ("showMatrix", "show matrix based"),
                                                ]
                                )

        self.applyMap = {
                                    "showTree": self.showTree,
                                    "showRankBased": self.showRankBased,
                                    "showMatrix": self.showMatrix,
                                }

        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This artwork allows to manage the duties of clones in this base.
This will change what work the clones are doing when told to be useful."""
        self.usageInfo = """
Use it by activating it and selecting in what mode you want to set the duties.
After changing the duties the clones should change their behaviour after completing their current task."""

    def changeCharges(self,delta):
        self.charges += delta

    def fetchCityleader(self):
        personnelArtwork = None
        for item in self.container.itemsOnFloor:
            if not item.type == "PersonnelArtwork":
                continue
            personnelArtwork = item

        if not personnelArtwork:
            return None

        return personnelArtwork.cityLeader

    def showTree(self, character):
        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        self.submenue = src.interaction.JobByRankMenu(cityLeader)
        character.macroState["submenue"] = self.submenue

    def showRankBased(self, character):
        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        self.submenue = src.interaction.JobByRankMenu(cityLeader)
        character.macroState["submenue"] = self.submenue

    def showMatrix(self, character):
        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        self.submenue = src.interaction.JobAsMatrixMenu(cityLeader)
        character.macroState["submenue"] = self.submenue

src.items.addType(DutyArtwork)
