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
            submenue = src.menuFolder.SelectionMenu.SelectionMenu(
                "Choose item To Reinforce", options, targetParamName="choice"
            )
            submenue.tag = "ArmorReinforceerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "ReinforceArmor", "params": params}
            return

        citinPlates = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["CitinPlates"]):
                citinPlates = item
                break

        if citinPlates is None:
            character.addMessage("you don't have Citin Plates")
            return

        armor = None
        if params["choice"] == "Reinforce Equipped Armor":
            if character.armor:
                armor = character.armor
                if armor.name == "improved Armor":
                    character.addMessage("you can't upgrade the Armor twice")
                    return
            else:
                character.addMessage("you don't have any Armor equipped")
                return
        else:
            for item in character.inventory:
                if isinstance(item, src.items.itemMap["Armor"]) and armor.name != "improved Armor":
                    armor = item
                    break
            if armor is None:
                character.addMessage("you don't have any base Armor in the inventory")
                return

        params["Armor"] = armor
        params["productionTime"] = 100
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse

        character.inventory.remove(CitinPlates)

        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]
        improvement_table = [(2, 5), (3, 3), (4, 2), (5, 1)]
        improvement = random.choices([val[0] for val in improvement_table], [val[1] for val in improvement_table])[0]
        character.addMessage(f"You improved the Armor by {improvement!s} points")

        armor = params["Armor"]
        armor.name = "improved Armor"
        armor.armorValue += improvement


src.items.addType(ArmorReinforcer)
