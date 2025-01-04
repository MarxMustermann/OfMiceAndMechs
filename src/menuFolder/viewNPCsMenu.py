import src

class ViewNPCsMenu(src.subMenu.SubMenu):
    type = "ViewNPCsMenu"

    def __init__(self,personnelArtwork):
        super().__init__()
        self.index = 0
        self.personnelArtwork = personnelArtwork
        self.lastSelectedCharacter = None

    def handleKey(self, key, noRender=False, character = None):

        # exit the submenu
        if key in ("esc"," ",):
            return True

        self.persistentText = ["press w/a and s/d to scroll\n\n"]
        self.persistentText = ["press . to pass a turn\n\n"]
        self.persistentText = ["press t to take over clone\n\n"]
        self.persistentText = ["press r to reset clone quests\n\n"]

        terrain = character.getTerrain()
        characters = terrain.characters[:]
        for room in terrain.rooms:
            characters.extend(room.characters)
        for otherChar in characters[:]:
            if otherChar.faction == character.faction:
                continue
            characters.remove(otherChar)

        if not characters:
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), "no personnel found"))
            return None

        if key in (".",):
            character.timeTaken += 1

        if key in ("w","a","up","left"):
            if self.index > 0:
                self.index -= 1
            else:
                self.index = len(characters)-1
            self.lastSelectedCharacter = None

        if key in ("s","d","down","right"):
            if self.index < len(characters)-1:
                self.index += 1
            else:
                self.index = 0
            self.lastSelectedCharacter = None

        self.persistentText.append(f"{self.index+1} of {len(characters)}\n\n")

        if self.lastSelectedCharacter:
            counter = 0
            for char in characters:
                if char == self.lastSelectedCharacter:
                    self.index = counter
                    break
                counter += 1

        selectedCharacter = characters[self.index]
        self.lastSelectedCharacter = selectedCharacter

        if key in ("t",):
            src.gamestate.gamestate.mainChar = selectedCharacter
        if key in ("r",):
            for quest in selectedCharacter.quests:
                quest.fail()

            containerQuest = src.quests.questMap["BeUsefull"]()
            selectedCharacter.quests.append(containerQuest)
            containerQuest.assignToCharacter(selectedCharacter)
            containerQuest.activate()
            containerQuest.autoSolve = True

            selectedCharacter.timeTaken = 0

        self.persistentText.append("\nname: {} (marked by {})".format(selectedCharacter.name,"XX"))
        part1 = f"position: {selectedCharacter.getPosition()} "
        part2 = f"big position: {selectedCharacter.getBigPosition()} "
        self.persistentText.append(f"\n{part1}{part2}")

        self.persistentText.append(" "*40+"\n")
        self.persistentText.append("\n")
        if selectedCharacter.container.isRoom:
            pos = selectedCharacter.getBigPosition()
            smallPos = selectedCharacter.getPosition()
            rawRender = selectedCharacter.container.render()
            terrain = selectedCharacter.getTerrain()
            miniMapRender = terrain.renderTiles()

            y = 0
            self.persistentText.append("\n")
            while y < 15:
                if y == 0 or y == 14:
                    self.persistentText.append("  "*15)
                else:
                    x = 0
                    self.persistentText.append("  ")
                    for entry in rawRender[y-1]:
                        if (x,y-1,0) == smallPos:
                            self.persistentText.append("XX")
                        else:
                            self.persistentText.append(entry)
                        x += 1
                    self.persistentText.append("  ")
                self.persistentText.append("  |  ")
                x = 0
                for entry in miniMapRender[y]:
                    if (x,y,0) == pos:
                        self.persistentText.append("XX")
                    else:
                        self.persistentText.append(entry)

                    x += 1
                self.persistentText.append("\n")
                y += 1
            self.persistentText.append("\n")
        else:
            pos = selectedCharacter.getBigPosition()
            fullPos = selectedCharacter.getPosition()
            rawRender = selectedCharacter.container.render(coordinateOffset=(15*pos[1],15*pos[0]),size=(14,14))
            terrain = selectedCharacter.getTerrain()
            miniMapRender = terrain.renderTiles()

            y = 0
            for line in rawRender:
                x = 0
                for entry in line:
                    if (x+pos[0]*15,y+pos[1]*15,0) == fullPos:
                        self.persistentText.append("XX")
                    else:
                        self.persistentText.append(entry)
                    x += 1
                self.persistentText.append("  |  ")
                x = 0
                for entry in miniMapRender[y]:
                    if (x,y,0) == pos:
                        self.persistentText.append("XX")
                    else:
                        self.persistentText.append(entry)

                    x += 1
                self.persistentText.append("\n")
                y += 1
        self.persistentText.append("\nrank: %s"%(selectedCharacter.rank))
        self.persistentText.append("\ninventory: ")
        for item in selectedCharacter.inventory:
            self.persistentText.append(item.render())
            self.persistentText.append(" ")
        self.persistentText.append(f"({len(selectedCharacter.inventory)})")

        if selectedCharacter.weapon:
            self.persistentText.append("\nweapon: %s"%(selectedCharacter.weapon.baseDamage))
        else:
            self.persistentText.append("\nweapon: None")
        if selectedCharacter.armor:
            self.persistentText.append("\narmor: %s"%(selectedCharacter.armor.armorValue))
        else:
            self.persistentText.append("\narmor: None")
        self.persistentText.append("\nstaff: %s"%(selectedCharacter.isStaff))
        self.persistentText.append("\nduties: {}".format(", ".join(selectedCharacter.duties)))
        quest = selectedCharacter.getActiveQuest()
        if quest:
            self.persistentText.append(f"\nactive quest: {quest.description}")
        else:
            self.persistentText.append("\nactive quest: None")

        src.interaction.main.set_text(self.persistentText)
        return None
