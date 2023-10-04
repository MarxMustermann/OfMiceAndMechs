class AttrSpec:
    """
    dummy object behaving like an urwid attribute
    this is used to prevent crashes
    """

    def __init__(self, fg, bg):
        """
        store basic attributes

        Parameters:
            fg: foreground color
            bg: background color
        """

        self.fg = fg
        self.bg = bg

    def get_rgb_values(self):
        def convertValue(value):
            if value == "a":
                return 10*16
            elif value == "b":
                return 11*16
            elif value == "c":
                return 12*16
            elif value == "d":
                return 13*16
            elif value == "e":
                return 14*16
            elif value == "f":
                return 15*16
            else:
                return int(value)*16

        color = []
        if self.fg[0] == "#":
            color.append(convertValue(self.fg[1]))
            color.append(convertValue(self.fg[2]))
            color.append(convertValue(self.fg[3]))
        elif self.fg in "black":
            color.append(0)
            color.append(0)
            color.append(0)
        elif self.fg in ("white","default"):
            color.append(255)
            color.append(255)
            color.append(255)
        else:
            color.append(None)
            color.append(None)
            color.append(None)
        if self.bg[0] == "#":
            color.append(convertValue(self.bg[1]))
            color.append(convertValue(self.bg[2]))
            color.append(convertValue(self.bg[3]))
        elif self.bg in ("black","default",""):
            color.append(0)
            color.append(0)
            color.append(0)
        else:
            color.append(None)
            color.append(None)
            color.append(None)
        return tuple(color)
