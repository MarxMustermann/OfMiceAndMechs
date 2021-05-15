import src

"""
"""


class Sheet(src.items.Item):
    type = "Sheet"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, noId=False):
        super().__init__(display=src.canvas.displayChars.sheet)

        self.bolted = False
        self.walkable = True
        self.recording = False
        self.character = None
        self.name = "sheet"
        self.description = "Simple building material and use to store information."
        self.usageInfo = """
Can be used to create a Note or a written command directly from the sheet.
Activate the sheet to get a selection, whether to create a command or a note.

To create a note select the "create note" option and type the text of the note.
Press enter to finish entering the text.

To create a command from a sheet. select the the "create command" option.
There are two ways to enter the command.

The first option is to record a new command.
After activating this option you will start to record your actions.
Activate the sheet again to create to command and to stop recording.

The second option ist to store a command from an existing macro buffer.
Activate this option and select the macro buffer to create the command.

Sheets are also needed as resource to create a blueprint in the blueprinter machine."""

        self.level = 1

        self.attributesToStore.extend(["recording", "level"])

    def getLongInfo(self):
        text = super().getLongInfo()
        text += """
Sheets can be produced from metal bars.

This is a level %s item

""" % (
            self.level,
        )
        return text

    def apply(self, character):
        if self.recording:
            self.createCommand()
            return

        if isinstance(character, src.characters.Monster):
            return

        self.character = character

        options = []
        options.append(("createCommand", "create a written command"))
        options.append(("createNote", "create a note"))
        options.append(("createMap", "create a map"))
        options.append(("createJobOrder", "create a job order"))
        self.submenue = src.interaction.SelectionMenu(
            "What do you want do do?", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.actionSwitch

    def actionSwitch(self):
        if self.submenue.selection == "createNote":
            self.createNote()
        elif self.submenue.selection == "createCommand":
            self.createCommand()
        elif self.submenue.selection == "createMap":
            self.createMapItem()
        elif self.submenue.selection == "createJobOrder":
            self.createJobOrder()

    def createNote(self):
        self.submenue = src.interaction.InputMenu(
            "type the text you want to write on the note"
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.createNoteItem

    def createNoteItem(self):

        note = src.items.itemMap["Note"]()
        note.setText(self.submenue.text)

        if self.xPosition:
            self.container.removeItem(self)
            self.container.addItem(note,self.getPosition())
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(note)

    def createMapItem(self):
        if self.xPosition:
            self.container.removeItem(self)
            self.container.addItem(mapItem,self.getPosition())
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(mapItem)

    def createJobOrder(self):

        jobOrder = src.items.itemMap["JobOrder"]()

        if self.xPosition:
            self.container.removeItem(self)
            self.container.addItem(jobOrder,self.getPosition())
        else:
            self.character.inventory.remove(self)
            self.character.inventory.append(jobOrder)

    def createCommand(self):

        if not self.character:
            return

        if not len(self.character.macroState["macros"]):
            self.character.addMessage(
                "no macro found - record a macro to be able to write a command"
            )

        if self.recording:
            convertedCommand = []
            convertedCommand.append(("-", ["norecord"]))
            self.character.macroState["commandKeyQueue"] = (
                convertedCommand + self.character.macroState["commandKeyQueue"]
            )

            if "a" not in self.character.macroState["macros"]:
                self.character.addMessage('no macro found in buffer "a"')
                return

            if self.xPosition:
                self.character.macroState["macros"]["a"] = self.character.macroState[
                    "macros"
                ]["a"][:-1]
            else:
                counter = 1
                while not self.character.macroState["macros"]["a"][-counter] == "i":
                    counter += 1
                self.character.macroState["macros"]["a"] = self.character.macroState[
                    "macros"
                ]["a"][:-counter]
            self.storeMacro("a")
            self.recording = False
            del self.character.macroState["macros"]["a"]
            return

        options = []
        options.append(
            (
                "record",
                "start recording (records to buffer + reapply to create command)",
            )
        )
        options.append(("store", "store macro from memory"))
        self.submenue = src.interaction.SelectionMenu(
            "select how to get the commands content", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeSelect

    def storeSelect(self):
        if self.submenue.selection == "record":
            self.recordAndstore()
        elif self.submenue.selection == "store":
            self.storeFromMacro()

    def recordAndstore(self):
        self.recording = True
        convertedCommand = []
        convertedCommand.append(("-", ["norecord"]))
        convertedCommand.append(("a", ["norecord"]))
        self.character.macroState["commandKeyQueue"] = (
            convertedCommand + self.character.macroState["commandKeyQueue"]
        )

    def storeFromMacro(self):
        self.recording = True

        options = []
        for key, value in self.character.macroState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/" + keystroke + "/"
            options.append((key, key + " - " + compressedMacro))

        self.submenue = src.interaction.SelectionMenu(
            "select the macro you want to store", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.storeMacro

    def storeMacro(self, key=None):
        if not key:
            key = self.submenue.selection

        if key not in self.character.macroState["macros"]:
            self.character.addMessage("command not found in macro")
            return

        command = src.items.itemMap["Command"]()
        command.setPayload(self.character.macroState["macros"][key])

        self.character.addMessage("you created a written command")

        if self.container:
            self.container.addItem(command, self.getPosition())
            self.container.removeItem(self)
        else:
            self.character.inventory.append(command)
            self.character.inventory.remove(self)


src.items.addType(Sheet)
