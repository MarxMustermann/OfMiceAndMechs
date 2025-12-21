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

        baseMovementSpeed = 4
        baseAttackSpeed = 4
        baseRawDamage = 0.2
        basehealth = 10
        if src.gamestate.gamestate.difficulty == "medium":
            baseMovementSpeed = 2
            baseAttackSpeed = 2
            baseRawDamage = 0.5
            basehealth = 50
        if src.gamestate.gamestate.difficulty == "difficult":
            baseMovementSpeed = 1
            baseAttackSpeed = 1
            baseRawDamage = 1
            basehealth = 100

        self.charType = "Guardian"
        self.specialDisplay = "&&"
        self.maxHealth = basehealth*modifier
        self.hasSpecialAttacks = True
        self.hasPushbackAttack = True
        self.health = self.maxHealth
        self.godMode = True
        self.movementSpeed = baseMovementSpeed/modifier
        self.baseAttackSpeed = baseAttackSpeed/modifier
        self.rawBaseDame = baseRawDamage*modifier
        self.baseDamage = baseRawDamage*modifier
        self.modifier = modifier

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
        for _i in range(0,self.modifier): 
            if random.random() < 0.5:
                num_ManaCrystal += 1
            else:
                num_MemoryFragment += 1
        return [([src.items.itemMap["MemoryFragment"]]*num_ManaCrystal+[src.items.itemMap["ManaCrystal"]]*num_MemoryFragment, 1)]

    def render(self):
        """
        force static render
        """
        color = (255,255,255)
        return (src.interaction.urwid.AttrSpec(color, "black"), "&&")

src.characters.add_character(Guardian)
