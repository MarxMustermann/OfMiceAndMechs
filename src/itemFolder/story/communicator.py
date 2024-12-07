import src
import random

class Communicator(src.items.Item):
    """
    """

    type = "Communicator"

    def __init__(self,):
        """
        configure the superclass
        """

        super().__init__(display="CC")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        options = []
        options.append(("contact base leader","contact base leader"))
        options.append(("contact main base","contact main base"))
        submenue = src.menuFolder.SelectionMenu.SelectionMenu("what do you want to do?",options,targetParamName="type")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"makeContact","params":{"character":character}}

    def makeContact(self,extraParams):
        character = extraParams["character"]

        if extraParams["type"] == "contact base leader":
            if character.rank > 5:
                character.addMessage("You need to be at least rank 5.")
                character.changed("permission denied",{})

                submenu = src.menuFolder.TextMenu.TextMenu("""
Permission denied:

You need to be at least rank 5 to contact the base leader.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                if character == src.gamestate.gamestate.mainChar:
                    src.gamestate.gamestate.stern["failedContact1"] = True
            else:
                character.addMessage("no base commander")
                submenu = src.menuFolder.TextMenu.TextMenu("""
no base leader found.
""")
                character.macroState["submenue"] = submenu

                if character == src.gamestate.gamestate.mainChar:
                    src.gamestate.gamestate.stern["failedContact1"] = True
                    src.gamestate.gamestate.stern["failedContact2"] = True
                character.changed("no base commander",{})
            return
        if extraParams["type"] == "contact main base":
            if character.rank > 2:
                character.addMessage("You need to be at least rank 2.")
                character.changed("permission denied",{})

                submenu = src.menuFolder.TextMenu.TextMenu("""
Permission denied:

You need to be at least rank 2 to contact main base.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                if character == src.gamestate.gamestate.mainChar:
                    src.gamestate.gamestate.stern["failedBaseContact1"] = True
            else:
                character.addMessage("no main base")
                submenu = src.menuFolder.TextMenu.TextMenu("""
no main base found.
""")
                character.macroState["submenue"] = submenu

                if character == src.gamestate.gamestate.mainChar:
                    src.gamestate.gamestate.stern["failedBaseContact1"] = True
                    src.gamestate.gamestate.stern["failedBaseContact2"] = True
                character.changed("no main base",{})
            return

        character.addMessage("unknown action")

src.items.addType(Communicator)
