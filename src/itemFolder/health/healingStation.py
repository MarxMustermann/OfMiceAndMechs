import src

class HealingStation(src.items.Item):
    type = "HealingStation"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.healingStation,xPosition,yPosition,creator=creator,name="healingstation")

        self.walkable = False
        self.bolted = True
        self.charges = 0

    def apply(self,character):
        options = [("heal","heal me"),("vial","fill vial")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "heal":
            self.heal(self.character)
        if self.submenue.selection == "vial":
            self.fill(self.character)

    def heal(self,character):

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        character.addMessage("the machine heals you")
        character.health = 100
        self.charges -= 1

    def fill(self,character):

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        for item in character.inventory:
            if not isinstance(item,src.items.Vial):
                continue
            if self.charges > item.maxUses-item.uses:
                self.charges -= item.maxUses-item.uses
                item.uses = item.maxUses
                character.addMessage("you fill your vial with the healing")
                return
            else:
                item.uses += self.charges
                self.charges = 0
                character.addMessage("you drain the healing into your vial")
                return

        character.addMessage("you have no vial in your inventory")

    def getLongInfo(self):
        return """
item: HealingStation

description:
heals you

charges:
%s

"""%(self.charges)

src.items.addType(HealingStation)
