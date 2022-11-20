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
        numTries = character.registers.get("numTrainingTries")
        if not numTries:
            numTries = 1
            character.registers["numTrainingTries"] = numTries
        character.registers["numTrainingTries"] = numTries + 1

        print("numTries")
        print(numTries)

        if numTries > 5:
            text = """

you seem to have some trouble. You will be trained in:

gathering

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            params = {"character":character}
            character.macroState["submenue"].followUp = {"container":self,"method":"checkScrap","params":params}

        elif character.baseDamage > 5:
            text = """

you will be trained in:

fighting

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            params = {"character":character}
            character.macroState["submenue"].followUp = {"container":self,"method":"checkWeapon","params":params}
        else:
            text = """

you will be trained in:

trap maintenence

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            params = {"character":character}
            character.macroState["submenue"].followUp = {"container":self,"method":"checkLightningRod","params":params}

    def checkScrap(self,extraParams):
        character = extraParams["character"]
        foundItem = None
        for item in character.inventory:
            if item.type == "Scrap":
                foundItem = item
                break

        if not foundItem:
            self.requireScrap(character)
            return

        super().apply(character)
        text = """

This scrap in your hands is the foundation of every industry.
The scrap is pressed into metal bars and then processed into the things around us.
So there always needs for some scrap and other materials.


"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        if not "gathering" in character.skills:
            character.skills.append("gathering")


    def requireScrap(self,character):
        text = """

Fetch a piece of scrap to proceed with the training.

Fetching the scrap is easy, just pick it up and bring it in.
The scrap pile can be found in many places, but primarily on scrap fields.
You will fetch the scrap from a scrap field.
The scrap field is marked with a white ss on the mini map.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.GatherScrap()
        quest.assignToCharacter(character)
        quest.activate()
        character.quests.insert(0,quest)


    def checkLightningRod(self,extraParams):
        character = extraParams["character"]
        foundItem = None
        for item in character.inventory:
            if item.type == "LightningRod":
                foundItem = item
                break

        if not foundItem:
            self.requireLightningRod(character)
            return

        super().apply(character)
        text = """

The lightning rods are used to reload the shockers.

One of the main defence systems of this base are the Trap rooms.
The trap rooms shock enemies that move through them.
Each shock uses up one charge.

When all charges are used up, the trap room is useless.
The trap rooms can be recharged using the shockers.
Use a shocker with lightning rods in your inventory to recharge the rooms.

When doing trap setting duty, your job is to ensure that the trap rooms are charged.
Training complete.

---

The trap rooms are your primary defence,
so do try to keep them charged.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        if not "trapReloading" in character.skills:
            character.skills.append("trapReloading")


    def requireLightningRod(self,character):
        text = """

Fetch a lightning rod to proceed with the training.

You will fetch the lightning rod directly from the production line.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.FetchItems(toCollect="LightningRod")
        quest.assignToCharacter(character)
        quest.activate()
        character.quests.insert(0,quest)


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
