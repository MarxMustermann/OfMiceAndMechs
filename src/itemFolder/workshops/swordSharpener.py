import random

import src
import src.items


class swordSharpener(src.items.itemMap["WorkShop"]):
    type = "swordSharpener"
    name = "sword Sharpener"
    description = "Use it to upgrade swords"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="SH")
        self.applyOptions.extend([("sharpen sword", "sharpen sword")])
        self.applyMap = {"sharpen sword": self.sharpenSwordHook}

    def sharpenSwordHook(self, character):
        self.sharpenSword({"character": character})

    def sharpenSword(self, params):
        character = params["character"]

        if "choice" not in params:
            options = [("Sharpen Equipped Sword", "Sharpen Equipped Sword"), ("Sharpen Sword", "Sharpen Sword")]
            submenue = src.menuFolder.SelectionMenu.SelectionMenu(
                "Choose item To Sharpen", options, targetParamName="choice"
            )
            submenue.tag = "SwordSharpenerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "sharpenSword", "params": params}
            return
        Grindstone = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["Grindstone"]):
                Grindstone = item
                break

        if Grindstone is None:
            character.addMessage("you don't have Grindstone")
            return

        sword = None
        if params["choice"] == "Sharpen Equipped Sword":
            if character.weapon:
                sword = character.weapon
                if sword.name == "improved sword":
                    character.addMessage("you can't upgrade the sword twice")
                    return
            else:
                character.addMessage("you don't have any sword equipped")
                return
        else:
            for item in character.inventory:
                if isinstance(item, src.items.itemMap["Sword"]) and sword.name != "improved sword":
                    sword = item
                    break
            if sword is None:
                character.addMessage("you don't have any base sword in the inventory")
                return
        params["sword"] = sword
        params["productionTime"] = 100
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse

        character.inventory.remove(Grindstone)

        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]
        improvement_table = [(2, 5), (3, 3), (4, 2), (5, 1)]
        improvement = random.choices([val[0] for val in improvement_table], [val[1] for val in improvement_table])[0]
        character.addMessage(f"You improved the sword by {improvement!s} points")

        sword = params["sword"]
        sword.name = "improved sword"
        sword.baseDamage += improvement


src.items.addType(swordSharpener)
