import src

class GlassStatue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "GlassStatue"
    description = "Used to build rooms."
    name = "glassStatue"

    def __init__(self,itemID=None):
        '''
        set up internal state
        '''
        super().__init__("GG")

        self.applyOptions.extend(
                        [
                                                                ("showChallenges", "show Challenges"),
                                                                ("getExtraChallenge", "get extra challenge"),
                                                                ("completeChallenge", "complete challenge"),
                                                                ("getReward", "getReward"),
                        ]
                        )
        self.applyMap = {
                    "showChallenges": self.showChallenges,
                    "getExtraChallenge": self.getExtraChallenge,
                    "getReward": self.getReward,
                        }
        self.itemID = itemID
        self.challenges = []

    def showChallenges(self,character):
        character.addMessage(str(self.challenges))

    def getExtraChallenge(self,character):
        character.addMessage(self.itemID)
        character.addMessage("bring me corpses")
        self.challenges.append(("corpses",src.gamestate.gamestate.tick))

    def getReward(self,character):
        corpses = []
        for item in character.inventory:
            if item.type != "MoldFeed":
                continue
            corpses.append(item)

        if self.itemID == 4:
            if not character.weapon:
                character.addMessage("you don't have a weapon to upgrade")
                return

            if character.weapon.baseDamage >= 30:
                character.addMessage("you can't improve your weapon further")

            for corpse in corpses:
                character.weapon.baseDamage += 1
                character.addMessage(f"your weapons base damage is increased by 1 to {character.weapon.baseDamage}")
                character.inventory.remove(corpse)
        elif self.itemID == 5:
            if not character.armor:
                character.addMessage("you don't have a armor to upgrade")
                return

            if character.armor.armorValue >= 8:
                character.addMessage("you can't improve your armor further")

            for corpse in corpses:
                character.armor.armorValue += 0.2
                character.addMessage(f"your armors armor value is increased by 0.2 to {character.armor.armorValue}")
                character.inventory.remove(corpse)
        elif self.itemID == 6:
            if character.health >= 500:
                character.addMessage("you can't improve your armor further")

            for corpse in corpses:
                character.armor.armorValue += 0.2
                character.addMessage(f"your armors armor value is increased by 0.2 to {character.armor.armorValue}")
                character.inventory.remove(corpse)
        else:
            if character.baseDamage >= 5:
                character.addMessage("you can't improve further")

            for corpse in corpses:
                character.baseDamage += 0.1
                character.addMessage(f"your base damage is increased by 0.1 to {character.baseDamage}")
                character.inventory.remove(corpse)

src.items.addType(GlassStatue)
