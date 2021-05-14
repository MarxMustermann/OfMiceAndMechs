import src


class BluePrintingArtwork(src.items.Item):
    type = "BluePrintingArtwork"

    def __init__(self):
        super().__init__(display="BA")

        self.name = "blueprinting artwork"

    def apply(self, character):
        self.character = character
        self.submenue = src.interaction.InputMenu("input menue")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createBlueprint
        return

    def createBlueprint(self):
        if self.submenue.text not in itemMap:
            self.character.addMessage("item not found")
            return
        new = BluePrint()
        new.setToProduce(self.submenue.text)
        new.bolted = False

        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))


src.items.addType(BluePrintingArtwork)
