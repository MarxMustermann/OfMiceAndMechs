import src

class BluePrintingArtwork(src.items.Item):
    type = "BluePrintingArtwork"

    def __init__(self):
        super().__init__(display="BA")

        self.name = "blueprinting artwork"

    def apply(self,character):
        self.character = character
        self.submenue = src.interaction.InputMenu("input menue")
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createBlueprint
        return

    def createBlueprint(self):
        if not self.submenue.text in itemMap:
            self.character.addMessage("item not found")
            return
        new = BluePrint()
        new.setToProduce(self.submenue.text)
        new.xPosition = self.xPosition+1
        new.yPosition = self.yPosition
        new.bolted = False

        self.room.addItems([new])

src.items.addType(BluePrintingArtwork)
