import src

class MacroRunner(src.items.Item):
    type = "MacroRunner"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MacroRunner",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.macroRunner,xPosition,yPosition,name=name,creator=creator)
        self.command = None

        self.attributesToStore.extend([
                "command"])

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if self.command == None:
            if not len(character.macroState["macros"]):
                character.addMessage("no macro found - record a macro to store it in this machine")

            options = []
            for key,value in character.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                options.append((key,compressedMacro))

            self.submenue = src.interaction.SelectionMenu("select the macro you want to store",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.storeMacro

            self.character = character
        else:
            import copy
            convertedCommand = []
            for item in self.command:
                convertedCommand.append((item,["norecord"]))
            character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def storeMacro(self):
        key = self.submenue.selection

        if not key in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return

        import copy
        self.command = copy.deepcopy(self.character.macroState["macros"][key])
        self.character.addMessage("you store the command into the machine")

src.items.addType(MacroRunner)
