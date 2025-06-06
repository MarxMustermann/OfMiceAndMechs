import src

class JobAsMatrixMenu(src.subMenu.SubMenu):
    type = "JobAsMatrixMenu"

    def __init__(self,dutyArtwork):
        super().__init__()
        self.dutyArtwork = dutyArtwork
        self.index = [0,0]

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        terrain = self.dutyArtwork.getTerrain()
        npcs = []
        for char in terrain.characters:
            if char.burnedIn:
                continue
            if char not in npcs:
                npcs.append(char)
        for room in terrain.rooms:
            for char in room.characters:
                if char.burnedIn:
                    continue
                if char not in npcs:
                    npcs.append(char)
        if src.gamestate.gamestate.mainChar in npcs:
            npcs.remove(src.gamestate.gamestate.mainChar)

        duties = list(reversed(["manufacturing","epoch questing","scavenging","machine operation","clone spawning","city planning","cleaning","painting","maggot gathering","machine placing","room building","machining","metal working","hauling","resource fetching","scrap hammering","resource gathering","questing","flask filling","praying","mold farming"]))


        if key == "C":
            for npc in npcs:
                npc.duties = []
        if key in ("w","up") and not self.index[0] < 1:
            self.index[0] -= 1
        if key in ("s","down"):
            self.index[0] += 1
        if key in ("a","left") and not self.index[1] < 1:
            self.index[1] -= 1
        if key in ("d","right") and not self.index[1] > len(duties)-2:
            self.index[1] += 1
        if key in ("j","k","l","c"):
            rowCounter = 0
            for npc in npcs:
                if npc.faction != character.faction:
                    continue
                if isinstance(npc,src.characters.characterMap["Ghoul"]):
                    continue

                if rowCounter == self.index[0]:
                    dutyname = duties[self.index[1]]

                    if key == "l":
                        pass
                    elif key == "j":
                        if dutyname not in npc.duties:
                            npc.duties.append(dutyname)
                            npc.dutyPriorities[dutyname] = 1
                        else:
                            if dutyname not in npc.dutyPriorities:
                                npc.dutyPriorities[dutyname] = 1
                            npc.dutyPriorities[dutyname] += 1
                    elif key == "k":
                        if dutyname in npc.duties:
                            if dutyname not in npc.dutyPriorities:
                                npc.dutyPriorities[dutyname] = 1
                            npc.dutyPriorities[dutyname] -= 1
                            if npc.dutyPriorities[dutyname] < 1:
                                del npc.dutyPriorities[dutyname]
                                npc.duties.remove(dutyname)
                    elif key == "c":
                        npc.duties = []
                        npc.dutyPriorities = {}

                rowCounter += 1

        text = "press wasd to move cursor"
        text += "press j to enable/disable"

        text = [text]

        text.append("\ncharacter                 ")
        rowCounter = 0
        dutyCounter = 0
        for duty in duties:
            color = "default"
            if rowCounter == self.index[1]:
                color = "#555"
            text.append("|")
            text.append((src.interaction.urwid.AttrSpec("default", color)," "+duty+" "))
            rowCounter += 1
            dutyCounter += 1
            if dutyCounter == 6:
                text.append("\n                          ")
                dutyCounter = 0


        def convertName(name):
            return name.ljust(25," ")[0:24]


        lineCounter = 0
        color = "default"
        rowCounter = 0
        if lineCounter == self.index[0]:
            color = "#333"

        lineCounter = 0
        for npc in npcs:
            if npc.faction != character.faction:
                continue
            if isinstance(npc,src.characters.characterMap["Ghoul"]):
                continue
            text.append("\n")
            if lineCounter == self.index[0]:
                color = "#333"
            else:
                color = "default"
            text.append((src.interaction.urwid.AttrSpec("default", color),f"{convertName(npc.name)}: "))
            rowCounter = 0
            for duty in duties:
                if lineCounter == self.index[0] and rowCounter == self.index[1]:
                    text.append("=>")
                else:
                    color = "default"
                    if rowCounter == self.index[1] or lineCounter == self.index[0]:
                        color = "#333"
                    text.append((src.interaction.urwid.AttrSpec("default", color),"  "))

                if duty in npc.duties:
                    text.append(str(npc.dutyPriorities.get(duty,1)))
                else:
                    color = "default"
                    if rowCounter == self.index[1] or lineCounter == self.index[0]:
                        color = "#333"
                    text.append((src.interaction.urwid.AttrSpec("default", color)," "))
                text.append("|")
                rowCounter += 1
            lineCounter += 1

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False
