import random

import src


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
        submenue = src.menuFolder.inputMenu.InputMenu(
                "input the target coordinate", targetParamName="targetPos"
        )
        character.macroState["submenue"] = submenue
        submenue.followUp = {"container":self,"method":"doTeleport","params":{"character":character}}

    def doTeleport(self,extraInfo):
        xPos = int(extraInfo["targetPos"].split(",")[0])
        yPos = int(extraInfo["targetPos"].split(",")[1])

        extraInfo["character"].addMessage("should do teleport")
        oldPosX = self.container.xPosition
        oldPosY = self.container.yPosition
        self.container.container.removeRoom(self.container)

        newTerrain = src.gamestate.gamestate.terrainMap[yPos][xPos]
        if 1 == 1:
            while True:
                newRoomPos = (random.randint(1,13),random.randint(1,13),0)
                if newTerrain.getRoomByPosition(newRoomPos):
                    continue
                break
        else:
            newRoomPos = (oldPosX,oldPosY,0)
        self.container.xPosition = newRoomPos[0]
        self.container.yPosition = newRoomPos[1]
        newTerrain.addRoom(self.container)

        for character in self.container.characters[:]:
            character.changed("changedTerrain",{"character":character})

src.items.addType(TeleporterArtwork)
