import src


class DutyBell(src.items.Item):
    """
    ingame item that makes characters using the item run commands
    """

    type = "DutyBell"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display="DB")

        self.name = "dutyBell"
        self.description = ""
        self.usageInfo = ""

        self.bolted = False
        self.walkable = False

        self.duty = "machine operation"
        self.duty = None

    def apply(self,character):
        if not self.container.isRoom:
            character.addMessage("this items needs to be within a room to be used")
            return

        if self.duty:
            if self.duty not in self.container.requiredDuties:
                self.container.requiredDuties.append(self.duty)

            dutySignals = {"machine operation":"MO","resource fetching":"RF","resource gathering":"RG","painting":"PT","machine placing":"MP"}
            dutySignal = dutySignals.get(self.duty,"##")

            character.addMessage(f"you ring the duty bell to signal {self.duty} is needed")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), dutySignal)})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})
            self.container.addAnimation(self.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})
            self.container.addAnimation(self.getPosition(offset=(0,1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})
            self.container.addAnimation(self.getPosition(offset=(0,-1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})
        else:
            options = []
            options.append(("machine operation", "machine operations"))
            options.append(("resource fetching", "resource fetching"))
            options.append(("resource gathering", "resource gathering"))
            options.append(("painting", "painting"))
            options.append(("machine placing", "machine placing"))
            options.append(("room building", "room building"))

            submenue = src.interaction.SelectionMenu("select the duty to set",options)
            character.macroState["submenue"] = submenue
            params = {"character":character}
            character.macroState["submenue"].followUp = {"container":self,"method":"setDuty","params":params}

    def ringDuty(self,extraParams):
        print(extraParams)
        1/0

    def render(self):
        if self.container and self.duty in self.container.requiredDuties:
            return (src.interaction.urwid.AttrSpec("#fff", "black"), "DB")
        else:
            return (src.interaction.urwid.AttrSpec("#aaa", "black"), "DB")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        options["d"] = ("set duty", self.dutySelection)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def dutySelection(self,character):
        options = []
        options.append(("machine operation", "machine operations"))
        options.append(("resource fetching", "resource fetching"))
        options.append(("resource gathering", "resource gathering"))
        options.append(("painting", "painting"))
        options.append(("machine placing", "machine placing"))
        options.append(("room building", "room building"))

        submenue = src.interaction.SelectionMenu("select the duty to set",options)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"setDuty","params":params}

    def setDuty(self,extraParams):
        if not extraParams.get("selection"):
            return

        character = extraParams["character"]
        self.duty = extraParams["selection"]
        character.addMessage(f"you set the duty to {self.duty}")

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Machine")

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Machine")

    def getLongInfo(self):
        """
        returns a longer than normal description of the item

        Returns:
            the description
        """

        text = super().getLongInfo()

        text += f"this bell signals the duty:\n{self.duty}"

        return text

src.items.addType(DutyBell)
