import src


class ScratchPlate(src.items.Item):
    """
    ingame item used as ressource for construction
    """

    type = "ScratchPlate"
    bolted = False
    walkable = True
    name = "scratch plate"
    description = "Used as building material and can be used to mark paths"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=";;")
        self.lastActivation = None

        self.commandOptions.append(("scratch","scratch"))
        self.commandOptions.append(("noscratch","noscratch"))

        self.applyOptions.extend([
                ("scratch","scratch"),
                ("check","check"),
            ])
        self.applyMap = {
            "scratch":self.scratch,
            "check":self.check,
            }
        self.settings["scratchThreashold"] = 10
        self.hasSettings = True

    # bad code: hacky way for bolting the item
    def scratch(self, character):
        """
        handle a character trying to use the item

        Parameters:
            character: the character trying to use the item
        """
        character.addMessage("you scratch the scratch plate")
        self.lastActivation = self.container.timeIndex
        self.runsCommands = True

    def hasScratch(self):
        if not self.lastActivation:
            return False
        return self.container.timeIndex-self.settings["scratchThreashold"] < self.lastActivation

    def check(self, character):
        if self.lastActivation and self.hasScratch():
            character.addMessage("there is a fresh scratch on the scratch plate")
            self.runCommand("scratch",character)
            return
        else:
            character.addMessage("there is no fresh scratch on the scratch plate")
            self.runCommand("noscratch",character)
            return

    def getLongInfo(self):
        """
        returns a longer than normal description of the item

        Returns:
            the description
        """

        text = super().getLongInfo()

        text += """

lastScratch: %s
""" % (
            self.lastActivation
            )

        text += """

hasScratch: %s
""" % (
            self.hasScratch()
        )

        return text

src.items.addType(ScratchPlate)
