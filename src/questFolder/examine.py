import src
import random

class Examine(src.quests.MetaQuestSequence):
    type = "Examine"
    lowLevel = True

    def __init__(self, description="examine",reason=None,targetPosition=None,targetPositionBig=None,itemType=None):
        super().__init__()
        self.metaDescription = description
        self.reason = reason
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"""
Decide{reasonString}.

"""
        return text

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # handle menus
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menuFolder.examineMenu.ExamineMenu):
                if character.getBigPosition() != self.targetPositionBig:
                    return (None,(["esc"],"close menu"))
                (show_characters,items,markers) = submenue.get_things_to_show()
                index = submenue.index
                if self.targetPosition:
                    if character.getDistance(self.targetPosition) > 1:
                        return (None,(["esc"],"close menu"))
                    offset = character.getOffset(self.targetPosition)
                    if offset != submenue.offset:
                        messsage = "select spot to examine"
                        if submenue.offset == (1,0,0):
                            return (None,("A",messsage))
                        if submenue.offset == (-1,0,0):
                            return (None,("D",messsage))
                        if submenue.offset == (0,1,0):
                            return (None,("W",messsage))
                        if submenue.offset == (0,-1,0):
                            return (None,("S",messsage))
                        if offset == (1,0,0):
                            return (None,("D",messsage))
                        if offset == (-1,0,0):
                            return (None,("A",messsage))
                        if offset == (0,1,0):
                            return (None,("S",messsage))
                        if offset == (0,-1,0):
                            return (None,("W",messsage))
                if self.itemType:
                    if not items:
                        return self._solver_trigger_fail(dryRun,"no items not found")

                    if len(show_characters) >= index+1:
                        return (None,("s","select item"))
                    if len(show_characters)+len(items) < index+1:
                        return (None,("w","select item"))

                    target_index = len(show_characters)
                    command = None
                    for item in items:
                        target_index += 1
                        if not item.type == self.itemType:
                            continue
                        if target_index == index:
                            if not dryRun:
                                self.postHandler()
                            return (None,("+","end quest"))
                        if target_index > index:
                            command = "s"
                        if target_index < index:
                            command = "w"
                            break

                    if command:
                        return (None,(command,"select item"))
                    return self._solver_trigger_fail(dryRun,"item not found")
                if not dryRun:
                    self.postHandler()
                return (None,("+","end quest"))
            return (None,(["esc"],"close menu"))

        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig, reason="get near the spot you want to examine")
            return ([quest],None)

        if character.getDistance(self.targetPosition) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition, reason="go to the spot you want to examine")
            return ([quest],None)

        return (None,("e","examine"))

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        """
        submenue = character.macroState["submenue"]
        if not submenue or submenue.tag != "player_quest_selection":
            if not dryRun:
                self.postHandler()
            return True
        """

        return False

    def examined(self,extraParams):
        item = extraParams.get("item")
        if not item:
            return

        if self.targetPosition and not item.getPosition() == self.targetPosition:
            return
        if self.targetPositionBig and not item.getBigPosition() == self.targetPositionBig:
            return
        if self.itemType and self.itemType != item.type:
            return

        if item.type == "TriggerPlate":
            src.gamestate.gamestate.stern["examined_trap"] = True
        self.postHandler()

    def assignToCharacter(self, character):
        '''
        start watching the character for getting promotions
        '''
        if self.character:
            return
        self.startWatching(character,self.examined, "examined")
        super().assignToCharacter(character)

src.quests.addType(Examine)
