import random

import src
from decimal import Decimal as D

class ArmorReinforcer(src.items.itemMap["WorkShop"]):
    '''
    ingame item to uprage armor

    Parameters:
        display: the icon for this item
    '''
    type = "ArmorReinforcer"
    name = "armor Reinforcer"
    description = "Use it to upgrade Armor"
    walkable = False
    bolted = True
    def __init__(self):
        super().__init__(display="AR")

        # configure interaction menu
        self.applyOptions.extend([
                                    ("reinforce equipped armor", "reinforce equipped armor"),
                                    ("reinforce inventory armor", "reinforce armor from inventory"),
                                ])
        self.applyMap = {
                                    "reinforce equipped armor": self.reinforceEquippedArmorHook,
                                    "reinforce inventory armor": self.reinforceInventoryArmorHook,
                }
        self.preferredMaxDefense = None

    def amountNeededForOneUpgrade(self, current_defense_output):
        '''
        calculate the cost for doing one upgrade
        '''

        # enforce bounds
        if current_defense_output > D("8"):
            return None

        # handle free upgrades
        if current_defense_output < D("3"):
            return 0

        # calculate the actual cost
        amount_ChitinPlates_needed_for_upgrade = 1
        if current_defense_output >= D("4"):
            amount_ChitinPlates_needed_for_upgrade += 1
        if current_defense_output >= D("5"):
            amount_ChitinPlates_needed_for_upgrade += 1
        if current_defense_output >= D("6"):
            amount_ChitinPlates_needed_for_upgrade += 1
        if current_defense_output >= D("7"):
            amount_ChitinPlates_needed_for_upgrade += 1

        # return the calculated cost
        return amount_ChitinPlates_needed_for_upgrade

    def reinforceEquippedArmorHook(self, character):
        """
        indirection to call the actual function
        """
        self.reinforceArmor({"character": character, "choice": "reinforce equipped armor"})

    def reinforceInventoryArmorHook(self, character):
        """
        indirection to call the actual function
        """
        self.reinforceArmor({"character": character, "choice": "reinforce inventory armor"})

    def reinforceArmorHook(self, character):
        """
        indirection to call the actual function
        """
        self.reinforceArmor({"character": character})

    def getAvailableChitinPlates(self,character):
        if not self.bolted:
            return []

        chitinPlates = []
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["ChitinPlates"]):
                continue
            chitinPlates.append(item)

        offsets = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0)]
        for offset in offsets:
            for item in self.container.getItemByPosition(self.getPosition(offset=offset)):
                if not isinstance(item, src.items.itemMap["ChitinPlates"]):
                    continue
                chitinPlates.append(item)

        return chitinPlates

    def reinforceArmor(self, params):
        """
        start upgrading the armor
        """

        # unpack the parameters
        character = params["character"]

        # get user input on what armor to upgrade
        if "choice" not in params:
            options = [("reinforce equipped armor", "reinforce equipped armor"), ("reinforce inventory armor", "reinforce armor from inventory")]
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                "Choose item To Reinforce", options, targetParamName="choice"
            )
            submenue.tag = "ArmorReinforceerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "reinforceArmor", "params": params}
            return

        # get user input on how much to upgrade the armor to upgrade
        if "amount" not in params:

            # get available chitin plates

            # show warning message when upgrade items are missing
            chitinPlates = self.getAvailableChitinPlates(character)
            if not chitinPlates:
                character.addMessage("you don't have ChitinPlates, you need ChitinPlates to upgrade your Armor up to more than 3")

            # get the armor to upgrade
            armor = None
            if params["choice"] == "reinforce equipped armor":
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

            # assume free upgrades are desired
            improvementAmount = 0
            if D(armor.armorValue) < D("3"):
                improvementAmount = D("3") - D(armor.armorValue)

            # abort and notify user if all upgrades are too expensive
            if D(armor.armorValue) >= D("8"):
                text = "you can't improve the armor further."
                submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text)
                character.macroState["submenue"] = submenue
                return

            # abort and notify the user if no ugrade can be afforded
            next_upgrade_level = D(armor.armorValue) + D("0.5")
            amount_ChitinPlates_needed_for_upgrade = self.amountNeededForOneUpgrade(next_upgrade_level)
            if amount_ChitinPlates_needed_for_upgrade > len(chitinPlates):
                text = f"you can't improve your armor.\nYou need {amount_ChitinPlates_needed_for_upgrade} ChitinPlates to upgrade your armor."
                submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text)
                character.macroState["submenue"] = submenue
                return

            # define callback to show total costs
            def amountNeededToLevel(level, allowed=None):
                '''
                callback returning the a text describing the cost to upgrade to a certain level
                '''
                chitinPlates_consumed = 0
                base = D(armor.armorValue)
                if base == level and not allowed:
                    return "the armor won't be upgraded"

                while base < level:
                    chitinPlates_consumed += self.amountNeededForOneUpgrade(base)
                    base += D("0.5")

                available = chitinPlates_consumed <= len(chitinPlates)

                if allowed:
                    return available

                if available:
                    return f"You will use {chitinPlates_consumed} ChitinPlates"
                else:
                    return f"You will need {chitinPlates_consumed} ChitinPlates to be able to upgrade"

            # DELETEME: backward compability
            try:
                self.preferredMaxDefense
            except:
                self.preferredMaxDefense = 6

            # calculate a reasonable default amount to upgrade
            defaultValue = armor.armorValue
            available_chitinPlates = len(chitinPlates)
            while 1:
                cost = self.amountNeededForOneUpgrade(defaultValue)
                if cost is None:
                    break
                if cost > available_chitinPlates:
                    break
                if self.preferredMaxDefense and defaultValue >= self.preferredMaxDefense:
                    break
                available_chitinPlates -= cost
                defaultValue += 0.5

            # spawn a slider to allow the user to select the amount to upgrade
            params["armor"] = armor
            params["chitinPlates"] = chitinPlates
            submenue = src.menuFolder.sliderMenu.SliderMenu(
                "choose the armor level to upgrade to",
                defaultValue=defaultValue,
                minValue=D(armor.armorValue),
                maxValue=D(8),
                stepValue=D(0.5),
                bigStepValue=D(1.0),
                targetParamName="amount",
                additionalInfoCallBack=amountNeededToLevel,
            )
            character.macroState["submenue"] = submenue
            submenue.tag = "ArmorReinforcerSlider"
            submenue.followUp = {
                "container": self,
                "method": "reinforceArmor",
                "params": params,
            }
            return

        # do nothing if no action was chosen
        chosenDefenseValue = params["amount"]
        armorOriginalDamage = params["armor"].armorValue
        if chosenDefenseValue == armorOriginalDamage:
            return

        # calculate the cost for the upgrade
        chitinPlates_consumed = 0
        base = D(params["armor"].armorValue)
        while base < chosenDefenseValue:
            chitinPlates_consumed += self.amountNeededForOneUpgrade(base)
            base += D("0.5")

        # remove the resources to pay for the upgrade
        chitinPlates = params["chitinPlates"]
        if chitinPlates_consumed:
            for chitinPlate in chitinPlates[:chitinPlates_consumed]:
                if chitinPlate in character.inventory:
                    character.removeItemFromInventory(chitinPlate)
                else:
                    self.container.removeItem(chitinPlate)

        # trigger the actual productions process
        improvementAmount = chosenDefenseValue - armorOriginalDamage
        params["delayTime"] = 20 * improvementAmount * 2
        params["improvementAmount"] = improvementAmount
        params["cost"] = chitinPlates_consumed
        params["action"]= "output_produced_item"
        self.delayedAction(params)

    def output_produced_item(self,params):
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

    def setDefaultMaxUpgradeAmount(self, character):
        """
        spawns the UI for setting the max upgrade amount
        """

        character.macroState["submenue"] = src.menuFolder.sliderMenu.SliderMenu(
            "set the preferred max amount of defense to upgrade to",
            self.preferredMaxDefense if self.preferredMaxDefense else 3,
            3,
            8,
            D(0.5),
        )
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "setterDefaultMaxUpgradeAmount",
            "params": {"character": character},
        }

    def setterDefaultMaxUpgradeAmount(self, params):
        """
        actually sets the max upgrade amount
        """
        character = params["character"]
        self.preferredMaxDefense = params["value"]

    def getConfigurationOptions(self, character):
        """
        offer options for complex actions
        """
        base: dict = super().getConfigurationOptions(character)
        base["s"] = ("set upgrade amount", self.setDefaultMaxUpgradeAmount)
        return base

    def readyToBeUsedByCharacter(self,character,extraIncrease=1):
        armor = character.armor
        if not isinstance(armor,src.items.itemMap["Armor"]):
            return False
        target_value = armor.armorValue+0.5
        amountNeeded = self.amountNeededForOneUpgrade(target_value)

        if amountNeeded is None:
            return False

        if amountNeeded <= len(self.getAvailableChitinPlates(character)):
            return True

        return False


# register the item
src.items.addType(ArmorReinforcer)
