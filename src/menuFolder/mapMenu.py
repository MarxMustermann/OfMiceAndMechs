import src

class MapMenu(src.subMenu.SubMenu):
    """
    a menu for triggering actions from a map
    """

    type = "MapMenu"

    def __init__(self, mapContent=None,functionMap=None, extraText = "", cursor = None):
        """
        initialise internal state

        Parameters:
            mapContent: the content to show
        """

        super().__init__()
        self.mapContent = mapContent
        self.functionMap = functionMap
        self.extraText = extraText
        if cursor:
            self.cursor = (cursor[0],cursor[1],)
        else:
            self.cursor = (7,7)

    def handleKey(self, key, noRender=False, character = None):
        """
        show the map and trigger functions depending on key presses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        closeMenu = False
        mappedFunctions = self.functionMap.get(self.cursor, {})
        if key in mappedFunctions:
            closeMenu = True
            self.callIndirect(mappedFunctions[key]["function"],{"coordinate":self.cursor})

        # exit the submenu
        if key in ("w",) and self.cursor[1] > 1:
            self.cursor = (self.cursor[0],self.cursor[1]-1)
        if key in ("s",) and self.cursor[1] < 13:
            self.cursor = (self.cursor[0],self.cursor[1]+1)
        if key in ("a",) and self.cursor[0] > 1:
            self.cursor = (self.cursor[0]-1,self.cursor[1])
        if key in ("d",) and self.cursor[0] < 13:
            self.cursor = (self.cursor[0]+1,self.cursor[1])

        if closeMenu or key in (
            "esc",
            "enter",
            "space",
            "j",
        ):
            if self.followUp:
                self.followUp()
            return True

        quest = character.getActiveQuest()
        if quest:
            for marker in quest.getQuestMarkersTile(character):
                pos = marker[0]
                display = self.mapContent[pos[1]][pos[0]]

                actionMeta = None
                if isinstance(display,src.interaction.ActionMeta):
                    actionMeta = display
                    display = display.content

                if isinstance(display,int):
                    display = src.canvas.displayChars.indexedMapping[display]
                if isinstance(display,str):
                    display = (src.interaction.urwid.AttrSpec("#fff","black"),display)

                if hasattr(display[0],"fg"):
                    display = (src.interaction.urwid.AttrSpec(display[0].fg,"#555"),display[1])
                elif not isinstance(display[0],tuple):
                    display = (src.interaction.urwid.AttrSpec(display[0].foreground,"#555"),display[1])

                if actionMeta:
                    actionMeta.content = display
                    display = actionMeta

                self.mapContent[pos[1]][pos[0]] = display

        # show rendered map
        mapText = []
        for y in range(15):
            mapText.append([])
            for x in range(15):
                if (x,y) == self.cursor:
                    mapText[-1].append("██")
                else:
                    mapText[-1].append(self.mapContent[y][x])
            mapText[-1].append("\n")

        mapText.append(f"\n press wasd to move cursor {self.cursor}")

        mappedFunctions = self.functionMap.get(self.cursor, {})
        for (key,item) in mappedFunctions.items():
            mapText.append("\n press {} to {}".format(key,item["description"],))

        mapText.append(self.extraText)

        if not noRender:
            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = mapText
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))


        return False
