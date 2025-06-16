import src


class SliderMenu(src.subMenu.SubMenu):
    """
    menu to get a string input from the user
    """

    type = "InputMenu"

    def __init__(
        self,
        query="",
        defaultValue=0,
        minValue=0,
        maxValue=9999,
        stepValue=10,
        targetParamName="value",
        additionalInfoCallBack=None,
    ):
        """
        initialise internal state

        Parameters:
            query: the text to be shown along with the input prompt
            ignoreFirst: flag to ignore first keypress
        """

        self.query = query
        self.value = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.stepValue = stepValue

        super().__init__()
        self.footerText = "press enter to confirm\npress a and d to change the value\npressing A and D will modify the value by " + str(stepValue * 10)
        self.targetParamName = targetParamName
        self.done = False
        self.additionalInfoCallBack = additionalInfoCallBack

    def handleKey(self, key, noRender=False, character=None):
        """
        gather the input keystrokes

        Parameters:
            key: the key pressed
            noRender: a flag to skip rendering
        Returns:
            returns True when done
        """

        if key == "enter":
            if self.followUp:
                self.callIndirect(self.followUp, extraParams={self.targetParamName: self.value})
            self.done = True
            return True

        if key == "~":
            pass
        elif key == "esc":
            self.done = True
            return True
        elif key in ("+", "*"):
            return None
        elif key == "left":
            self.value = max(self.minValue, self.value - 1)
        elif key == "right":
            self.value = min(self.maxValue, self.value + 1)
        elif key == "a":
            self.value = max(self.minValue, self.value - self.stepValue)
        elif key == "d":
            self.value = min(self.maxValue, self.value + self.stepValue)
        elif key == "A":
            self.value = max(self.minValue, self.value - self.stepValue * 10)
        elif key == "D":
            self.value = min(self.maxValue, self.value + self.stepValue * 10)

        percentage = (self.value - self.minValue) / (self.maxValue - self.minValue)
        number_of_bars = 35

        center_len = int(len(self.query) / 2)

        svalue = str(self.value)
        text = (center_len - int(len(svalue) / 2)) * " " + svalue + "\n"
        filled = int(percentage * number_of_bars)
        text += (center_len - int(number_of_bars / 2)) * " " + filled * "║"
        text += (number_of_bars - filled) * "|"
        if not noRender:
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\nvalue input\n\n"))
            src.interaction.footer.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\nvalue input\n\n"))

            additional = self.additionalInfoCallBack(self.value) if self.additionalInfoCallBack else ""
            self.persistentText = (
                src.interaction.urwid.AttrSpec("default", "default"),
                "\n" + self.query + "\n\n" + text + "\n\n" + additional + "\n\n" + self.footerText,
            )

            # show the render
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False
