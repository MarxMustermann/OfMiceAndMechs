import src

class GlassStatue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "GlassStatue"
    description = "Used to build rooms."
    name = "glassStatue"

    def __init__(self):
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
        self.challenges = []

    def showChallenges(self,character):
        character.addMessage(str(self.challenges))

    def getExtraChallenge(self,character):
        character.addMessage("bring me corpses")
        self.challenges.append(("corpses",src.gamestate.gamestate.tick))

    def getReward(self,character):
        corpses = []
        for item in character.inventory:
            if not item.type == "MoldFeed":
                continue
            corpses.append(item)

        if character.baseDamage >= 5:
            character.addMessage("you can't improve further")

        for corpse in corpses:
            character.baseDamage += 0.1
            character.addMessage("your base damage is increased by 0.1 to %s"%(character.baseDamage,))
            character.inventory.remove(corpse)


src.items.addType(GlassStatue)
