import collections

import src

class AdvancedQuestMenu(src.menues.SubMenu):
    """
    player interaction for delegating a quest
    """

    type = "AdvancedQuestMenu"

    def __init__(self,activeChar=None):
        """
        set up internal state
        """

        self.character = None
        self.quest = None
        self.questParams = {}
        self.activeChar = activeChar
        self.submenu = None
        super().__init__()

    def getTitle(self):
        return "ADVANCED QUEST MENU"

    def handleKey(self, key, noRender=False, character = None):
        """
        gather the quests parameters and assign the quest

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            return True

        # start rendering
        if not noRender:
            src.interaction.header.set_text(
                (src.interaction.urwid.AttrSpec("default", "default"), "\nadvanced Quest management\n")
            )
            out = "\n"
            #if self.character:
            #    out += "character: " + str(self.character.name) + "\n"
            if self.quest:
                out += "quest: " + str(self.quest) + "\n"
            out += "\n"

        # handle the submenue key forwarding
        if self.submenu:

            # forward the key
            if not self.submenu.done:
                self.submenu.handleKey(key, noRender=noRender, character=character)
            if not self.submenu.done:
                return False

            # process the result
            selection = None
            if isinstance(self.submenu,src.menues.menuMap["SelectionMenu"]):
                selection = self.submenu.getSelection()
            if isinstance(self.submenu,src.menues.menuMap["InputMenu"]):
                selection = self.submenu.text

        # let the player select the character to assign the quest to
        if not self.character:
            if self.submenu and self.submenu.tag == "character_selection":

                # store the character to assign the quest to
                self.character = selection

            else:
                
                # add the active player as target
                base_text = "whom to give the order to: "
                options = [(
                    self.activeChar,
                    self.activeChar.name+ " (you)",
                )]
                options.append(("ALL","all subordinates"))

                # add the main players subordinates as target
                for char in self.activeChar.subordinates:
                    if char is None:
                        continue
                    options.append((char, char.name))
                self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options)
                self.submenu.tag = "character_selection"
                return False


        if not self.quest:
            if self.submenu and self.submenu.tag == "quest_selection":

                # store the selected quest type
                self.quest = selection

            else:

                # create the next menu
                base_text = "what type of quest:"
                options = []
                options.append(("quest_by_name", "Type quest name"))
                options.append(("GoHome", "GoHome"))
                options.append(("ClearInventory", "ClearInventory"))
                options.append(("Scavenge", "Scavenge"))
                options.append(("ScavengeTile", "ScavengeTile"))
                options.append(("ClearTile", "ClearTile"))
                options.append(("LootRoom", "LootRoom"))
                options.append(("RestockRoom", "RestockRoom"))
                options.append(("DoMapSync", "DoMapSync"))
                options.append(("SharpenPersonalSword", "SharpenPersonalSword"))
                options.append(("ReinforcePersonalArmor", "ReinforcePersonalArmor"))
                options.append(("ClearTerrain", "ClearTerrain"))
                options.append(("BeUsefull", "BeUsefull"))
                options.append(("SpawnClone", "SpawnClone"))
                options.append(("Adventure", "Adventure"))
                options.append(("SearchForRuins", "SearchForRuins"))
                options.append(("AdventureOnTerrain", "AdventureOnTerrain"))
                options.append(("Equip", "Equip"))
                options.append(("FarmMold", "FarmMold"))
                options.append(("GoInside", "GoInside"))
                self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options)
                self.submenu.tag = "quest_selection"
                return False

        # allow manually inputing a quest name
        if self.submenu.tag == "quest_input":
            self.quest = selection
        if self.quest == "quest_by_name":
            base_text = "Type the name of the quest you want to create:"
            self.submenu = src.menues.menuMap["InputMenu"](base_text)
            self.submenu.tag = "quest_input"
            return False

        # create the next menu
        if self.character == "ALL":
            self.activeChar.macroState["submenue"] = src.menues.menuMap["CreateQuestMenu"](self.quest, self.activeChar.subordinates, self.activeChar)
        else:
            self.activeChar.macroState["submenue"] = src.menues.menuMap["CreateQuestMenu"](self.quest, [self.character], self.activeChar)
        return True

    def render(self):
        '''
        show the text of the menu
        '''
        if self.submenu:
            return self.submenu.render()
        else:
            return ["""something went wrong"""]

# register the menu type
src.menues.add_menu(AdvancedQuestMenu)
