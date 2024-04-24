import src


class DutyBeacon(src.items.Item):
    """
    ingame item that makes characters using the item run commands
    """

    type = "DutyBeacon"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display="DB")

        self.name = "dutyBeacon"
        self.priority = 0

        self.bolted = False
        self.walkable = False

    def apply(self,character):

        if not self.container.isRoom:
            character.addMessage("this items needs to be within a room to be used")
            return

        options = []
        options.append(("abort", "no change"))
        options.append(("pull", "set to pull"))
        options.append(("push", "set to push"))
        options.append(("neutral", "set tp neutral"))
        options.append(("increase", "increase priority"))
        options.append(("decrease", "decrease priority"))

        submenue = src.interaction.SelectionMenu(f"select the mode for the duty beacon.\n(current priority: {self.container.priority})",options)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"setRoomPrio","params":params}

    def setRoomPrio(self,extraParams):
        room = self.container
        if not room:
            return

        if extraParams["selection"] == "abort":
            return

        priority = 0
        if extraParams["selection"] == "pull":
            priority = 1
        if extraParams["selection"] == "push":
            priority = -1
        if extraParams["selection"] == "neutral":
            priority = 0
        if extraParams["selection"] == "increase":
            priority = room.priority+1
        if extraParams["selection"] == "decrease":
            priority = room.priority-1


        room.priority = priority
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#fff", "#000"), "##")})

    def render(self):
        return (src.interaction.urwid.AttrSpec("#aaa", "black"), "DB")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

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

        text += f"the duty beacon is set to:\n{self.priority}"

        return text

src.items.addType(DutyBeacon)
