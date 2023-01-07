import src
import random
import copy
import json

class Assimilator(src.items.Item):
    """
    """


    type = "Assimilator"

    def __init__(self, name="Assimilator", noId=False, healingEffect = 50, baseDamageEffect = 2, healthIncrease = 20):
        """
        set up the initial state
        """

        super().__init__(display="AS", name=name)

        self.healingEffect = healingEffect
        self.baseDamageEffect = baseDamageEffect
        self.healthIncrease = healthIncrease
        self.usageInfo = """
Use it by activating it."""

        self.requiredReputationForRank5 = 300
        self.requiredReputationForRank4 = 500
        self.requiredReputationForRank3 = 750

    def getPossibleDuties(self,character, exclude=None):
        out = []
        if "fighting" in character.skills:
            duty = "Questing"
            dutytext = duty+": Get quests from the QuestArtwork and kill things."
            out.append((duty,dutytext))
        if "gathering" in character.skills:
            duty = "resource gathering"
            dutytext = duty+": Collect Scrap and other things"
            out.append((duty,dutytext))
        if "trap maintence" in character.skills:
            duty = "trap setting"
            dutytext = duty+": Reload the trap rooms"
            out.append((duty,dutytext))
        if "cleaning" in character.skills:
            duty = "cleaning"
            dutytext = duty+": clean"
            out.append((duty,dutytext))

        if exclude:
            for option in out[:]:
                if option[0] in exclude:
                    out.remove(option)

        return out

    def selectDuties(self,extraParams):
        character = extraParams["character"]

        duty1 = extraParams.get("duty1")
        if not duty1:
            if character.rank == 6:
                text = """
you can chose to do one duty based on your skills.
Choose how you are gooing to serve:\n"""
            else:
                text = """
Choose your primary duty:\n"""

            options = self.getPossibleDuties(character)

            if not options:
                character.addMessage("no duty found")
                character.changed("changed duties",character)
                return

            submenue = src.interaction.SelectionMenu(text,options,targetParamName="duty1")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":extraParams}
            return

        if character.rank == 6:
            character.duties = [duty1]
            character.changed("changed duties",character)
            return

        duty2 = extraParams.get("duty2")
        if not duty2:
            text = """
Choose your secondary duty:\n"""

            options = self.getPossibleDuties(character,exclude=[duty1])

            if not options:
                character.addMessage("no duty found")
                character.duties = [duty1]
                character.changed("changed duties",character)
                return

            submenue = src.interaction.SelectionMenu(text,options,targetParamName="duty2")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":extraParams}
            return

        if character.rank == 5:
            character.duties = [duty1,duty2]
            character.changed("changed duties",character)
            return

        duty3 = extraParams.get("duty3")
        if not duty3:
            text = """
Choose your tertiary duty:\n"""

            options = self.getPossibleDuties(character,exclude=[duty1,duty2])

            if not options:
                character.addMessage("no duty found")
                character.duties = [duty1,duty2]
                character.changed("changed duties",character)
                return

            submenue = src.interaction.SelectionMenu(text,options,targetParamName="duty3")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":extraParams}
            return

        if character.rank == 4:
            character.duties = [duty1,duty2,duty3]
            character.changed("changed duties",character)
            return

        1/0


    def apply(self,character):
        if character.registers.get("gotMostBasicTraining") == None:
            character.registers["gotMostBasicTraining"] = True
            self.implantIntroduction({"character":character,"step":0})
            character.registers["HOMEx"] = 7
            character.registers["HOMEy"] = 7
            return
        
        if character.rank == None:
            self.shortIntroduction({"character":character})
            return
        
        if character.rank == 6:
            if character.reputation < self.requiredReputationForRank5:
                text = """

you need %s reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""%(self.requiredReputationForRank5,)

                params = {"character":character}
                character.addMessage("----------------"+text+"-----------------")
                submenue = src.interaction.TextMenu(text)
                character.macroState["submenue"] = submenue
                character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":params}
                return
            else:
                self.doRank5Promotion({"character":character,"step":1})
                character.changed("got promotion",character)
            return

        if character.rank == 5:
            if character.reputation < self.requiredReputationForRank4:
                text = """

you need %s reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""%(self.requiredReputationForRank4,)

                params = {"character":character}
                character.addMessage("----------------"+text+"-----------------")
                submenue = src.interaction.TextMenu(text)
                character.macroState["submenue"] = submenue
                character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":params}
                return
            else:
                text = """

you are hereby rank 4.

Continue to be useful.

To help you with that you got the universal leaders blessing.
Additionally you recieve 2 health vials.

"""
                character.changed("got promotion",character)
                character.rank = 4
                character.reputation = 0

                character.baseDamage += self.baseDamageEffect
                character.addMessage("your base damage increased by %s"%(self.baseDamageEffect,))
                character.maxHealth += self.healthIncrease
                character.heal(self.healingEffect)
                character.movementSpeed *= 0.9
                character.addMessage("your max heath increased by %s"%(self.healingEffect,))

            item = src.items.itemMap["Vial"]()
            item.uses = item.maxUses
            character.addToInventory(item,force=True)

            item = src.items.itemMap["Vial"]()
            item.uses = item.maxUses
            character.addToInventory(item,force=True)

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return

        if character.rank == 4:
            cityleader = self.container.getItemsByType("PersonnelArtwork")[0].fetchCityleader()
            print(cityleader)
            if cityleader:
                text = """

you cannot be promoted further. The base already has a leader.

Reapply after this changes.

"""
                character.reputation = 0
            else:
                if character.reputation < self.requiredReputationForRank3:
                    text = """

you need %s reputation to be promoted.

gain reputation by completing quests and killing enemies.
"""%(self.requiredReputationForRank3,)
                    params = {"character":character}
                    character.addMessage("----------------"+text+"-----------------")
                    submenue = src.interaction.TextMenu(text)
                    character.macroState["submenue"] = submenue
                    character.macroState["submenue"].followUp = {"container":self,"method":"selectDuties","params":params}
                    return
                else:
                    text = """

you are hereby rank 3.
This means you are the commander of this base now.

You will carry the burden of the epoch quest now.

To help you with that you got the universal leaders blessing.
Additionally you recieve 2 health vials.

"""
                    character.changed("got promotion",character)
                    character.rank = 3
                    character.reputation = 0

                    character.baseDamage += self.baseDamageEffect
                    character.addMessage("your base damage increased by %s"%(self.baseDamageEffect,))
                    character.maxHealth += self.healthIncrease
                    character.heal(self.healingEffect)
                    character.movementSpeed *= 0.9
                    character.addMessage("your max heath increased by %s"%(self.healingEffect,))

                    item = src.items.itemMap["Vial"]()
                    item.uses = item.maxUses
                    character.addToInventory(item,force=True)

                    item = src.items.itemMap["Vial"]()
                    item.uses = item.maxUses
                    character.addToInventory(item,force=True)

                    self.container.getItemsByType("PersonnelArtwork")[0].setCityleader(character)

                    for quest in character.quests:
                        quest.postHandler()

                    character.quests = []
                    quest = src.quests.EpochQuest()
                    quest.assignToCharacter(character)
                    character.quests.append(quest)
                    quest.activate()

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return
        
        if character.rank == 3:
                text = """

you this bases commander.
you can not increase your rank.

"""

        super().apply(character)

    def shortIntroduction(self,extraParams):
        text = """
Showing short introduction.
"""

        character = extraParams["character"]
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration1","params":params}

    def doRank5Promotion(self,extraParams):
        character = extraParams["character"]
        if extraParams["step"] == 0:
            text = """

you are hereby rank 5.

That means you can have up to 3 subordinates.

Use the personnel artwork to request a subordinate.

---

Most items in the command center are trank locked.
As you gain rank, more of the items on the base will become usable.
You now unlocked the personnel artwork (PA).

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            extraParams["step"] += 1
            character.macroState["submenue"].followUp = {"container":self,"method":"doRank5Promotion","params":extraParams}
            return

        elif extraParams["step"] == 1:
            text = """
you are hereby rank 5.

Continue to be useful.

To help you with that you got the following:

* the universal leaders blessing.
(base damage +%s max health +%s, health +%s)
* 2 health vials

---

You can heal using the vials. The vials are consumables so it is limited healing.
Use the vial or press Jh to heal once or JH to fully heal.

"""%(self.baseDamageEffect,self.healthIncrease,self.healingEffect)
            character.rank = 5
            character.reputation = 0

            character.baseDamage += self.baseDamageEffect
            character.addMessage("your base damage increased by %s"%(self.baseDamageEffect,))
            character.maxHealth += self.healthIncrease
            character.heal(self.healingEffect)
            character.movementSpeed *= 0.9
            character.addMessage("your max heath increased by %s"%(self.healingEffect,))

            item = src.items.itemMap["Vial"]()
            item.uses = item.maxUses
            character.addToInventory(item,force=True)

            item = src.items.itemMap["Vial"]()
            item.uses = item.maxUses
            character.addToInventory(item,force=True)

            character.addMessage("----------------"+text+"-----------------")
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            return

    def implantIntroduction(self,extraParams):
        character = extraParams["character"]
        step = extraParams["step"]

        if step == 0:
            text = """
You have no records on this base.

Showing full introduction.
"""
        elif step == 1:
            text = """
You are a clone and serve in faction %s.

After assimilation you will serve on this base.
All clones on this base work together.
Ranks on this base are 3,4,5,6 and it supports ghuls.
You will have rank 6 the lowest rank beside ghuls.

---

The green @3, @4, @5, @6 and @x are your allies.
Try to work with them.

"""%(character.faction,)
        elif step == 2:
            text = """

Most coordination is done by the implants.
No clone is complete without it.
It stores your tasks and can direct your steps.
Most day to day tasks can be solved completely by the implant.

Ghuls don't have implants and can only execute simple commands.

---

Try pressing "+", if you are lost or a quest doesn't complete correctly.

The Implant is represented by the quests in your UI.
Press "+" to autosolve a step of your quest.

This can result in 2 effects:
* The quest splits into subquests
* The character will move some steps to solve the deepest subquest.

If you want to stop your character from moving automatically press "ctrl-d".
Alternatively click the red "*" in the upper part of your UI to stop.
"""
        else:
            self.basicIntegration1({"character":character})
            return

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character,"step":step+1}
        character.macroState["submenue"].followUp = {"container":self,"method":"implantIntroduction","params":params}


    def basicIntegration1(self,extraParams):
        character = extraParams["character"]
        text = """
This base is primarily organised by a job system.
That means you just will told to be useful.
What you will be doing exactly will be decided by your duties.
The implant will guide you through the steps.

Main duties that have to be taken care of on this base are:

* Hauling:
Carry resources between stockpiles
* Clearing:
Pick up items from the walkways
* Resource fetching:
Transport resources between rooms 
* Resource gathering:
Go outside and collect resources
* Trap reloading:
Reloading the trap rooms

To find tasks to complete just walk around until you find somewhere to be useful.
"""
        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        params = {"character":character}
        character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration2","params":params}

    def basicIntegration2(self,extraParams):
        character = extraParams["character"]
        if not character.skills: 
            text = """

You need to retrain your skills for this base.

You have no skills retrained.

Retrain a skill and return to integrate into the bases systems

"""
            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue

            quest = src.quests.TrainSkill()
            quest.activate()
            quest.assignToCharacter(character)
            quest.generateSubquests(character)
            character.quests.insert(0,quest)
            return

        else:
            if "fighting" in character.skills:
                duty = "Questing"
                dutytext = "Go to the QuestArtwork and complete the quests given."
            if "gathering" in character.skills:
                duty = "resource gathering"
                dutytext = "Collect Scrap and other things"
            if "trap maintence" in character.skills:
                duty = "trap setting"
                dutytext = "Reload the trap rooms"
            if "cleaning" in character.skills:
                duty = "cleaning"
                dutytext = "clean"
            text = """
You hereby have a rank of 6.
You can request promotions here.

Your duties are:

%s:
%s

To help you with that you got the universal leaders blessing.
(base damage +2 max health +20, health +50)

---

your stats were increased and you got healing.
This happens when you complete a story section.

"""%(duty, dutytext,)
            character.rank = 6
            character.reputation = 0

            character.baseDamage += 2
            character.addMessage("your base damage increased by 2")
            character.maxHealth += 20
            character.heal(50)
            character.addMessage("your max heath increased by 20")

            character.addMessage("----------------"+text+"-----------------")

            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"basicIntegration3","params":extraParams}

            character.duties = [duty]

    def basicIntegration3(self,extraParams):
        character = extraParams["character"]
        text = """
Now go on and be useful

----
You were assigned the "be useful" quest.
Initially it will show up as one line only.
When you press "+" that quest generates sub quests.
"""

        character.addMessage("----------------"+text+"-----------------")

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue

        for quest in character.quests:
            quest.postHandler()

        character.quests = []
        quest = src.quests.BeUsefull()
        quest.assignToCharacter(character)
        quest.activate()
        character.quests.append(quest)

src.items.addType(Assimilator)
