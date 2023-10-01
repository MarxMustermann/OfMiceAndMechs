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
                                                    ("showOverview", "show overview"),
                                                    ("showMatrix", "show matrix based"),
                                                ]
                                )

        self.applyMap = {
                                    "showMatrix": self.showMatrix,
                                    "showOverview": self.showOverview,
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
            if item.type != "PersonnelArtwork":
                continue
            personnelArtwork = item

        if not personnelArtwork:
            return None

        return personnelArtwork.cityLeader

    def showOverview(self, character):
        text = ""

        terrain = character.getTerrain()

        characters = []
        characters.extend(terrain.characters)
        for room in terrain.rooms:
            characters.extend(room.characters)

        for testChar in characters[:]:
            if testChar.faction != character.faction or len(testChar.duties) > 1:
                characters.remove(testChar)

        dutyMap = {}
        for char in characters:
            for duty in char.duties:
                if not duty in dutyMap:
                    dutyMap[duty] = 0
                dutyMap[duty] += 1

        for (k,v) in dutyMap.items():
            text += f"{k} - {v}\n"

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

    def showMatrix(self, character):
        if not character.rank < 4:
            character.addMessage("you need to have rank 3 to do this. You can see the overview though.")
            return
        self.submenue = src.interaction.JobAsMatrixMenu(self)
        character.macroState["submenue"] = self.submenue

src.items.addType(DutyArtwork)
