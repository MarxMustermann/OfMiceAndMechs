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

        super().__init__(display="JA")

        self.name = "job artwork"
                
        self.applyOptions.extend(
                                                [
                                                    ("showTree", "show tree"),
                                                    ("showRankBased", "show rank based"),
                                                    ("showMatrix", "show matrix based"),
                                                    ("showDetailed", "show character based"),
                                                ]
                                )

        self.applyMap = {
                                    "showTree": self.showTree,
                                    "showRankBased": self.showRankBased,
                                    "showMatrix": self.showMatrix,
                                }

    def fetchCityleader(self):
        cityBuilder = None
        for item in self.container.itemsOnFloor:
            if not item.type == "CityBuilder2":
                continue
            cityBuilder = item

        if not cityBuilder:
            return None

        return cityBuilder.cityLeader

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
