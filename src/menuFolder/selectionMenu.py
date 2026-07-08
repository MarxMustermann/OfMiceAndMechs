import src

# bad code: this does nothing the Submenu doesn't do
class SelectionMenu(src.menues.SubMenu):
    '''
    does a simple selection and terminates
    Parameters:
        text: the text to show next to the selection
        options: the options to select from
        default: the default value
        targetParamName: name of the parameter the selection should be stored in
    '''
    def __init__(self, text="", options=None, default=None, targetParamName="selection",extraDescriptions=None, selected=None, tag=None, title=None):
        if not options:
            options = []

        self.type = "SelectionMenu"
        super().__init__(default=default,targetParamName=targetParamName,tag=tag)
        self.setOptions(text, options)

        if selected:
            counter = 0
            for option in options:
                counter += 1
                if option[0] == selected:
                    self.selectionIndex = counter

        self.extraDescriptions = extraDescriptions

        self.title = title

    def getTitle(self):
        return self.title

    def handleKey(self, key, noRender=False, character = None):
        '''
        handles a keypress

        Parameters:
            key: the key pressed
            noRender: flag for skipping rendering
        Returns:
            returns True when done
        '''

        # exit submenu
        if key == "esc":
            self.selection = None
            if self.followUp:
                self.callIndirect(self.followUp,extraParams={self.targetParamName:None})
            return True
        if key == ".":
            if character:
                character.takeTime(amount=1,reason="waiting")
            return False
        if not noRender and src.interaction.header:
            src.interaction.header.set_text("")

        # let superclass handle the actual selection
        if not self.getSelection():
            super().handleKey(key, noRender=noRender, character=character)

        # stop when done
        return bool(self.getSelection())

    def get_command_to_select_option(self,option_to_select,selectionCommand="j"):
        """
        generate the command to select a menu entry
        """
        command = ""
        target_index = None
        counter = 0
        for option in self.options.values():
            counter += 1
            if option == option_to_select:
                target_index = counter
        if not target_index is None:
            return "s"*(target_index-self.selectionIndex)+"w"*(self.selectionIndex-target_index)+selectionCommand
        return None

    def render(self):
        result = []
        result.append(super().render())
        result.append((src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"\npress w/s to move cursor\npress j/k/enter to select option\npress esc to close menu\npress a/d to shift options"))
        return result
