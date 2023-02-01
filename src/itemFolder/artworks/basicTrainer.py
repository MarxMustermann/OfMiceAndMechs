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
        trainingType = character.registers.get("trainingFor")

        if trainingType in character.skills:
            trainingType = None
            del character.registers["trainingFor"]
            del character.registers["numTrainingFailed"]
        if trainingType:
            self.startTraining({"character":character,"skillType":trainingType})
            return

        text = """
select the skill you want to train:
"""
        candidates = self.getMatchingCandidates(character)
        random.shuffle(candidates)

        allCandidates = ["fighting","gathering","trap maintence","cleaning","machine operation"]
        random.shuffle(allCandidates)
        for candidate in allCandidates:
            if not candidate in candidates:
                candidates.append(candidate)

        for candidate in candidates[:]:
            if candidate in character.skills:
                candidates.remove(candidate)

        options = []
        for candidate in candidates:
            options.append((candidate,candidate))

        if not options:
            character.addMessage("There are no skills for you to learn")
            character.changed("learnedSkill",character)
            return

        submenue = src.interaction.SelectionMenu(text,options,targetParamName="skillType")
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"startTraining","params":params}

    def getMatchingCandidates(self,character):
        out = []
        if character.baseDamage > 8:
            out.extend(["fighting"])
        if character.movementSpeed < 1:
            out.extend(["gathering","trap maintence","cleaning","machine operation"])
        return out

    def startTraining(self,extraParams):

        trainingType = extraParams.get("skillType")
        if not trainingType:
            return

        character = extraParams["character"]

        if not character.registers.get("numTrainingFailed"):
            character.registers["numTrainingFailed"] = 0
        character.registers["numTrainingFailed"] +=1
        if character.registers["numTrainingFailed"] > 3:
            del character.registers["numTrainingFailed"]
            del character.registers["trainingFor"]
            character.addMessage("you failed the training too often - reseting")
            return
        character.registers["trainingFor"] = trainingType
        character.registers["trainingFor"] = trainingType

        params = {"character":character}
        if trainingType == "fighting":
            self.checkWeapon(params)

        elif trainingType == "gathering":
            self.checkScrap(params)

        elif trainingType == "trap maintence":
            self.checkLightningRod(params)

        elif trainingType == "cleaning":
            self.giveSkillCleaning(params)

        elif trainingType == "machine operation":
            self.giveSkillMachineOperation(params)

    def giveSkillCleaning(self,extraParams):
        character = extraParams["character"]
        text = """

To clean simply pick up items from the walkways.
When your inventory is full put the collected items into storage.

Items cluttering the base can have several negative consequences:

* cluttered trap rooms do not work properly
This is because the enemies need to step on the electrified floor.
Items lying on the floor prevent that.

* the ghul automation might break.
This is because the ghuls can collide with items and get disoriented.

* entry to and passage through rooms might not be possible
This happens rarely but can interrupt a base.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.learnSkill("cleaning")

    def giveSkillMachineOperation(self,extraParams):
        character = extraParams["character"]
        text = """

Find machines, that are ready to be operated.
Those machines will be highlighted in white.
Operate those machines.
Each machine should have a manual.
Read the amnual to understand how the amchine works.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.learnSkill("machine operation")

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

        text = """

This scrap in your hands is the foundation of every industry.
The scrap is pressed into metal bars and then processed into the things around us.
So there always needs for some scrap and other materials.

Search for rooms with scrap input stockpiles that are not filled.
Then go to the scrap fields and collect scrap.
Return to the room and fill the scrap input stockpiles.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.learnSkill("gathering")


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

        quest = src.quests.GatherScrap(lifetime=500)
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

These lightning rods are used to reload the shockers.

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
        character.learnSkill("trap maintence")


    def requireLightningRod(self,character):
        text = """

Fetch a lightning rod to proceed with the training.

You will fetch the lightning rod directly from the production line.

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.questMap["FetchItems"](toCollect="LightningRod",lifetime=500)
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

If that is too complex for you, you can use the implant to fight.

Training complete.

---

To attack enemies walk into them.

For example:

Assuming an enemy is to the field west to you.
press "a" to attack it.

You can also press "m" to attack a nearby enemy.

You can auto fight by pressing gg

"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.learnSkill("fighting")

    def requireWeapon(self,character):
        text = """
Equip yourself to proceed with the training.

You will fetch your weapon and armor directly from the production line.

Available weapons are swords (wt) and rods (+|)
Armor is also available (ar)

Weapons and armor have a quality.
This quality will have a big effect on your combat power.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        quest = src.quests.Equip(lifetime=500)
        quest.assignToCharacter(character)
        quest.activate()
        quest.solver(character)
        character.quests.insert(0,quest)

src.items.addType(BasicTrainer)
