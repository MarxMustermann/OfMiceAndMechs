import src


class WorkShop(src.items.Item):
    type = "WorkShop"
    name = "WorkShop"

    def produceItem_wait(self, params):
        character = params["character"]

        if not "hitCounter" in params:
            params["hitCounter"] = character.numAttackedWithoutResponse

        if params["hitCounter"] != character.numAttackedWithoutResponse:
            character.addMessage("You got hit while working")
            return
        ticksLeft = params["productionTime"] - params["doneProductionTime"]
        character.takeTime(1,"produced")
        params["doneProductionTime"] += 1

        barLength = params["productionTime"]//10
        if params["productionTime"]%10:
            barLength += 1
        baseProgressbar = "X"*(params["doneProductionTime"]//10)+"."*(barLength-(params["doneProductionTime"]//10))
        progressBar = ""
        while len(baseProgressbar) > 10:
            progressBar += baseProgressbar[:10]+"\n"
            baseProgressbar = baseProgressbar[10:]
        progressBar += baseProgressbar

        submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(progressBar, targetParamName="abortKey")
        submenue.tag = "metalWorkingProductWait"
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "produceItem_done" if ticksLeft <= 0 else "produceItem_wait",
            "params": params,
        }
        character.runCommandString(".", nativeKey=True)
        if ticksLeft % 10 != 9 and src.gamestate.gamestate.mainChar == character:
            src.interaction.skipNextRender = True


    def getConfigurationOptions(self, character):
        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self, character):
        self.bolted = True
        character.addMessage("you bolt down the " + self.name)
        character.changed("boltedItem", {"character": character, "item": self})
        if hasattr(self,"numUsed"):
            self.numUsed = 0

    def unboltAction(self, character):
        self.bolted = False
        character.addMessage("you unbolt the " + self.name)
        character.changed("unboltedItem", {"character": character, "item": self})
        if hasattr(self,"numUsed"):
            self.numUsed = 0

    def getInputItems(self):
        result = []

        for offset in [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition + offset[2])
            ):
                if item.bolted:
                    continue
                result.append(item)
        return result

    def wantItemTypeWithAmount(self, character, ItemTypeAmount):
        items_available = self.getInputItems()

        if character:
            items_available.extend(character.inventory)

        items_available = list(
            set(items_available)
        )  # HACK it may be needed if some getInputItems implementation already provide char inventory

        neededItemCount = {}
        for item in items_available:
            if item.type in ItemTypeAmount:
                if item.type not in neededItemCount:
                    neededItemCount[item.type] = []
                neededItemCount[item.type].append(item)

        missing_items = False
        for itemType in ItemTypeAmount:
            if itemType not in neededItemCount or not (ItemTypeAmount[itemType] <= len(neededItemCount[itemType])):
                name = src.items.itemMap[itemType]().name
                character.addMessage(
                    f'missing {ItemTypeAmount[itemType]-len(neededItemCount.get(itemType,[]))} of item "{name}" '
                )
                missing_items = True

        if missing_items:
            return False

        for itemType in ItemTypeAmount:
            for i in range(ItemTypeAmount[itemType]):
                current_item = neededItemCount[itemType][i]
                if current_item in character.inventory:
                    character.inventory.remove(current_item)
                else:
                    self.container.removeItem(current_item)

        return True


src.items.addType(WorkShop)
