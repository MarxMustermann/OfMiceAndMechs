import src
import random
import copy
import json

class PersonnelArtwork(src.items.Item):
    """
    a ingame item to build and extend cities
    is a representation of a city and holds the coresponding information
    takes tasks and delegates tasks to other manager
    """


    type = "PersonnelArtwork"

    def __init__(self, name="PersonnelArtwork", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="PA", name=name)

        self.applyOptions.extend(
                        [
                                                                ("viewNPCs", "view npcs"),
                        ]
                        )
        self.applyMap = {
                    "viewNPCs": self.viewNPCs,
                    "spawnRank6": self.spawnRank6,
                    "spawnRank5": self.spawnRank5,
                    "spawnRank4": self.spawnRank4,
                    "spawnRank3": self.spawnRank3,
                    "spawnMilitary": self.spawnMilitary,
                    "spawnSet": self.spawnSet,
                    "spawnRankUnranked": self.spawnRankUnranked,
                        }
        self.cityLeader = None
        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This item allows to manage the clones in this base."""
        self.usageInfo = """
Activate the item to use it.
Use the item so see an overview over the NPCs in this base."""

    def viewNPCs(self,character):
        submenue = src.interaction.ViewNPCsMenu(self)
        character.macroState["submenue"] = submenue

    def getPersonnelList(self):

        personel = []

        cityLeader = self.fetchCityleader()

        if not cityLeader:
            return []

        personel.append(cityLeader)

        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue

            personel.append(subleader)

            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue

                personel.append(subsubleader)

                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    personel.append(worker)
        return personel
        
    def fetchCityleader(self):
        return self.cityLeader

    def spawnSet(self,character):
        cityleader = self.spawnRank(3,character)
        for i in range(0,3):
            self.spawnRank(4,character)
        for i in range(0,9):
            self.spawnRank(5,character)
        for i in range(0,9*3):
            self.spawnRank(6,character)
        return cityleader

    def spawnRank6(self,character):
        return self.spawnRank(6,character)
    def spawnRank5(self,character):
        return self.spawnRank(5,character)
    def spawnRank4(self,character):
        return self.spawnRank(4,character)
    def spawnRank3(self,character):
        return self.spawnRank(3,character)
    def spawnRankUnranked(self,character):
        return self.spawnRank(None,character)
    def spawnMilitary(self,character):
        return self.spawnRank(None,character,isMilitary=True)

    def spawnRank(self,rank,actor,isMilitary=False):
        cityLeader = self.fetchCityleader()

        if rank == 3:
            if cityLeader and not cityLeader.dead:
                actor.addMessage("only one rank 3 possible")
                return

        if rank == 4:
            if not cityLeader or self.cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    cityLeader.subordinates.remove(subleader)

            if len(cityLeader.subordinates) > 2:
                actor.addMessage("no rank 3 to hook into")
                return

        if rank == 5:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            foundSubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue
                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        subleader.subordinates.remove(subsubleader)
                if len(subleader.subordinates) > 2:
                    continue
                foundSubleader = subleader

            if not foundSubleader:
                actor.addMessage("no rank 4 to hook into")
                return

        if rank == 6:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            foundSubsubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue

                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        continue
                    if len(subsubleader.subordinates) > 2:
                        continue
                    foundSubsubleader = subsubleader

            if not foundSubsubleader:
                actor.addMessage("no rank 5 to hook into")
                return

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.personality["abortMacrosOnAttack"] = False

        if rank == 3:
            if not cityLeader or cityLeader.dead:
                self.cityLeader = char

        if rank == 4:
            cityLeader.subordinates.append(char)
            char.duties.extend(["scratch checking","clearing","painting"])

        if rank == 5:
            foundSubleader.subordinates.append(char)
            char.duties.extend(["resource fetching","trap setting","hauling"])

        if rank == 6:
            foundSubsubleader.subordinates.append(char)
            char.duties.extend(["resource gathering"])

        quest = src.quests.BeUsefull()
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)
        char.faction = actor.faction
        char.isMilitary = False
        if rank:
            char.rank = rank
        self.container.addCharacter(char,5,6)
        char.runCommandString("********")
        char.godMode = True

        return char

src.items.addType(PersonnelArtwork)
