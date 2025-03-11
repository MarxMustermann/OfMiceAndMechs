from functools import partial

import src


class MemoryReader(src.items.itemMap["WorkShop"]):
    type = "MemoryReader"
    name = "Memory Reader"
    description = "Use it to read Memory Fragments"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="MR")

        self.applyOptions.append(
            ("decrypt Fragments", "decrypt Fragments"),
        )

        self.applyMap = {
            "decrypt Fragments": self.decryptFragments,
        }

        self.fragments_decrypted = -1

        self.massages = ["example massage 1", "example massage 2", "example massage 3"]

    def read(self, fragment_number, character):
        submenue = src.menuFolder.textMenu.TextMenu(
            "you decrypt new fragment:\n" + self.massages[fragment_number],
        )
        submenue.tag = "massage"
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)

    def decryptFragments(self, character):
        self.produceItem({"character": character})

    def produceItem(self, params):
        character = params["character"]

        if self.fragments_decrypted + 1 == len(self.massages):
            character.addMessage("You can't decrypt more massages")
            return

        fragments = []
        for item in character.inventory:
            if item.type == "MemoryFragment":
                fragments.append(item)

        if not fragments:
            character.addMessage("You need to have fragments in your inventory to decrypt them")
            return

        character.inventory.remove(fragments[-1])

        #     in case decrypting needing time to decrypt
        #     params["productionTime"] = 10
        #     params["doneProductionTime"] = 0
        #     params["hitCounter"] = character.numAttackedWithoutResponse
        #     self.produceItem_wait(params)

        # def produceItem_done(self, params):
        #     character = params["character"]

        self.fragments_decrypted += 1

        numbers = ["first", "second", "third", "forth", "fifth", "sixth", "seventh"]
        option = f"read {numbers[self.fragments_decrypted]} massage"
        self.applyOptions.append(
            (option, option),
        )
        self.applyMap[option] = partial(self.read, self.fragments_decrypted)

        self.read(self.fragments_decrypted, character)


src.items.addType(MemoryReader)
