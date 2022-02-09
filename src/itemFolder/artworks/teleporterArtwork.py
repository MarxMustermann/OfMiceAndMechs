import src
import random


class TeleporterArtwork(src.items.Item):
    """
    ingame item that allows the player the convert ressources and
    items by trading
    """

    type = "TeleporterArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        self.doAutoTrade = True
        self.tradingHistory = {}

        super().__init__(display="TT")

        self.name = "teleporter artwork"

        self.applyOptions.extend(
                                                [
                                                    ("teleport", "teleport"),
                                                                                                                                                                                                                                                ]
                                )

        self.applyMap = {
                                    "teleport": self.teleport,
                                }

    def teleport(self,character):
        submenue = src.interaction.InputMenu(
                "input the target coordinate", targetParamName="targetPos"
        )
        character.macroState["submenue"] = submenue
        submenue.followUp = {"container":self,"method":"doTeleport","params":{"character":character}}

    def doTeleport(self,extraInfo):
        try:
            xPos = int(extraInfo["targetPos"].split(",")[0])
            yPos = int(extraInfo["targetPos"].split(",")[1])
        except:
            return
        extraInfo["character"].addMessage("should do teleport")
        oldPosX = self.container.xPosition
        oldPosY = self.container.yPosition
        self.container.container.removeRoom(self.container)
        newTerrain = src.gamestate.gamestate.terrainMap[yPos][xPos]
        self.container.xPosition = oldPosX
        self.container.yPosition = oldPosY
        newTerrain.addRoom(self.container)
        

src.items.addType(TeleporterArtwork)
