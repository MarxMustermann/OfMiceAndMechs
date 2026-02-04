import src

class OneKeystrokeMenu(src.subMenu.SubMenu):
    '''
    a menu getting a single keystroke from the character
    Parameters:
        text: the text to show
    '''
    type = "OneKeystrokeMenu"
    def __init__(self, text="",targetParamName="keyPressed",ignoreFirstKey=True,do_not_scale=False):
        super().__init__()
        self.text = text
        self.firstRun = True
        if not ignoreFirstKey:
            self.firstRun = False
        self.keyPressed = ""
        self.done = False
        self.targetParamName = targetParamName
        self.counter = 0
        self.rerenderFunction = None
        self.do_not_scale = do_not_scale

    def rerender(self):
        '''
        show the last state again
        '''
        if self.rerenderFunction:
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.rerenderFunction()))

    def handleKey(self, key, noRender=False, character = None):
        '''
        show the text and quit on second keypress

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        '''

        # exit the submenu
        if key not in ("~",) and not self.firstRun:
            self.keyPressed = key
            if self.followUp:
                self.callIndirect(self.followUp,{self.targetParamName:key})
            self.done = True
            return True

        # mark that the menu was shown once
        self.firstRun = False
        return False

    def render(self):
        out = []
        out.append(self.text)
        out.append("\n")
        return out

