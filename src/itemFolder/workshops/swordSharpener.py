import random

import src

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

    def sharpenSwordHook(self, character):
        self.sharpenSword({"character": character})

    def sharpenSword(self, params):
        character = params["character"]

        if "choice" not in params:
            options = [("Sharpen Equipped Sword", "Sharpen Equipped Sword"), ("Sharpen Sword", "Sharpen Sword")]
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                "Choose item To Sharpen", options, targetParamName="choice"
            )
            submenue.tag = "SwordSharpenerSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container": self, "method": "sharpenSword", "params": params}
            return

        grindstones = []
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["Grindstone"]):
               continue 
            grindstones.append(item)

        if not grindstones:
            character.addMessage("you don't have Grindstone, you only can improve your sword to 15")

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

        improvementAmount = 0
        grindstone_consumed = 0
        if sword.baseDamage < 15:
            improvementAmount += 15-sword.baseDamage

        elif sword.baseDamage == 30:
            character.addMessage("you can't further improve the sword")
            return

        while grindstone_consumed <= len(grindstones):
            current_damage_output = sword.baseDamage + improvementAmount
            if current_damage_output < 25:
                improvementAmount += 1
                grindstone_consumed += 1
            elif current_damage_output < 30:
                grindStone_amount_needed = (current_damage_output - 24) * 3
                if len(grindstones) - grindstone_consumed - grindStone_amount_needed >= 0:
                    grindstone_consumed += grindStone_amount_needed
                    improvementAmount += 1
                else:
                    break
            else:
                break

        if grindstone_consumed:
            for grindStone in grindstones[:grindstone_consumed]:
                character.inventory.remove(grindStone)

        if not improvementAmount:
            character.addMessage("you can't improve your sword")
            character.changed("sharpened sword")
            return

        params["sword"] = sword
        params["productionTime"] = 20*improvementAmount
        params["doneProductionTime"] = 0
        params["improvementAmount"] = improvementAmount
        params["cost"] = grindstone_consumed
        params["hitCounter"] = character.numAttackedWithoutResponse


        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]
        improvement = params["improvementAmount"]
        character.changed("sharpened sword")

        sword = params["sword"]
        sword.baseDamage += improvement

        cost = params["cost"]

        character.addMessage(f"You improved the sword by {improvement!s} to {sword.baseDamage}")
        character.addMessage(f"it costed {cost} grindstone to improve the sword")
        if sword.baseDamage < 30:
            if sword.baseDamage < 25:
                amount_to_next_level = 1
            else:
                amount_to_next_level = (sword.baseDamage - 24) * 3
            character.addMessage(f"you will need {amount_to_next_level} grindstone to improve the sword again")

src.items.addType(SwordSharpener)
