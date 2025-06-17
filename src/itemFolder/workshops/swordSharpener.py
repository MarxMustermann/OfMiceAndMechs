import random

import src
import src.menuFolder
import src.menuFolder.sliderMenu

class SwordSharpener(src.items.itemMap["WorkShop"]):
    type = "SwordSharpener"
    name = "sword Sharpener"
    description = "Use it to upgrade swords"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="SH")
        self.applyOptions.extend([("sharpen sword", "sharpen sword")])
        self.applyMap = {"sharpen sword": self.sharpenSwordHook}
        self.preferredMaxDamage = None
    def sharpenSwordHook(self, character):
        self.sharpenSword({"character": character})

    def amountNeededForOneUpgrade(self, current_damage_output):
        if current_damage_output < 15:
            return 0

        if current_damage_output >= 30:
            return None
        # increase the amount of grindstones needed for better upgrades
        amount_grindstone_needed_for_upgrade = 1
        if current_damage_output >= 20:
            amount_grindstone_needed_for_upgrade += 1
        if current_damage_output >= 23:
            amount_grindstone_needed_for_upgrade += 1
        if current_damage_output >= 25:
            amount_grindstone_needed_for_upgrade += 1
        if current_damage_output >= 26:
            amount_grindstone_needed_for_upgrade += 1
        if current_damage_output >= 27:
            amount_grindstone_needed_for_upgrade += 2
        if current_damage_output >= 28:
            amount_grindstone_needed_for_upgrade += 4
        if current_damage_output >= 29:
            amount_grindstone_needed_for_upgrade += 8

        return amount_grindstone_needed_for_upgrade

    def sharpenSword(self, params):

        # unnpack paramters
        character = params["character"]

        if "amount" in params:
            chosenDamageValue = params["amount"]
            swordOriginalDamage = params["sword"].baseDamage
            amount_grindstone_consumed = 0

            for i in range(swordOriginalDamage, chosenDamageValue):
                amount_grindstone_consumed += self.amountNeededForOneUpgrade(i)

            grindstones = params["grindstones"]
            if amount_grindstone_consumed:
                for grindStone in grindstones[:amount_grindstone_consumed]:
                    character.inventory.remove(grindStone)

            improvementAmount = chosenDamageValue - swordOriginalDamage
            # trigger the actual productions process
            params["productionTime"] = 20 * improvementAmount
            params["doneProductionTime"] = 0
            params["improvementAmount"] = improvementAmount
            params["cost"] = amount_grindstone_consumed
            params["hitCounter"] = character.numAttackedWithoutResponse
            self.produceItem_wait(params)
            return

        # make the user select the 
        if "choice" not in params:
            options = [("Sharpen Equipped Sword", "Sharpen Equipped Sword"), ("Sharpen Sword", "Sharpen Sword")]
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                "Choose item To Sharpen", options, targetParamName="choice"
            )
            submenue.tag = "SwordSharpenerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "sharpenSword", "params": params}
            return

        # check the grindstones that can be used to upgrade the sword
        grindstones = []
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["Grindstone"]):
               continue 
            grindstones.append(item)

        # warn the player that only basic upgrades can be done without grindstones
        if not grindstones:
            character.addMessage("you don't have Grindstone, you only can improve your sword to 15")

        # get the sword to sharpen
        sword = None
        if params["choice"] == "Sharpen Equipped Sword":
            if character.weapon:
                sword = character.weapon
            else:
                character.addMessage("you don't have any sword equipped")
                return
        else:
            for item in character.inventory:
                if isinstance(item, src.items.itemMap["Sword"]):
                    sword = item
                    break
            if sword is None:
                character.addMessage("you don't have any base sword in the inventory")
                return

        # abort and notify the user if the sword is upgraded to the maximum already
        if sword.baseDamage == 30:
            character.addMessage("you can't further improve the sword")
            return

        # get improvement amount that has no costs associated
        improvementAmount = 0
        if sword.baseDamage < 15:
            improvementAmount += 15-sword.baseDamage

        # calculate how many upgrades can be done using grindstones

        amount_grindstone_consumed = 0
        amount_grindstone_needed_for_upgrade = 0
        while 1:
            amount_grindstone_needed_for_upgrade = self.amountNeededForOneUpgrade(sword.baseDamage + improvementAmount)
            if (
                amount_grindstone_needed_for_upgrade is not None
                and amount_grindstone_needed_for_upgrade + amount_grindstone_consumed <= len(grindstones)
            ):
                improvementAmount += 1
                amount_grindstone_consumed += amount_grindstone_needed_for_upgrade
            else:
                break
        # abort and notify user if sword can't be improved
        if not improvementAmount:
            character.addMessage(f"you can't improve your sword.\nYou need {amount_grindstone_needed_for_upgrade} Grindstone to upgrade your sword.")
            character.changed("sharpened sword")
            return

        maxDamageAvailable = sword.baseDamage + improvementAmount
        params["sword"] = sword
        params["nextUpgradeCost"] = amount_grindstone_needed_for_upgrade
        params["grindstones"] = grindstones

        def AmountNeededToLevel(level):
            grindstone_consumed = 0
            for i in range(sword.baseDamage, level):
                grindstone_consumed += self.amountNeededForOneUpgrade(i)
            return f"You will use {grindstone_consumed} grindstone"

        character.macroState["submenue"] = src.menuFolder.sliderMenu.SliderMenu(
            "choose the damage level to upgrade to",
            max(sword.baseDamage + 1, self.preferredMaxDamage)
            if self.preferredMaxDamage is not None
            else min(
                30,
                maxDamageAvailable,
            ),
            sword.baseDamage + 1,
            min(30, maxDamageAvailable),
            1,
            2,
            "amount",
            AmountNeededToLevel,
        )
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "sharpenSword",
            "params": params,
        }

        # remove/destroy grindstones used to upgrade sword

    def produceItem_done(self, params):
        character = params["character"]
        improvement = params["improvementAmount"]
        character.changed("sharpened sword")

        sword = params["sword"]
        sword.baseDamage += improvement

        cost = params["cost"]

        character.addMessage(f"You improved the sword by {improvement!s} to {sword.baseDamage}")
        character.addMessage(f"it costed {cost} grindstone to improve the sword")
        if params.get("nextUpgradeCost"):
            character.addMessage(f'you will need {params.get("nextUpgradeCost")} grindstone to improve the sword again')

    def SetDefaultMaxUpgradeAmount(self, character):
        character.macroState["submenue"] = src.menuFolder.sliderMenu.SliderMenu(
            "set the preferred max amount of damage to upgrade to",
            self.preferredMaxDamage if self.preferredMaxDamage else 20,
            15,
            30,
            1,
        )
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "SetterDefaultMaxUpgradeAmount",
            "params": {"character": character},
        }

    def SetterDefaultMaxUpgradeAmount(self, params):
        character = params["character"]
        self.preferredMaxDamage = params["value"]

    def getConfigurationOptions(self, character):
        base: dict = super().getConfigurationOptions(character)
        base["s"] = ("set upgrade amount", self.SetDefaultMaxUpgradeAmount)
        return base


src.items.addType(SwordSharpener)
