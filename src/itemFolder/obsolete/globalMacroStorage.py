import src

"""
"""


class GlobalMacroStorage(src.items.Item):
    type = "GlobalMacroStorage"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.globalMacroStorage)
        self.name = "global macro storage"

    def apply(self, character):

        self.character = character

        options = []
        options.append(("load", "load macro from global storage"))
        options.append(("store", "add macro to the global storage"))
        self.submenue = src.interaction.SelectionMenu("what do you want to do", options)
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSelection

    def actionSelection(self):
        selection = self.submenue.getSelection()
        if selection == "load":
            try:
                with open("globalStorage.json", "r") as globalStorageFile:
                    globalStorage = json.loads(globalStorageFile.read())
            except:
                globalStorage = []

            counter = 1

            options = []
            for entry in globalStorage:
                options.append((counter, entry["name"]))
                counter += 1
            self.submenue = src.interaction.SelectionMenu(
                "what macro do you want to load?", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.load

        if selection == "store":
            self.submenue = src.interaction.InputMenu(
                "supply a name/description for the macro"
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.store

    def load(self):
        try:
            with open("globalStorage.json", "r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        rawMacros = globalStorage[self.submenue.getSelection() - 1]["macro"]
        parsedMacros = {}

        state = "normal"
        for key, value in rawMacros.items():
            parsedMacro = []
            for char in value:
                if state == "normal":
                    if char == "/":
                        state = "multi"
                        combinedKey = ""
                        continue
                    parsedMacro.append(char)
                if state == "multi":
                    if char == "/":
                        state = "normal"
                        parsedMacro.append(combinedKey)
                    else:
                        combinedKey += char
            parsedMacros[key] = parsedMacro

        self.character.macroState["macros"] = parsedMacros
        self.character.addMessage(
            "you load the macro %s from the macro storage"
            % (globalStorage[self.submenue.getSelection() - 1]["name"])
        )

    def store(self):
        try:
            with open("globalStorage.json", "r") as globalStorageFile:
                globalStorage = json.loads(globalStorageFile.read())
        except:
            globalStorage = []

        compressedMacros = {}
        for key, value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/" + keystroke + "/"
            compressedMacros[key] = compressedMacro

        globalStorage.append({"name": self.submenue.text, "macro": compressedMacros})

        with open("globalStorage.json", "w") as globalStorageFile:
            globalStorageFile.write(
                json.dumps(globalStorage, indent=10, sort_keys=True)
            )

        self.character.addMessage("you store the macro in the global macro storage")

    def getLongInfo(self):
        text = """

This device is a one of a kind machine. It allows to store and load marcos between gamestates.

"""
        return text


src.items.addType(GlobalMacroStorage)
