import src


class Siren(src.items.Item):
    """
    """

    type = "Siren"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="ii")

        self.name = "siren"

        self.applyOptions.extend(
                                                [
                                                    ("run alarm", "run alarm"),
                                                    ("order artwork inteface", "open order artwork interface"),
                                                ]
                                )

        self.applyMap = {
                                    "run alarm": self.runAlarm,
                                    "openOrderArtworkInterface": self.openOrderArtworkInterface,
                                }

    def runAlarm(self, character):
        self.assignQuest({"character":character})

    def runAlarm(self, character):
        self.assignQuest({"character":character})

src.items.addType(Siren)
