import src


class BluePrintingArtwork(src.items.Item):
    """
    ingame item that produces blueprints needed to produce stuff
    this is a godmode item and should not be included in normal gameplay
    """
    type = "BluePrintingArtwork"

    def __init__(self):
        '''
        superclass configuration
        '''

        super().__init__(display="BA")

        self.name = "blueprinting artwork"

        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This artwork allows to generate a Blueprint for anything."""
        self.usageInfo = """
Use it by activating it and typing the exact name of the item you want the blueprint for
The new blueprint should be spawned into your inventory."""


    def apply(self, character):
        '''
        start creating a blueprint
        this at first only spawns a submenu to get parameters and then triggers createBlueprint to do something

        Parameters:
            character: the character trying to produce a blueprint
        '''

        self.character = character
        self.submenu = src.menuFolder.InputMenu.InputMenu("input menue")
        self.character.macroState["submenue"] = self.submenu
        self.character.macroState["submenue"].followUp = self.createBlueprint

    # bad code: is mixed with submenu internals
    def createBlueprint(self):
        '''
        create a blueprint
        '''

        if self.submenu.text not in itemMap:
            self.character.addMessage("item not found")
            return
        new = BluePrint()
        new.setToProduce(self.submenue.text)
        new.bolted = False

        self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))


src.items.addType(BluePrintingArtwork)
