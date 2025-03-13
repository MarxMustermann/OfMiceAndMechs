from functools import partial

import src
import src.items


class MemoryReader(src.items.itemMap["WorkShop"]):
    type = "MemoryReader"
    name = "Memory Reader"
    description = "Use it to read and stitching Memory Fragments"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="MR")

        self.applyOptions.extend([("decrypt Fragments", "decrypt Fragments"), ("stitch Fragments", "stitch Fragments")])

        self.applyMap = {
            "decrypt Fragments": self.decryptFragments,
            "stitch Fragments": self.stitchFragments,
        }

        self.fragments_decrypted = -1

        self.massages = ["example massage 1", "example massage 2", "example massage 3"]

        self.fragment_per_implant = 5

    def read(self, fragment_number, character):
        submenue = src.menuFolder.textMenu.TextMenu(
            "you decrypt new fragment:\n" + self.massages[fragment_number],
        )
        submenue.tag = "massage"
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)

    def getFragments(self, character):
        fragments = []
        for item in character.inventory:
            if item.type == "MemoryFragment":
                fragments.append(item)
        return fragments

    def decryptFragments(self, character):
        if self.fragments_decrypted + 1 == len(self.massages):
            character.addMessage("You can't decrypt more massages")
            return

        fragments = self.getFragments(character)

        if not fragments:
            character.addMessage("You need to have fragments in your inventory to decrypt them")
            return

        character.inventory.remove(fragments[-1])

        self.fragments_decrypted += 1

        numbers = ["first", "second", "third", "forth", "fifth", "sixth", "seventh"]
        option = f"read {numbers[self.fragments_decrypted]} massage"
        self.applyOptions.append(
            (option, option),
        )
        self.applyMap[option] = partial(self.read, self.fragments_decrypted)

        self.read(self.fragments_decrypted, character)

    def stitchFragments(self, character):
        fragments = self.getFragments(character)

        if len(fragments) < self.fragment_per_implant:
            character.addMessage("You need to have 5 fragments in your inventory to stitch them")
            return

        params = {"character": character}
        params["productionTime"] = 50
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]

        fragments = self.getFragments(character)
        for i in range(self.fragment_per_implant):
            character.inventory.remove(fragments[i])

        character.inventory.append(src.items.itemMap["Implant"]())
        character.addMessage("you got a functional implant")

src.items.addType(MemoryReader)
