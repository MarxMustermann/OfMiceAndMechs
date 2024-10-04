import collections

from src.interaction import main, urwid

# bad code: there is redundant code from the specific submenus that should be put here
# bad code: there is spcific code from the selection submenu that should NOT be here


class SubMenu:
    """
    The base class for submenus offering selections
    """

    def __init__(self, default=None, targetParamName="selection"):
        """
        set up basic state

        Parameters:
            default: the default selection
            targetParamName: name of the parameter the selection should be stored in
        """

        self.stealAllKeys = False
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.footerText = "press w / s to move selection up / down, press enter / j / k to select, press esc to exit"
        self.followUp = None
        self.done = False
        self.tag = None
        self.extraInfo ={}

        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        self.default = default
        self.targetParamName = targetParamName
        self.extraDescriptions = {}
        super().__init__()

        self.escape = False

    def rerender(self):
        pass

    def callIndirect(self, callback, extraParams=None):
        """
        call a callback that is stored in a savable format

        Parameters:
            callback: the callback to call
            extraParams: some additional parameters
        """

        if extraParams is None:
            extraParams = {}
        if not isinstance(callback, dict):
            # bad code: direct function calls are deprecated, but not completely removed
            callback()
        else:
            if "container" not in callback:
                return
            container = callback["container"]
            function = getattr(container, callback["method"])

            if "params" in callback:
                callback["params"].update(extraParams)
                function(callback["params"])
            else:
                function()

    def getQuestMarkersTile(self, character):
        return []

    def setOptions(self, query, options):
        """
        set the options to select from

        Parameters:
            query: the text shown for the selection
            options: the options to choose from
        """

        # convert options to ordered dict

        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        counter = 1
        for option in options:
            self.options[str(counter)] = option[0]
            self.niceOptions[str(counter)] = option[1]
            counter += 1

        # set related state
        self.query = query
        self.selectionIndex = 1
        self.lockOptions = True
        self.selection = None
        self.origKey = None

    def getSelection(self):
        """
        get the selected item
        """

        return self.selection

    def handleKey(self, key, noRender=False, character=None):
        """
        show the options and allow the user to select one

        Parameters:
            key: the key pressed
            noRender: flag for skipping the rendering
        Returns:
            returns True when done
        """

        origKey = key

        if not self.options:
            self.done = True
            return True
        if self.done:
            return True

        # exit submenu
        if key == "esc":
            return True

        if key == "a":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            while counter < len(oldOptions):
                self.options[str(counter)] = oldOptions[str(counter + 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter + 1)]
                counter += 1
            self.options[str(counter)] = oldOptions[str(1)]
            self.niceOptions[str(counter)] = oldNiceOptions[str(1)]

        if key == "d":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            self.options[str(counter)] = oldOptions[str(len(oldOptions))]
            self.niceOptions[str(counter)] = oldNiceOptions[str(len(oldOptions))]
            counter = 2
            while counter < len(oldOptions) + 1:
                self.options[str(counter)] = oldOptions[str(counter - 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter - 1)]
                counter += 1

        # show question
        out = ["\n"]
        out.extend([self.query, "\n"])

        # handle the selection of options
        if not self.lockOptions:
            # change the marked option
            if key in (
                "w",
                "up",
            ):
                self.selectionIndex -= 1
                if self.selectionIndex == 0:
                    self.selectionIndex = len(self.options)
            if key in (
                "s",
                "down",
            ):
                self.selectionIndex += 1
                if self.selectionIndex > len(self.options):
                    self.selectionIndex = 1
            # select the marked option
            if key in ["enter", "j", "k", "right"]:
                # bad code: transforming the key to the shortcut is needlessly complicated
                if len(self.options.items()):
                    key = list(self.options.items())[self.selectionIndex - 1][0]
                else:
                    self.selection = None
                    self.done = True
                    return True

            # select option by shortcut
            if key in self.options:
                self.selection = self.options[key]
                self.options = None
                if self.followUp:
                    self.callIndirect(self.followUp,extraParams={self.targetParamName:self.selection,"key":origKey})
                self.origKey = origKey
                return True
        else:
            self.lockOptions = False

        extraDescription = None
        if not noRender:
            # render the options
            counter = 0
            for k, v in self.niceOptions.items():
                counter += 1
                if counter == self.selectionIndex:
                    out.extend([" -> ", v, "\n"])
                    if self.extraDescriptions and self.options[k] in self.extraDescriptions:
                        extraDescription = self.extraDescriptions[self.options[k]]+"\n\n"
                else:
                    out.extend(["    ", v, "\n"])

            if extraDescription:
                out += extraDescription

            # show the rendered options
            # bad code: urwid specific code
            if main:
                main.set_text(
                    (
                        urwid.AttrSpec("default", "default"),
                        [self.persistentText , "\n\n" , out],
                    )
                )

        return False

    # bad code: should either be used everywhere or be removed
    # bad code: urwid specific code
    def set_text(self, text):
        """
        set text in urwid

        Parameters:
            text: the text to set
        """

        main.set_text((urwid.AttrSpec("default", "default"), text))
