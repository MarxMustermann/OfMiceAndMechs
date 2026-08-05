import src

import random

class OpenObserveMenu(src.quests.MetaQuestSequence):
    type = "OpenObserveMenu"

    def __init__(self, description="open observe menu", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,observationsRequired=10):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.spotsObserved = []
        self.observationsRequired = observationsRequired

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menues.menuMap["ObserveMenu"]):
                command = []
                command.extend(["w"]*(submenue.index[1]-6))
                command.extend(["s"]*(6-submenue.index[1]))
                command.extend(["a"]*(submenue.index[0]-6))
                command.extend(["d"]*(6-submenue.index[0]))
                return (None,(command,"move the cursor"))
            if not submenue.tag == "open observe info":
                return (None,(["esc",],"close the menu"))

        return (None,("o","open observe menu"))

    def generateTextDescription(self):
        text = []
        text.extend(["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Open the observation menu"""),""" and look around afterwards.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""
Do this by pressing o after closing this menu.
You can move the cursor by pressing the wasd key.
""")])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.lookedAt, "lookedAt")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False

    def lookedAt(self,extraInformation):
        spot = (extraInformation["index_big"],extraInformation["index"])
        if not spot in self.spotsObserved:
            self.spotsObserved.append(spot)

        if extraInformation["index"] == (6,6,0):
            self.postHandler()

        if len(self.spotsObserved) >= self.observationsRequired:
            self.postHandler()

src.quests.addType(OpenObserveMenu)
