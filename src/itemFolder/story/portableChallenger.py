import src


#NIY: half done
class PortableChallenger(src.items.Item):

    """
    ingame item to complete challenges outside
    """

    type = "PortableChallenger"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.portableChallenger)

        self.name = "portable challenger"
        self.challenges = []
        self.done = False
        self.walkable = True
        self.bolted = False
        self.secret = ""

    def apply(self, character):
        """
        handle a character tryin to use the item
        by running the challenge set

        Parameters:
            character: the character trying to use the item
        """

        if not self.challenges:
            self.done = True

        if self.done:
            self.submenue = src.menuFolder.TextMenu.TextMenu(
                "all challenges completed return to auto tutor"
            )
        else:
            if self.challenges[-1] == "gotoEastNorthTile":
                if not (
                    character.room is None
                    and character.xPosition // 15 == 13
                    and character.yPosition // 15 == 1
                ):
                    text = "challenge: go to the most east north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition // 15 < 13:
                        text += "go futher east\n"
                    if character.yPosition // 15 > 1:
                        text += "go futher north\n"

                    self.submenue = src.menuFolder.TextMenu.TextMenu(text)
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestNorthTile":
                if not (
                    character.room is None
                    and character.xPosition // 15 == 1
                    and character.yPosition // 15 == 1
                ):
                    text = "challenge: go to the most west north tile\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition // 15 > 1:
                        text += "go futher west\n"
                    if character.yPosition // 15 > 1:
                        text += "go futher north\n"

                    self.submenue = src.menuFolder.TextMenu.TextMenu(text)
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoWestSouthTile":
                if not (
                    character.room is None
                    and character.xPosition // 15 == 1
                    and character.yPosition // 15 == 13
                ):
                    text = "challenge: go to the most west south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition // 15 > 1:
                        text += "go futher west\n"
                    if character.yPosition // 15 < 13:
                        text += "go futher south\n"

                    self.submenue = src.menuFolder.TextMenu.TextMenu(text)
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "gotoEastSouthTile":
                if not (
                    character.room is None
                    and character.xPosition // 15 == 13
                    and character.yPosition // 15 == 13
                ):
                    text = "challenge: go to the most east south\n\nchallenge in progress\n\ncomment:\n"
                    if character.xPosition // 15 < 13:
                        text += "go futher east\n"
                    if character.yPosition // 15 < 13:
                        text += "go futher south\n"

                    self.submenue = src.menuFolder.TextMenu.TextMenu(text)
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "9livingBlooms":
                baseCoordinateX = character.xPosition - (character.xPosition % 15)
                baseCoordinateY = character.yPosition - (character.yPosition % 15)

                numFound = 0
                for extraX in range(1, 14):
                    for extraY in range(1, 14):
                        for item in character.container.getItemByPosition(
                            (baseCoordinateX + extraX, baseCoordinateY + extraY)
                        ):
                            if item.type == "Bloom" and item.dead is False:
                                numFound += 1

                if not numFound >= 9:
                    self.submenue = src.menuFolder.TextMenu.TextMenu(
                        "challenge: find 9 living blooms\n\nchallenge in progress:\ngo to tile with 9 living blooms on it and activate challenger"
                    )
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "3livingSickBlooms":
                baseCoordinateX = character.xPosition - (character.xPosition % 15)
                baseCoordinateY = character.yPosition - (character.yPosition % 15)

                numFound = 0
                for extraX in range(1, 14):
                    for extraY in range(1, 14):
                        for item in character.container.getItemByPosition(
                            (baseCoordinateX + extraX, baseCoordinateY + extraY)
                        ):
                            if item.type == "SickBloom" and item.dead is False:
                                numFound += 1

                if not numFound >= 3:
                    self.submenue = src.menuFolder.TextMenu.TextMenu(
                        "challenge: find 3 living sick blooms\n\nchallenge in progress:\ngo to tile with 3 living sick blooms on it and activate challenger"
                    )
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            elif self.challenges[-1] == "fullMoldCover":
                baseCoordinateX = character.xPosition - (character.xPosition % 15)
                baseCoordinateY = character.yPosition - (character.yPosition % 15)

                emptyFound = False
                for extraX in range(1, 14):
                    for extraY in range(1, 14):
                        hasMold = False
                        for item in character.container.getItemByPosition(
                            (baseCoordinateX + extraX, baseCoordinateY + extraY)
                        ):
                            if item.type in [
                                "Mold",
                                "Sprout",
                                "Sprout2",
                                "Bloom",
                                "SickBloom",
                                "PoisonBloom",
                                "Bush",
                                "EncrustedBush",
                                "PoisonBush",
                                "EncrustedPoisonBush",
                            ]:
                                hasMold = True
                        if not hasMold:
                            emptyFound = True

                if emptyFound:
                    self.submenue = src.menuFolder.TextMenu.TextMenu(
                        "challenge: find tile completely covered in mold\n\nchallenge in progress:\ngo to a tile completed covered in mold and activate challenger"
                    )
                else:
                    self.submenue = src.menuFolder.TextMenu.TextMenu("challenge done")
                    self.challenges.pop()
            else:
                self.submenue = src.menuFolder.TextMenu.TextMenu("unkown challenge")

        character.macroState["submenue"] = self.submenue

        if not len(self.challenges):
            self.done = True

    def getLongInfo(self):
        """
        returns a description text

        Returns:
            the description text
        """

        text = """
item:

%s
        """ % (
            str(self.challenges)
        )

src.items.addType(PortableChallenger)
