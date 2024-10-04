import src


class SimpleRunner(src.items.Item):
    type = "SimpleRunner"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(
            display=src.canvas.displayChars.simpleRunner,
        )
        self.name = "simple runner"
        self.command = None

    def apply(self, character):
        super().apply(character)

        if self.command is None:
            if not len(character.macroState["macros"]):
                character.addMessage(
                    "no macro found - record a macro to store it in this machine"
                )

            options = []
            for key, value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/" + keystroke + "/"
                options.append((key, compressedMacro))

            self.submenue = src.menuFolder.SelectionMenu.SelectionMenu(
                "select the macro you want to store", options
            )
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            character.runCommandString(self.command)

    def storeMacro(self):
        key = self.submenue.selection

        if key not in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return

        import copy

        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.addMessage("you store the command into the machine")
