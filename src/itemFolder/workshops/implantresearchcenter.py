import src


class ImplantResearchCenter(src.items.itemMap["WorkShop"]):
    type = "ImplantResearchCenter"
    name = "Implant Research Center"
    description = "Use it to research the inner working of the implants"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="IR")

        self.applyOptions.extend(
            [
                ("research implant", "research implant"),
            ]
        )
        self.applyMap = {
            "research implant": self.researchImplant,
        }

        self.research_level = 0
        self.research_level_needed = 5  # research level needed to get ImplantManipulator

    def discovered_manipulator(self):
        return self.research_level == self.research_level_needed

    def researchImplant(self, character):
        self.produceItem({"character": character})

    def produceItem(self, params):
        character = params["character"]

        implants = []
        for item in character.inventory:
            if item.type == "Implant":
                implants.append(item)

        if not implants:
            character.addMessage("You need to have implants in your inventory to research them")
            return

        character.inventory.remove(implants[-1])

        params["productionTime"] = 10
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]

        character.addMessage("You researched the implant")
        character.addMessage("It took you 10 turns to do that")

        self.research_level += 1
        character.addMessage(f"Your implant research level now is {self.research_level}")

        if self.discovered_manipulator():
            character.addMessage("you finally found a way to manipulate it")
            character.addMessage("you created an Implant Manipulator")

            character.inventory.append(src.items.itemMap["ImplantManipulator"]())

            character.changed("researched implant manipulator", {})
        else:
            massages = [
                "you found a way to dissemble the outer shell",
                "you know now how to get to the internals of it",
                "you learnt how it works internally",
                "you see a way to manipulate it but it doesn't work yet",
            ]

            if self.research_level - 1 < len(massages):
                character.addMessage(massages[self.research_level - 1])

            character.changed("researched implant", {})


src.items.addType(ImplantResearchCenter, nonManufactured=True)
