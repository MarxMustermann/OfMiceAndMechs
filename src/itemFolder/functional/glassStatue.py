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
                                                                ("showInfo", "show Info"),
                                                                ("showChallenges", "show Challenges"),
                                                                ("getExtraChallenge", "get extra challenge"),
                                                                ("completeChallenge", "complete challenge"),
                                                                ("getReward", "getReward"),
                        ]
                        )
        self.applyMap = {
                    "showInfo": self.showInfo,
                    "showChallenges": self.showChallenges,
                    "getExtraChallenge": self.getExtraChallenge,
                    "getReward": self.getReward,
                        }
        self.itemID = itemID
        self.challenges = []

    def showInfo(self,character):
        if self.itemID:
            character.addMessage(str(src.gamestate.gamestate.gods[self.itemID]))
        else:
            character.addMessage(str(src.gamestate.gamestate.gods))

        if self.itemID == 3:
            character.addMessage("this god can improve your weapon")
        if self.itemID == 4:
            character.addMessage("this god can improve your attack speed")
        if self.itemID == 5:
            character.addMessage("this god can improve your armor")
        if self.itemID == 6:
            character.addMessage("this god can improve your max health")
        if self.itemID == 7:
            character.addMessage("this god can improve your base damage")


    def showChallenges(self,character):
        character.addMessage(str(self.challenges))

    def getExtraChallenge(self,character):
        character.addMessage(self.itemID)
        character.addMessage("bring me corpses")
        self.challenges.append(("corpses",src.gamestate.gamestate.tick))

    def getReward(self,character):
        corpses = []
        for item in character.inventory:
            if not item.type == "MoldFeed":
                continue
            corpses.append(item)

        godInfo = src.gamestate.gamestate.gods.get(self.itemID,None)

        if self.itemID == 3:
            if not character.weapon:
                character.addMessage("you don't have a weapon to upgrade")
                return

            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 1*rewardFactor

                if character.weapon.baseDamage >= 30:
                    character.addMessage("you can't improve your weapon further")
                    return

                increaseValue = min(30-character.weapon.baseDamage,increaseValue)

                godInfo["mana"] -= 10
                character.weapon.baseDamage += increaseValue
                character.addMessage(f"your weapons base damage is increased by {increaseValue} to {character.weapon.baseDamage}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return

        elif self.itemID == 4:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.1*rewardFactor

                if character.attackSpeed <= 0.5:
                    character.addMessage("you can't improve your attack speed further")
                    return

                increaseValue = min(character.attackSpeed-0.5,increaseValue)

                godInfo["mana"] -= 10
                character.attackSpeed -= increaseValue
                character.addMessage(f"your attack speed is improved by {increaseValue} to {character.attackSpeed}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return

            pass

        elif self.itemID == 5:
            if not character.armor:
                character.addMessage("you don't have a armor to upgrade")
                return

            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.2*rewardFactor

                if character.armor.armorValue >= 8:
                    character.addMessage("you can't improve your armor further")
                    return

                increaseValue = min(8-character.armor.armorValue,increaseValue)
                
                godInfo["mana"] -= 10
                character.armor.armorValue += increaseValue
                character.addMessage(f"your armors armor value is increased by {increaseValue} to {character.armor.armorValue}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        elif self.itemID == 6:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 10*rewardFactor

                if character.maxHealth >= 500:
                    character.addMessage("you can't improve your health further")
                    return

                increaseValue = min(500-character.maxHealth,increaseValue)

                godInfo["mana"] -= 10
                character.maxHealth += increaseValue
                character.addMessage(f"your max health is increased by {increaseValue} to {character.maxHealth}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        elif self.itemID == 7:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.1*rewardFactor

                if character.baseDamage >= 10:
                    character.addMessage("you can't improve your base damage further")
                    return

                increaseValue = min(10-character.baseDamage,increaseValue)

                godInfo["mana"] -= 10
                character.baseDamage += increaseValue
                character.addMessage(f"your base damage is increased by {increaseValue} to {character.baseDamage}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        else:
            character.addMessage("unknown god")

src.items.addType(GlassStatue)
