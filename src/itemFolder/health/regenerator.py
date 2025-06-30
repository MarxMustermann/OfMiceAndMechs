import src

class Regenerator(src.items.Item):
    '''
    Ingame item that heals all characters in the room
    '''
    type = "Regenerator"
    description = "heals all characters in the room"
    name = "regenerator"
    healing_amount = 25
    mana_charges = 100
    def __init__(self):
        self.bolted = True
        self.activated = False
        super().__init__(display="()")

    def addTickingEvent(self):
        '''
        sets up a loop of events that do the actual healing
        '''

        # add event    
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 15)
        event.setCallback({"container": self, "method": "handleTicking"})
        self.container.addEvent(event)

    def apply(self, character):
        '''
        start triggering a loop of healing events on user activation

        Args:
            character: the entity that used the regenerator
        '''

        # do nothing when already running
        if self.activated:
            return

        # trigger the loop of healing events
        self.addTickingEvent()

        # show user feedback
        character.addMessage("You activated the regenerator")
        submenue = src.menuFolder.textMenu.TextMenu(
            f"You activated the Regenerator.\nIt will heal every creature in this room when it pulses.\nIt pulses every 15 ticks"
        )
        character.macroState["submenue"] = submenue
        character.runCommandString("~",nativeKey=True)

        # set internal state to activated
        self.activated = True

        # notify listerners about the state change
        character.changed("regenerator activated",{})

    def handleTicking(self):
        '''
        a loop of events that does the actual healing. This event retriggers itself
        '''

        # set up trigger to be called back later and form a loop
        self.addTickingEvent()

        # show activity indicator to user
        self.container.addAnimation(
            self.getPosition(), "showchar", 1, {"char": ")("}
        )

        # heal all characters within the room
        for character in self.container.characters:
            
            # abort when running out of mana
            if mana_charges < 1:
                break

            # do the actual healing
            character.heal(self.healing_amount, reason="by the regenerator")
            self.container.addAnimation(
                character.getPosition(), "showchar", 1, {"char": [(src.interaction.urwid.AttrSpec("#f00", "#fff"), "^^")]}
            )

            # pay mana cost
            mana_charges -= 1

# registers class
src.items.addType(Regenerator)
