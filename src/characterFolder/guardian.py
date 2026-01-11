import src

import random

class Guardian(src.monster.Monster):
    """
    the class for animated statues
    intended as temple guards
    """

    def __init__(
        self,
        display="&&",
        xPosition=0,
        yPosition=0,
        quests=None,
        automated=True,
        name="Guardian",
        creator=None,
        characterId=None,
        modifier=1,
    ):
        """
        basic state setting

        Parameters:
            display: how the mouse should look like
            xPosition: obsolete, ignore
            yPosition: obsolete, ignore
            quests: obsolete, ignore
            automated: obsolete, ignore
            name: obsolete, ignore
            creator: obsolete, ignore
            characterId: obsolete, ignore
        """
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
        )

        baseMovementSpeed = 2
        baseAttackSpeed = 2
        baseRawDamage = 4
        basehealth = 50
        if src.gamestate.gamestate.difficulty == "medium":
            baseMovementSpeed = 1
            baseAttackSpeed = 1
            baseRawDamage = 8
            basehealth = 400
        if src.gamestate.gamestate.difficulty == "difficult":
            baseMovementSpeed = 0.5
            baseAttackSpeed = 0.5
            baseRawDamage = 10
            basehealth = 800

        self.charType = "Guardian"
        self.specialDisplay = "&&"
        self.hasSpecialAttacks = True
        self.hasPushbackAttack = True
        self.godMode = True

        self.modifier = modifier
        self.maxHealth = basehealth+basehealth*0.25*modifier
        self.health = self.maxHealth
        self.movementSpeed = baseMovementSpeed-(baseMovementSpeed*0.5/15*modifier)
        self.baseAttackSpeed = baseAttackSpeed-(baseAttackSpeed*0.5/15*modifier)
        self.rawBaseDame = baseRawDamage+(baseRawDamage*0.5*modifier)
        self.baseDamage = baseRawDamage+(baseRawDamage*0.5*modifier)

    def changed(self, tag="default", info=None):
        if tag == "pickup bolted fail":
            info["item"].destroy()
        super().changed(tag, info)

    def getCorpse(self):
        return None

    def die(self, reason=None, addCorpse=True, killer=None):
        """
        die without leaving a corpse
        """
        super().die(reason, addCorpse=True, killer=killer)

    def lootTable(self):
        num_ManaCrystal = 0
        num_MemoryFragment = 0
        for _i in range(0,int(self.modifier)):
            if random.random() < 0.5:
                num_ManaCrystal += 1
            else:
                num_MemoryFragment += 1
        return [([src.items.itemMap["MemoryFragment"]]*num_ManaCrystal+[src.items.itemMap["ManaCrystal"]]*num_MemoryFragment, 1)]

    def render(self):
        """
        force static render
        """
        if self.modifier > 7:
            shade = int(255-((255/7)*self.modifier))
            color = (255,shade,shade)
        else:
            color = (150,255,150)
        return (src.interaction.urwid.AttrSpec((255,shade,shade),"#000"), "&&")

src.characters.add_character(Guardian)
