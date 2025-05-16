import src


class KnowledgeBase(src.items.Item):
    type = "KnowledgeBase"

    def __init__(self):
        super().__init__(display="KB")

        self.name = "knowledge base"

    def apply(self, character):
        self.show_info(character)

    def configure(self, character):
        self.show_info(character)

    def show_info(self, character):

        text = ""

        for (itemType,itemClass) in src.items.itemMap.items():
            text += f"{itemType}:\n{itemClass.description}\n\n"
            print(itemType)
            print(itemClass.description)

        character.showTextMenu(text)

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
""" % (
            self.charges
        )


src.items.addType(KnowledgeBase)
