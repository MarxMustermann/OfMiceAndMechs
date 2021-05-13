import src

class WaterPump(src.items.Item):
    type = "WaterPump"

    def __init__(self):
        super().__init__(display="WP")

        self.name = "water pump"

        self.walkable = False
        self.bolted = True
        self.rods = 0


    def apply(self,character):
        options = [("drink","drink"),("rod","add rod")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if not self.terrain:
            self.character.addMessage("the water condenser needs to be placed outside to work")
            return

        self.bolted = True

        if self.submenue.selection == "drink":
            if self.terrain.heatmap[self.xPosition//15][self.yPosition//15] > 4:
                self.character.addMessage("there is no water left")
                return

            amount = 100+self.rods*10
            self.character.addMessage("you drink from the water condenser. You gain %s satiation, but are poisoned"%(amount,))
            self.character.satiation += amount
            if self.character.satiation > 1000:
                self.character.satiation = 1000
            self.character.hurt(amount//100,reason="poisoned")

            self.terrain.heatmap[self.xPosition//15][self.yPosition//15] += 1

        if self.submenue.selection == "rod":
            for item in self.character.inventory:
                if isinstance(item,src.items.Rod):

                    self.character.addMessage("you insert a rod into the water condenser increasing its output")
                    self.rods += 1
                    self.character.inventory.remove(item)
                    return
            self.character.addMessage("you have no rods in your inventory")

    def getLongInfo(self):
        return """
item: Water condenser

description:
you can drink condensed water from it

"""

src.items.addType(WaterPump)
