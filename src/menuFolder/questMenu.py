import src

class QuestMenu(src.subMenu.SubMenu):
    """
    show the quests for a character and allow player interaction
    """

    def __init__(self, char=None):
        """
        initialise internal state

        Parameters:
            char: the character to show the quests for
        """

        self.type = "QuestMenu"
        self.lockOptions = True
        if not char:
            char = src.gamestate.gamestate.mainChar
        self.char = char
        self.offsetX = 0
        self.questCursor = [0]
        self.sidebared = False
        super().__init__()

    def render(self, char):
        return self.renderQuests(char=self.char, asList=True, questCursor=self.questCursor,sidebared=self.sidebared)

    # overrides the superclasses method completely
    def handleKey(self, key, noRender=False, character = None):
        """
        show a questlist and handle interactions

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            self.sidebared = True
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            self.sidebared = True
            return True

        # move the marker that marks the selected quest
        if key == "w" and self.questCursor[0] > 0:
            self.questCursor[0] -= 1
        if key == "s" and self.questCursor[0] < len(character.quests)-1:
            self.questCursor[0] += 1
        if key == "d":
            baseList = self.char.quests
            failed = False
            for index in self.questCursor:
                quest = baseList[index]
                try:
                    baseList = quest.subQuests
                    if len(baseList) < 1:
                        failed = True
                except:
                    baseList = None
                    failed = True
            if not failed:
                self.questCursor.append(0)
        if key == "a" and len(self.questCursor) > 1:
            self.questCursor.pop()

        # make the selected quest active
        if key == "j" and self.questCursor[0]:
            quest = self.char.quests[self.questCursor[0]]
            self.char.quests.remove(quest)
            self.char.quests.insert(0, quest)
            self.char.setPathToQuest(quest)
            self.questCursor[0] = 0
            self.char.runCommandString(["esc"])
        if key == "K":
            quest = None
            baseList = self.char.quests
            for index in self.questCursor:
                quest = baseList[index]
                baseList = quest.subQuests
            quest.autoSolve = True
            self.char.runCommandString(["esc"])
        if key == "r":
            quest = None
            baseList = self.char.quests
            for index in self.questCursor:
                quest = baseList[index]
                baseList = quest.subQuests
            quest.generateSubquests(self.char)
        if key == "R":
            baseList = self.char.quests
            for index in self.questCursor:
                quest = baseList[index]
                baseList = quest.subQuests
            quest.clearSubQuests()
            quest.generateSubquests(self.char)
        if key == "x":
            baseList = self.char.quests
            for index in self.questCursor:
                quest = baseList[index]
                try:
                    baseList = quest.subQuests
                except:
                    baseList = None
            quest.fail()
        if key == "X":
            baseList = self.char.quests
            for index in self.questCursor:
                quest = baseList[index]
                try:
                    baseList = quest.subQuests
                except:
                    baseList = None
            quest.clearSubQuests()

        # render the quests
        addition = ""
        if self.char == src.gamestate.gamestate.mainChar:
            addition = " (you)"
        src.interaction.header.set_text(
            (
                src.interaction.urwid.AttrSpec("default", "default"),
                "\nquest overview for "
                + self.char.name
                + ""
                + addition
                + "\n\n",
            )
        )
        self.persistentText = []
        self.persistentText.append(
            self.render(self.char)
        )

        self.lockOptions = False

        # add interaction instructions
        self.persistentText.extend(
            [
                "\n",
                "* press esc to close this menu\n",
                "* press wasd to select quest\n",
                "* press j to make selected quest the active quest\n",
                "* press x to delete selected quest\n",
                "* press X to delete sub quests\n",
                "* press r to generate sub quests\n",
                "* press R to regenerate sub quests\n",
                "* press k to check if that quest has been completed\n",
                "* press K to mark the selected quest for auto completion\n",
                "\n",
            ]
        )

        # flatten the mix of strings and urwid format so that it is less recursive to workaround an urwid bug
        # bad code: should be elsewhere
        def flatten(pseudotext):
            newList = []
            for item in pseudotext:
                if isinstance(item, list):
                    for subitem in flatten(item):
                        newList.append(subitem)
                elif isinstance(item, tuple):
                    newList.append((item[0], flatten(item[1])))
                else:
                    newList.append(item)
            return newList

        self.persistentText = flatten(self.persistentText)

        # show rendered quests via urwid
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False
    # bad code: the asList and questIndex parameters are out of place
    @staticmethod
    def renderQuests(maxQuests=0, char=None, asList=False, questCursor=None,sidebared=False):
        """
        render the quests into a string or list

        Parameters:
            maxQuests: the maximal number of quests rendered (0=no maximum)
            char: the character the quests belong to
            asList: flag to switch from rendering as string to rendering as list
            questsIndex: index pointing to the active quest

        Returns:
            the rendered messages
        """

        # basic set up
        if not char:
            char = src.gamestate.gamestate.mainChar
        if asList:
            txt = []
        else:
            txt = ""

        # render the quests
        if len(char.quests):
            if sidebared:
                result = char.getActiveQuest().getSolvingCommandString(char)
                solvingCommangString = None
                if result:
                    if isinstance(result,list):
                        result = (result,"continue")
                    if isinstance(result,str):
                        result = (result,"continue")
                    (solvingCommangString,reason) = result
                    if isinstance(solvingCommangString,list):
                        solvingCommangString = "".join(solvingCommangString)
                    if solvingCommangString:
                        solvingCommangString = solvingCommangString.replace("\n","\\n")

                if solvingCommangString:
                    nextstep = f"suggested action: \npress {solvingCommangString} \nto {reason}\n\n"
                else:
                    nextstep = "suggested action: \npress + \nto generate subquests\n\n"
                txt.append(src.interaction.ActionMeta(payload="+",content=nextstep))

            if not sidebared:
                baseList = char.quests
                for index in questCursor:
                    if index >= len(baseList):
                        index = 0
                    quest = baseList[index]
                    try:
                        baseList = quest.subQuests
                    except:
                        baseList = None
                txt.append(quest.generateTextDescription())
                txt.append("\n")
                txt.append("\n")

                solvingCommangString = char.getActiveQuest().getSolvingCommandString(char)

            if not sidebared:
                txt.append("select quest:\n\n")

            counter = 0
            for quest in char.quests:
                if questCursor and counter == questCursor[0]:
                    newCursor = questCursor[1:]
                else:
                    newCursor = None
                txt.extend(
                    quest.render(cursor=newCursor,sidebared=sidebared)
                        )
                txt.extend("\n\n")
                counter += 1


            if sidebared:
                txt.append("press q to see detailed descriptions\n\n")
        else:
            txt.append("No Quest\n\n")

        return txt
