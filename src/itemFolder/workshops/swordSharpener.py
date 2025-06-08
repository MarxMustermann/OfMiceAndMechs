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

        # unnpack paramters
        character = params["character"]

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

        # calculate how much improvement can be done using grindstones
        grindstone_consumed = 0
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

        # abort and notify user if sword can't be improved
        if not improvementAmount:
            character.addMessage("you can't improve your sword. You need more Grindstone")
            character.changed("sharpened sword")
            return

        # remove/destroy grindstones used to upgrade sword
        if grindstone_consumed:
            for grindStone in grindstones[:grindstone_consumed]:
                character.inventory.remove(grindStone)

        # trigger the actual productions process
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
