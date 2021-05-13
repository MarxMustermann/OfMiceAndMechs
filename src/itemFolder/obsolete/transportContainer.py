import src

class TransportContainer(src.items.Item):
    type = "TransportContainer"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__(display="TC")

        self.name = "transport container"

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        options = [("addItems","load item"),
                   ("transportItem","transport item"),
                   ("getJobOrder","set transport command")
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        # add item
        # remove item
        # transport item
        # set transport command
        pass

src.items.addType(TransportContainer)
