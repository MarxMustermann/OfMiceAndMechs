import random

import src
from decimal import Decimal as D

class ArmorReinforcer(src.items.itemMap["WorkShop"]):
    """
    ingame item to uprage armor
    """

    type = "ArmorReinforcer"
    name = "armor Reinforcer"
    description = "Use it to upgrade armors"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="AR")

        # configure interaction menu
        self.applyOptions.extend([("Reinforce Armor", "Reinforce Armor")])
        self.applyMap = {"Reinforce Armor": self.reinforceArmorHook}
        self.preferredMaxDefense = None

    def amountNeededForOneUpgrade(self, current_defense_output):
        if current_defense_output < D("3"):
            return 0

        if current_defense_output > D("8"):
            return None

        amount_ChitinPlates_needed_for_upgrade = 1
        if current_defense_output >= D("4"):
            amount_ChitinPlates_needed_for_upgrade += 1
        if current_defense_output >= D("5"):
            amount_ChitinPlates_needed_for_upgrade += 2
        if current_defense_output >= D("6"):
            amount_ChitinPlates_needed_for_upgrade += 3
        if current_defense_output >= D("7"):
            amount_ChitinPlates_needed_for_upgrade += 4

        return amount_ChitinPlates_needed_for_upgrade

    def reinforceArmorHook(self, character):
        """
        indirection to call the actual function
        """
        self.reinforceArmor({"character": character})

    def reinforceArmor(self, params):
        """
        start upgrading the armor
        """

        # unpack the parameters
        character = params["character"]

        if "amount" in params:
            chosenDefenseValue = params["amount"]
            armorOriginalDamage = params["armor"].armorValue
            if chosenDefenseValue == armorOriginalDamage:
                return


            ChitinPlates_consumed = 0
            base = D(params["armor"].armorValue)
            while base < chosenDefenseValue:
                ChitinPlates_consumed += self.amountNeededForOneUpgrade(base)
                base += D("0.5")

            chitinPlates = params["chitinPlates"]
            if ChitinPlates_consumed:
                for chitinPlate in chitinPlates[:ChitinPlates_consumed]:
                    character.inventory.remove(chitinPlate)

            improvementAmount = int(chosenDefenseValue - armorOriginalDamage)
            # trigger the actual productions process
            params["productionTime"] = 20 * improvementAmount * 2
            params["doneProductionTime"] = 0
            params["improvementAmount"] = improvementAmount
            params["cost"] = ChitinPlates_consumed
            params["hitCounter"] = character.numAttackedWithoutResponse
            self.produceItem_wait(params)
            return
        # get user input on what armor to upgrade
        if "choice" not in params:
            options = [("Reinforce Equipped Armor", "Reinforce Equipped Armor"), ("Reinforce Armor", "Reinforce Armor")]
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                "Choose item To Reinforce", options, targetParamName="choice"
            )
            submenue.tag = "ArmorReinforceerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "reinforceArmor", "params": params}
            return

        # get available chitin plates
        chitinPlates = []
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["ChitinPlates"]):
                continue
            chitinPlates.append(item)

        # show warning message when upgrade items are missing
        if not chitinPlates:
            character.addMessage("you don't have ChitinPlates, you need ChitinPlates to upgrade your Armor up to more than 3")

        # get the armor to upgrade
        armor = None
        if params["choice"] == "Reinforce Equipped Armor":
            if character.armor:
                armor = character.armor
            else:
                character.addMessage("you don't have any Armor equipped")
                return
        else:
            for item in character.inventory:
                if isinstance(item, src.items.itemMap["Armor"]):
                    armor = item
                    break
            if armor is None:
                character.addMessage("you don't have any Armor in the inventory")
                return

        improvementAmount = (D("3") - D(armor.armorValue)) if D(armor.armorValue) < D("3") else 0
        amount_ChitinPlates_needed_for_upgrade = self.amountNeededForOneUpgrade(
            D(armor.armorValue) + D("0.5") + improvementAmount
        )

        if amount_ChitinPlates_needed_for_upgrade is None:
            character.addMessage("you can't improve your armor further.")
            return

        if amount_ChitinPlates_needed_for_upgrade > len(chitinPlates) and improvementAmount == D("0"):
            character.addMessage(
                f"you can't improve your armor.\nYou need {amount_ChitinPlates_needed_for_upgrade} ChitinPlates to upgrade your armor."
            )
            character.changed("improved armor")
            return
        params["armor"] = armor
        params["chitinPlates"] = chitinPlates

        def amountNeededToLevel(level, allowed=None):
            ChitinPlates_consumed = 0
            base = D(armor.armorValue)
            if base == level and not allowed:
                return "the armor won't be upgraded"

            while base < level:
                ChitinPlates_consumed += self.amountNeededForOneUpgrade(base)
                base += D("0.5")

            available = ChitinPlates_consumed <= len(chitinPlates)

            if allowed:
                return available

            if available:
                return f"You will use {ChitinPlates_consumed} ChitinPlates"
            else:
                return f"You will need {ChitinPlates_consumed} ChitinPlates to be able to upgrade"

        try:
            self.preferredMaxDefense
        except:
            self.preferredMaxDefense = 6

        character.macroState["submenue"] = src.menuFolder.sliderMenu.SliderMenu(
            "choose the Defense level to upgrade to",
            defaultValue=max(
                armor.armorValue,
                self.preferredMaxDefense
                if self.preferredMaxDefense and amountNeededToLevel(self.preferredMaxDefense, True) <= len(chitinPlates)
                else 0,
            ),
            minValue=D(armor.armorValue),
            maxValue=D(8),
            stepValue=D(0.5),
            bigStepValue=D(1.0),
            targetParamName="amount",
            additionalInfoCallBack=amountNeededToLevel,
        )
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "reinforceArmor",
            "params": params,
        }

    def produceItem_done(self, params):
        """
        Finalize improving the armor
        """

        # unpack parameters
        character = params["character"]
        improvement = params["improvementAmount"]
        armor = params["armor"]

        # trigger events
        character.changed("improved armor")

        # actually improve the armor
        armor.armorValue += improvement
        character.addMessage(f"You improved the Armor by {improvement!s} to {armor.armorValue}")

    def SetDefaultMaxUpgradeAmount(self, character):
        character.macroState["submenue"] = src.menuFolder.sliderMenu.SliderMenu(
            "set the preferred max amount of defense to upgrade to",
            self.preferredMaxDefense if self.preferredMaxDefense else 3,
            3,
            8,
            D(0.5),
        )
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "SetterDefaultMaxUpgradeAmount",
            "params": {"character": character},
        }

    def SetterDefaultMaxUpgradeAmount(self, params):
        character = params["character"]
        self.preferredMaxDefense = params["value"]

    def getConfigurationOptions(self, character):
        base: dict = super().getConfigurationOptions(character)
        base["s"] = ("set upgrade amount", self.SetDefaultMaxUpgradeAmount)
        return base

src.items.addType(ArmorReinforcer)
