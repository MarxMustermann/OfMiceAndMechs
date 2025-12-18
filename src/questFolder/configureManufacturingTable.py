import src
import random

class ConfigureManufacturingTable(src.quests.MetaQuestSequence):
    type = "ConfigureManufacturingTable"

    def __init__(self, description="configure manufacturing table", creator=None, targetPosition=None, targetPositionBig=None,reason=None, itemType=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason
        self.itemType = itemType

    def handleManufactured(self, extraInfo):
        return 
    def handleConfigured(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(self.character,dryRun=False)

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleConfigured, "configured ManufacturingTable")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
Configure the manufacturing table on {self.targetPosition}{reason} to produce {self.itemType}.


"""

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return False

        if not character.container.isRoom:
            if not dryRun:
                self.fail("room gone")
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        manufacturingTable = None
        if items and items[0].type in ("ManufacturingTable",):
            manufacturingTable = items[0]

        if not manufacturingTable:
            if not dryRun:
                self.fail("no manufacturing table")
            return True

        if manufacturingTable.toProduce == self.itemType:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        # handle weird states
        if self.subQuests:
            return (None,None)

        # handle menues
        submenue = character.macroState.get("submenue")
        if submenue:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "ManufacturingTable":
                target_index = None
                counter = 0
                for option in submenue.options.values():
                    counter += 1
                    if option == "configure item":
                        target_index = counter
                if not target_index is None:
                    return (None,("s"*(target_index-submenue.selectionIndex)+"w"*(submenue.selectionIndex-target_index)+"j","configure ManufacturingTable"))
            if submenue.tag == "manufacturingTableTypeConfigurationSelection":

                # get the index of the value to select
                target_index = 0
                for item_type in submenue.options.values():
                    target_index += 1
                    if item_type == self.itemType:
                        break
                else:
                    target_index = len(submenue.options)

                # handle weird edge case
                if target_index is None:
                    return (None,(["esc"],"close the sub menu"))

                # actually select the value
                if target_index < submenue.selectionIndex:
                    return (None,("w"*(submenue.selectionIndex-target_index)+"j","select the item type to set"))
                elif target_index > submenue.selectionIndex:
                    return (None,("s"*(target_index-submenue.selectionIndex)+"j","select the item type to set"))
                else:
                    return (None,("j","select the item type to set"))

            return (None,(["esc"],"close the sub menu"))

        # activate production item when marked
        if character.macroState.get("itemMarkedLast"):
            item = character.macroState["itemMarkedLast"]
            if item.type == "ManufacturingTable" and item.getPosition() == self.targetPosition and item.getBigPosition() == self.targetPositionBig:
                return (None,("j","activate ManufacturingTable"))
            else:
                return (None,(".","undo selection"))
            
        # go to the manufacturing table
        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the ManufacturingTable is on")
            return ([quest],None)
        pos = character.getPosition()
        if self.targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the ManufacturingTable")
            return ([quest],None)

        # start configuring the manufacturing table
        message = "configure item type"
        activationCommand = "J"
        if "advancedInteraction" in character.interactionState:
            activationCommand = " "
        direction = None
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            direction = "."
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            direction = "s"
        if direction:
            return (None,(activationCommand+direction+"sj",message))
        return (None,(".","stand around confused"))

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPositionBig:
            result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            if self.targetPosition and self.targetPositionBig:
                result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

src.quests.addType(ConfigureManufacturingTable)
