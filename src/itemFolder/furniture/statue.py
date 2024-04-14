import src


class Statue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Statue"
    description = "Used for decoration and religious purposes"
    name = "statue"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__("@@")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
            options["p"] = ("pray", self.pray)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def apply(self,character):
        self.pray(character)

    def pray(self,character):
        options = []
        options.append((1,[(src.interaction.urwid.AttrSpec("#f00","black"),"1 - god of fertility")]))
        options.append((2,[(src.interaction.urwid.AttrSpec("#0f0","black"),"2 - god of desolution")]))
        options.append((3,[(src.interaction.urwid.AttrSpec("#00f","black"),"3 - god of construction")]))
        options.append((4,[(src.interaction.urwid.AttrSpec("#0ff","black"),"4 - god of fighting")]))
        options.append((5,[(src.interaction.urwid.AttrSpec("#f0f","black"),"5 - god of battle gear")]))
        options.append((6,[(src.interaction.urwid.AttrSpec("#ff0","black"),"6 - god of life")]))
        options.append((7,[(src.interaction.urwid.AttrSpec("#fff","black"),"7 - god of crushing")]))

        submenu = src.interaction.SelectionMenu(
            "Select what god to pray to", options,
            targetParamName="god",
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
                "container": self,
                "method": "pray2",
                "params": {"character":character},
        }

    def pray2(self,extraInfo):
        # convert parameters to local variables
        godID = extraInfo["god"]
        if godID is None:
            return
        character = extraInfo["character"]

        container = self.container
        character.addMessage("the Statue turns into a GlassStatue")
        new = src.items.itemMap["GlassStatue"](itemID=godID)
        container.addItem(new,self.getPosition())
        container.removeItem(self)

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15))+10)
        event.setCallback({"container": new, "method": "handleEpochChange"})
        container.addEvent(event)

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        return f"""Statues are mainly of decorative purposes.

It also serves a religious use.
You can pray at a Statue to convert it to a GlassStatue.
A GlassStatue can be used to interact with the gods.
"""

src.items.addType(Statue)
