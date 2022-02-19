import src
import random


class JobArtwork(src.items.Item):
    """
    ingame item that allows the player the convert ressources and
    items by trading
    """

    type = "JobArtwork"

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
                                                    ("showMatrix", "configure jobs"),
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

        text = ""
        text += "rank 3: "
        text += str(cityLeader.name)

        character.addMessage(text)
        print(text)

    def showRankBased(self, character):
        cityLeader = self.fetchCityleader()
        if not cityLeader:
            character.addMessage("no city leader")
            return

        text = ""

        dutyCount = {"Trapsetting":0,"Farming":0,"Cleaning":0}
        npcCount = 0
        npcCount += 1
        for duty in cityLeader.duties:
            dutyCount[duty] += 1
        text += "rank 3 (%s): \n"%(npcCount,)
        for (duty,count) in dutyCount.items():
            text += "%s: %s "%(duty,count)
        text += "\n"

        dutyCount = {"Trapsetting":0,"Farming":0,"Cleaning":0}
        npcCount = 0
        for subleader in cityLeader.subordinates:
            npcCount += 1
            for duty in subleader.duties:
                dutyCount[duty] += 1
        text += "rank 4 (%s): \n"%(npcCount,)
        for (duty,count) in dutyCount.items():
            text += "%s: %s "%(duty,count)
        text += "\n"

        dutyCount = {"Trapsetting":0,"Farming":0,"Cleaning":0}
        npcCount = 0
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                npcCount += 1
                for duty in subsubleader.duties:
                    dutyCount[duty] += 1
        text += "rank 5 (%s): \n"%(npcCount,)
        for (duty,count) in dutyCount.items():
            text += "%s: %s "%(duty,count)
        text += "\n"

        dutyCount = {"Trapsetting":0,"Farming":0,"Cleaning":0}
        npcCount = 0
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                for worker in subsubleader.subordinates:
                    npcCount += 1
                    for duty in worker.duties:
                        dutyCount[duty] += 1
        text += "rank 6 (%s): \n"%(npcCount,)
        for (duty,count) in dutyCount.items():
            text += "%s: %s "%(duty,count)
        text += "\n"


        self.submenue = src.interaction.JobByRankMenu(cityLeader)
        character.macroState["submenue"] = self.submenue

        print(text)
        character.addMessage(text)

    def showMatrix(self, character):
        character.addMessage("show matrix")

src.items.addType(JobArtwork)
