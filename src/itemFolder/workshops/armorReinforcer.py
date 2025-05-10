import random

import src

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

        # calculate how much to improve the armor by
        improvementAmount = 0
        if armor.armorValue < 3:
            improvementAmount += 3-armor.armorValue
        for chitinPlate in chitinPlates:
            if improvementAmount+armor.armorValue >= 8:
                break
            character.inventory.remove(chitinPlate)
            improvementAmount += min(0.5,8-armor.armorValue-improvementAmount)
        if not improvementAmount:
            character.changed("improved armor")
            character.addMessage("you can't improve your armor")
            return

        # trigger a waiting period before completing upgrading the armor
        params["Armor"] = armor
        params["productionTime"] = int(100*improvementAmount)+1
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        params["improvementAmount"] = improvementAmount
        self.produceItem_wait(params)

    def produceItem_done(self, params):
        """
        Finalize improving the armor
        """

        # unpack parameters
        character = params["character"]
        improvement = params["improvementAmount"]
        armor = params["Armor"]

        # trigger events
        character.changed("improved armor")

        # actually improve the armor
        armor.armorValue += improvement
        character.addMessage(f"You improved the Armor by {improvement!s} to {armor.armorValue}")


src.items.addType(ArmorReinforcer)
