import src

class ShieldBug(src.characters.characterMap["Insect"]):
    def __init__(
        self,
        display="/>",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="ShieldBug",
        creator=None,
        characterId=None,
        level=1,
        runModifier=0,
    ):
        if quests is None:
            quests = []

        self.level = level
        multiplier = level

        super().__init__(
            display,
            xPosition,
            yPosition,
            quests,
            automated,
            name,
            creator=creator,
            characterId=characterId,
        )
        self.charType = "Insect"
        self.specialDisplay = "/>"
        self.baseDamage = 5
        self.baseDamage = int(self.baseDamage * (1 - runModifier))

        self.maxHealth = int(100 * multiplier)
        self.maxHealth = int(self.maxHealth * (1 + runModifier))
        self.health = self.maxHealth

        if src.gamestate.gamestate.difficulty == "difficult":
            self.baseDamage *= 2
            self.health *= 2
            self.maxHealth *= 2

        self.godMode = True
        self.movementSpeed = 2.2

        self.autoAdvance = True

    def render(self):
        """
        force static render
        """
        try:
            self.level
        except:
            self.level = 1
        if self.level is None:
            self.level = 1
        color_1 = self.color_for_multiplier(self.level, start=(255, 255, 255), end=(255, 0, 0))[0]
        color_2 = self.color_for_multiplier(self.level, start=(0, 66, 46), end=(33, 255, 101))[0]
        return [(color_1,"<"),(color_2,"/")]

    """
    def render(self):
        self.level = self.maxHealth//100
        return (src.interaction.urwid.AttrSpec(front_color_1,"black"), "/")
    """

    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    @staticmethod
    def lootTable():
        return [(None, 1), (src.items.itemMap["ChitinPlates"], 1)]

    def getLoreDescription(self):
        return [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You see a ShieldBug.")," It slowly moves dragging its enourmous weight through the mud.\nThe oldest ShieldBugs have ChitinPlates almost unpenetrable by a normal blade."]

    def getFunctionalDescription(self):
        return (src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),f"Shieldbugs have a lot of HP and are slow. Some are stronger than others.")

    def description(self):
        return [self.getLoreDescription(),"\n\n---- ",self.getFunctionalDescription()]

    def generateQuests(self):

        quest = src.quests.questMap["SecureTile"](toSecure=self.getBigPosition(),wandering=True, endWhenCleared=False,neverHuntDown=True)
        quest.autoSolve = True
        quest.assignToCharacter(self)
        quest.activate()
        self.quests.append(quest)

        return super().generateQuests()

src.characters.add_character(ShieldBug)
