import src


class KnowledgeBase(src.items.Item):
    type = "KnowledgeBase"

    def __init__(self):
        super().__init__(display="KB")

        self.name = "knowledge base"

    def apply(self, character):
        self.show_info({"character":character,"search_term":""})

    def show_info(self, params):

        character = params["character"]
        search_term = params["search_term"]

        key_pressed = params.get("keyPressed")
        if key_pressed:
            if key_pressed in ("ENTER","esc","rESC","lESC",):
                return
            if key_pressed == "backspace":
                if len(search_term) > 0:
                    search_term = search_term[:-1]
            else:
                search_term += params.get("keyPressed")

        text = f"search for: {search_term}\n\nresults:\n\n"

        for (itemType,itemClass) in src.items.itemMap.items():
            itemText = f"{itemType}:\n{itemClass.description}\n\n"
            if search_term.lower() in itemText.lower():
                text += itemText

        params["search_term"] = search_term

        submenu = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(text)
        submenu.followUp = {"container":self,"method":"show_info","params":params}
        character.macroState["submenue"] = submenu

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the KnowledgeBase")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the KnowledgeBase")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
""" % (
            self.charges
        )

src.items.addType(KnowledgeBase)
