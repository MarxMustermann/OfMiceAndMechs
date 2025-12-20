import src


class WorkShop(src.items.Item):
    type = "WorkShop"
    name = "WorkShop"

    def getConfigurationOptions(self, character):
        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

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
                    character.removeItemFromInventory(current_item)
                else:
                    self.container.removeItem(current_item)

        return True


src.items.addType(WorkShop)
