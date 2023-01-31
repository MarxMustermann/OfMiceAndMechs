import src

class BeUsefullOnTile(src.quests.questMap["BeUsefull"]):
    type = "BeUsefullOnTile"

    def getRequiredParameters(self):
        parameters = super().getRequiredParameters()
        parameters.append({"name":"targetPosition","type":"coordinate"})
        return parameters

src.quests.addType(BeUsefullOnTile)
