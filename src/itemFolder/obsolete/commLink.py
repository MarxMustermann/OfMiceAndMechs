import src

"""
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
"""


class Commlink(src.items.Item):
    type = "CommLink"
    attributesToStore = []

    """
    call superclass constructor with modified paramters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.commLink)

        self.name = "commlink"

        self.scrapToDeliver = 100
        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(["scrapToDeliver"])

    """
    get tributes and trades
    """

    def apply(self, character):
        super().apply(character)

        if self.scrapToDeliver > 0:
            toRemove = []
            for item in character.inventory:
                if isinstance(item, itemMap["Scrap"]):
                    toRemove.append(item)
                    self.scrapToDeliver -= 1

            character.addMessage("you need to delivered %s scraps" % (len(toRemove)))
            for item in toRemove:
                character.inventory.remove(item)

        if self.scrapToDeliver > 0:
            character.addMessage(
                "you need to deliver %s more scraps to have payed tribute"
                % (self.scrapToDeliver)
            )
            return

        character.addMessage("you have payed tribute yay")

    def getLongInfo(self):
        text = """
item: CommLink

description:
A comlink. 

"""


src.items.addType(Commlink)
