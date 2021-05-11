import src

'''
'''
class Command(src.items.Item):
    type = "Command"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Command",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.command,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.command = ""
        self.extraName = ""
        self.description = None
        self.level = 1

        self.attributesToStore.extend([
                "command","extraName","level","description"])

    def getLongInfo(self):
        compressedMacro = ""
        for keystroke in self.command:
            if len(keystroke) == 1:
                compressedMacro += keystroke
            else:
                compressedMacro += "/"+keystroke+"/"

        text = """
item: Command

description:
A command. A command is written on it. Activate it to run command.

"""
        text += """

This is a level %s item.
"""%(self.level)

        if self.name:
            text += """
name: %s"""%(self.name)
        if self.description and len(self.description) > 0:
            text += """

description:\n%s"""%(self.description)
        text += """

it holds the command:

%s

"""%(compressedMacro)
        return text

    def apply(self,character):
        super().apply(character,silent=True)

        if isinstance(character,src.characters.Monster):
            return

        if self.level == 1:
            self.runPayload(character)
        else:
            options = [("runCommand","run command"),
                       ("setName","set name"),]
            if self.level > 2:
                options.append(("setDescription","set description"))
            if self.level > 3:
                options.append(("rememberCommand","store command in memory"))

            self.submenue = src.interaction.SelectionMenu("Do you want to reconfigure the machine?",options)
            character.macroState["submenue"] = self.submenue
            character.macroState["submenue"].followUp = self.advancedActions
            self.character = character
            pass

    def advancedActions(self):
        if self.submenue.selection == "runCommand":
            self.runPayload(self.character)
        elif self.submenue.selection == "setName":
            self.submenue = src.interaction.InputMenu("Enter the name")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setName
        elif self.submenue.selection == "setDescription":
            self.submenue = src.interaction.InputMenu("Enter the description")
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setDescription
        elif self.submenue.selection == "rememberCommand":

            if not self.name or self.name == "":
                self.character.addMessage("command not loaded: command has no name")
                return

            properName = True
            for char in self.name[:-1]:
                if not (char.isupper() or char == " "):
                    properName = False
                    break
            if self.name[-1].isupper():
                properName = False
                pass

            if properName:
                self.character.macroState["macros"][self.name] = self.command
                self.character.addMessage("loaded command to macro storage")
            else:
                self.character.addMessage("command not loaded: name not in propper format. Should be capital letters except the last letter. example \"EXAMPLE NAMe\"")
        else:
            self.character.addMessage("action not found")

    def setName(self):
        self.name = self.submenue.text
        self.character.addMessage("set command name to %s"%(self.name))

    def setDescription(self):
        self.description = self.submenue.text
        self.character.addMessage("set command description")

    def runPayload(self,character):
        convertedCommand = []
        for item in self.command:
            convertedCommand.append((item,["norecord"]))
        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]

    def setPayload(self,command):
        import copy
        self.command = copy.deepcopy(command)

    def getDetailedInfo(self):
        if self.extraName == "":
            return super().getDetailedInfo()+" "
        else:
            return super().getDetailedInfo()+" - "+self.extraName

src.items.addType(Command)

