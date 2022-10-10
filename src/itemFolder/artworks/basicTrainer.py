import src
import random
import copy
import json

class BasicTrainer(src.items.Item):
    """
    """


    type = "BasicTrainer"

    def __init__(self, name="BasicTrainer", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="BT", name=name)

        self.usageInfo = """
Use it by activating it."""

    def apply(self,character):
        text = """

you will be trained in:

fighting

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"checkWeapon","params":params}

    def checkWeapon(self,extraParams):
        character = extraParams["character"]
        if character.weapon == None or character.armor == None:
            self.requireWeapon(character)
            return

        super().apply(character)
        text = """

You are equiped and ready to fight.

Fighting is simple.
Just hit into enemies until they die.

Training complete.

---

To attack enemies walk into them.

For example:

Assuming an enemy is to the field west to you.
press "a" to attack it.

You can also press "m" to attack a nearby enemy.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        if not "fighting" in character.skills:
            character.skills.append("fighting")

    def requireWeapon(self,character):
        text = """
you will be trained in:

fighting
"""

        text = """

Equip yourself to proceed with the training.

You will fetch your weapon and armor directly from the production line.

----

you got the quest to equip yourself.
This quest will show up as a single line.
Press "+" and it will split up into sub quests.
When the quest is splitted deep enough it can be autosolved.
To autosolve a quest press "+" and your character will do automated actions.
The actions done by the autosolver are aimed at completing the current task.

Sometimes quest do not complete properly when they are done.
Press "+" to make them recalculate and complete.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"requireWeapon2","params":params}

    def requireWeapon2(self,extraParams):
        character = extraParams["character"]
        text = """

Available weapons are swords (wt) and rods (+|)
Armor is also available (ar)

----

Weapons and armor have a quality.
This quality will have a big effect on their combat power.
The equip quest will not take this into consideration.
Selecting good equipment will give you an edge.

This is one example where you beat the auto solver.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"requireWeapon3","params":params}

    def requireWeapon3(self,extraParams):
        character = extraParams["character"]
        text = """

Go fetch your weapons and armor now.

----

press "+" to expand the euip quest.
This will show you where to go.
This will be important going forward.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.Equip()
        quest.assignToCharacter(character)
        quest.activate()
        character.quests.insert(0,quest)

src.items.addType(BasicTrainer)
