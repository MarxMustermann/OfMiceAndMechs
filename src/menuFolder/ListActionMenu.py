import collections

import SubMenu

from src.interaction import commandChars, header, main, urwid


# bad code: this does nothing the Submenu doesn't do
class ListActionMenu(SubMenu):
    """
    does a simple selection and terminates
    """

    def __init__(self, options, actions, text="", default=None, targetParamName="selection"):
        """
        set up the selection

        Parameters:
            text: the text to show next to the selection
            options: the options to select from
            default: the default value
            targetParamName: name of the parameter the selection should be stored in
        """

        self.type = "ListActionMenu"
        super().__init__(default=default,targetParamName=targetParamName)
        self.setOptions(text, options)
        self.actions = actions

    def handleKey(self, key, noRender=False, character = None):
        """
        handles a keypress

        Parameters:
            key: the key pressed
            noRender: flag for skipping rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            self.selection = None
            if self.followUp:
                self.callIndirect(self.followUp)
            return True
        if not noRender:
            header.set_text("")

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

        if key in (commandChars.autoAdvance, commandChars.advance):
            if self.default is not None:
                self.selection = self.default
            else:
                self.selection = list(self.options.values())[0]
            self.options = None
            if self.followUp:
                self.followUp()
            return True

        # show question
        out = "\n"
        out += self.query + "\n"

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
            key = "default"

        if key in self.actions:
            option = list(self.options.items())[self.selectionIndex - 1][1]
            callback = self.actions[key]["callback"]
            if not callback.get("params"):
                callback["params"] = {}
            self.callIndirect(callback,extraParams={self.targetParamName:option})
            return True

        if not noRender:
            # render the options
            counter = 0
            for k, v in self.niceOptions.items():
                counter += 1
                if counter == self.selectionIndex:
                    out += str(k) + " ->" + str(v) + "\n"
                else:
                    out += str(k) + " - " + str(v) + "\n"

            # show the rendered options
            # bad code: urwid specific code
            main.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    self.persistentText + "\n\n" + out,
                )
            )

        return False
