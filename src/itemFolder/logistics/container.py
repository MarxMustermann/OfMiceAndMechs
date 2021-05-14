import src


class Container(src.items.Item):
    type = "Container"

    def __init__(self):
        super().__init__()

        self.contained = []
        self.display = src.canvas.displayChars.container
        self.name = "container"

        self.charges = 0
        self.maxItems = 10
        self.level = 1

        self.attributesToStore.extend(["charges", "maxCharges", "level"])

    def getLongInfo(self):
        text = """
item: Container

description:
The container is used to carry and store small items.

it holds the items. It can hold a maximum of %s items.

This is a level %s item.

""" % (
            self.maxItems,
            self.level,
        )

        if self.contained:
            for item in self.contained:
                text += """
* %s
%s""" % (
                    item.name,
                    item.description,
                )
        else:
            text += """
the container is empty
"""

        text += """ 

actions:

= load items =
prepare by placing the bloom container on the ground and placing the items to the east of the container.
Activate the bloom container and select the option "load items" to load the blooms into the container.

= unload items =
prepare by placing the container on the ground.
Activate the container and select the option "unload items" to unload the items.
"""
        return text

    def getState(self):
        state = super().getState()
        state["contained"] = []
        for item in self.contained:
            state["contained"].append(item.getState())
        return state

    def setState(self, state):
        super().setState(state)

        if "contained" in state:
            for item in state["contained"]:
                self.contained.append(getItemFromState(item))

    def apply(self, character):
        options = []
        options.append(("load", "load items"))
        options.append(("unload", "unload items"))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    def doSelection(self):
        selection = self.submenue.selection
        if selection == "load":
            if len(self.contained) >= self.maxItems:
                self.character.addMessage("container full. no items loaded")
                return

            items = []
            for item in self.container.getItemByPosition(
                (self.xPosition - 1, self.yPosition)
            ):
                if item.walkable:
                    items.append(item)

            if not items:
                self.character.addMessage("no small items to load")
                return

            for item in items:
                if len(self.contained) >= self.maxItems:
                    self.character.addMessage("container full. not all items loaded")
                    return

                self.contained.append(item)

                self.container.removeItem(item)
                self.charges += 1

            self.character.addMessage("items loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.addMessage("no items to unload")
                return

            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition(
                (self.xPosition + 1, self.yPosition)
            ):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1

            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.addMessage("target area full. no items unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.contained:
                new = self.contained.pop()
                new.xPosition = self.xPosition + 1
                new.yPosition = self.yPosition

                toAdd.append(new)
            self.container.addItems(toAdd)


src.items.addType(Container)
