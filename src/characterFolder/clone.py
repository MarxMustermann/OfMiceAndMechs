import src

class Clone(src.characters.Character):
    '''
    the "human" player class
    '''
    def __init__(
        self,
        display="@@",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name=None,
        creator=None,
        characterId=None,
        firstname=None
    ):
        if quests is None:
            quests = []
        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
            firstname=firstname
        )

        self.charType = "Clone"
        self.lastMapSync = None
        self.waitLength = 1
        self.specialChatOptions = []

    '''
    drop a implant in addition to the corpse
    '''
    def die(self, reason=None, addCorpse=True, killer=None):
        if not addCorpse:
            super().die(reason=reason, addCorpse=addCorpse, killer=killer)
            return

        #self.container.addItem(src.items.itemMap["Implant"](), self.getPosition())
        super().die(reason=reason, addCorpse=addCorpse, killer=killer)

    def getLoreDescription(self):
        return [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You see a Clone")," a humanoid figure. all Clones look slightly different but look kind of the same"]

    def getFunctionalDescription(self):
        return (src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),f"Clones are the normal player and NPC characters.\nClone vary widly in skills, behaviour, equipment and stats.")

    def description(self):
        return [self.getLoreDescription(),"\n\n---- ",self.getFunctionalDescription()]

    def getSpecialChatOptions(self):
        return self.specialChatOptions

# register the creature type
src.characters.add_character(Clone)
