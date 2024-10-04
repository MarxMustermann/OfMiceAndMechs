import src


class Note(src.items.Item):
    """
    ingame item having no other purpose that to display a text
    """

    type = "Note"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.note)
        self.name = "note"
        self.description = "It has a text written on it"
        self.usageInfo = """
activate the note to read it.
"""

        self.bolted = False
        self.walkable = True
        self.text = ""

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += f"""
it holds the text:

{self.text}
"""
        return text

    def apply(self, character):
        """
        handle a character reading the note

        Parameters:
            character: the character that tries to read the note
        """

        submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(
            f"the note has the text: \n\n\n{self.text}"
        )
        character.macroState["submenue"] = submenue

    def setText(self, text):
        """
        set the notes text

        Parameters:
            text: the text to set
        """

        self.text = text

src.items.addType(Note)
