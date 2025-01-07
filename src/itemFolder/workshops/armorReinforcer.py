import random

import src

class ArmorReinforcer(src.items.itemMap["WorkShop"]):
    type = "ArmorReinforcer"
    name = "armor Reinforcer"
    description = "Use it to upgrade armors"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="AR")
        self.applyOptions.extend([("Reinforce armor", "Reinforce armor")])
        self.applyMap = {"Reinforce armor": self.reinforceArmorHook}

    def reinforceArmorHook(self, character):
        self.reinforceArmor({"character": character})

    def reinforceArmor(self, params):
        character = params["character"]

        if "choice" not in params:
            options = [("Reinforce Equipped Armor", "Reinforce Equipped Armor"), ("Reinforce Armor", "Reinforce Armor")]
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                "Choose item To Reinforce", options, targetParamName="choice"
            )
            submenue.tag = "ArmorReinforceerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "reinforceArmor", "params": params}
            return

        chitinPlates = []
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["ChitinPlates"]):
                continue
            chitinPlates.append(item)

        if not chitinPlates:
            character.addMessage("you don't have Citin Plates, you only can improve your armor to 3")

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
                character.addMessage("you don't have any base Armor in the inventory")
                return

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

        params["Armor"] = armor
        params["productionTime"] = int(100*improvementAmount)+1
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        params["improvementAmount"] = improvementAmount

        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]
        improvement = params["improvementAmount"]

        character.changed("improved armor")

        armor = params["Armor"]
        armor.armorValue += improvement

        character.addMessage(f"You improved the Armor by {improvement!s} to {armor.armorValue}")


src.items.addType(ArmorReinforcer)
