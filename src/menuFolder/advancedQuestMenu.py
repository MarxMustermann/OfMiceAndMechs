import collections

import src

class AdvancedQuestMenu(src.subMenu.SubMenu):
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
        super().__init__()

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

        # let the player select the character to assign the quest to
        if self.state is None:
            self.state = "participantSelection"
        if self.state == "participantSelection":

            if key == "S":
                self.state = "questSelection"
                self.character = "ALL"
                self.selection = None
                self.lockOptions = True
                self.options = None
            else:
                # set up the options
                if not self.options and not self.getSelection():

                    # add the active player as target
                    options = [(
                        self.activeChar,
                        self.activeChar.name+ " (you)",
                    )]

                    # add the main players subordinates as target
                    for char in self.activeChar.subordinates:
                        if char is None:
                            continue
                        options.append((char, char.name))
                    self.setOptions("whom to give the order to: \n(press S for all subordinates)", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the character to assign the quest to
                if self.getSelection():
                    self.state = "questSelection"
                    self.character = self.selection
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

        # let the player select the type of quest to create
        if self.state == "questSelection":

            if key == "N":
                self.state = "questByName"
                self.selection = ""
                key = "~"
            else:
                # add quests to select from
                if not self.options and not self.getSelection():
                    options = []
                    """
                    for key, value in src.quests.questMap.items():

                        # show only quests the character has done
                        if key not in self.activeChar.questsDone:
                            continue

                        # do not show naive quests
                        if key.startswith("Naive"):
                            continue

                        options.append((value.type, key))
                    """
                    options.append(("GoHome", "GoHome"))
                    options.append(("Adventure", "Adventure"))
                    options.append(("ScavengeTile", "ScavengeTile"))
                    options.append(("SecureTile", "SecureTile"))
                    options.append(("ClearInventory", "ClearInventory"))
                    options.append(("BeUsefull", "BeUsefull"))
                    options.append(("BeUsefullOnTile", "BeUsefullOnTile"))
                    options.append(("Equip", "Equip"))
                    options.append(("Eat", "Eat"))
                    options.append(("FillFlask", "FillFlask"))
                    self.setOptions("what type of quest: (press N for quest by name)", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the type of quest to create
                if self.getSelection():
                    self.state = "parameter selection"
                    self.quest = self.selection
                    self.selection = None
                    self.lockOptions = True
                    self.questParams = {}
                else:
                    return False

        if self.state == "questByName":
            if key == "enter":
                self.state = "parameter selection"
                if self.selection not in src.quests.questMap:
                    return True
                self.quest = self.selection
                self.selection = None
                self.lockOptions = True
                self.questParams = {}
            else:
                if key == "~":
                    pass
                elif key == "backspace":
                    if len(self.selection) > 0:
                        self.selection = self.selection[:-1]
                else:
                    self.selection += key

                if not noRender:
                    src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.selection+"\n\n%s"%(self.activeChar.questsDone)))
                return False

        # let the player select the parameters for the quest
        if self.state == "parameter selection":
            if self.quest == "EnterRoomQuestMeta":

                # set up the options
                if not self.options and not self.getSelection():

                    # add a list of of rooms
                    options = []
                    for room in src.gamestate.gamestate.terrain.rooms:
                        # do not show unimportant rooms
                        if isinstance(room, src.rooms.CpuWasterRoom | src.rooms.MechArmor):
                            continue
                        options.append((room, room.name))
                    self.setOptions("select the room:", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the parameter
                if self.getSelection():
                    self.questParams["room"] = self.selection
                    self.state = "confirm"
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

            elif self.quest == "StoreCargo":

                # set up the options for selecting the cargo room
                if "cargoRoom" not in self.questParams:
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in src.gamestate.gamestate.terrain.rooms:
                            # show only cargo rooms
                            if not isinstance(room, src.rooms.CargoRoom):
                                continue
                            options.append((room, room.name))
                        self.setOptions("select the room:", options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key, noRender=noRender, character=character)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["cargoRoom"] = self.selection
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
                else:
                    # set up the options for selecting the storage room
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in src.gamestate.gamestate.terrain.rooms:
                            # show only storage rooms
                            if not isinstance(room, src.rooms.StorageRoom):
                                continue
                            options.append((room, room.name))
                        self.setOptions("select the room:", options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key, noRender=noRender, character=character)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["storageRoom"] = self.selection
                        self.state = "confirm"
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
            elif self.quest:
                if self.character == "ALL":
                    self.activeChar.macroState["submenue"] = src.menuFolder.CreateQuestMenu.CreateQuestMenu(self.quest, self.activeChar.subordinates, self.activeChar)
                else:
                    self.activeChar.macroState["submenue"] = src.menuFolder.CreateQuestMenu.CreateQuestMenu(self.quest, [self.character], self.activeChar)
                return False
            else:
                # skip parameter selection
                self.state = "confirm"

        # get confirmation and assign quest
        if self.state == "confirm":

            # set the options for confirming the selection
            if not self.options and not self.getSelection():
                options = [("yes", "yes"), ("no", "no")]
                if self.quest == src.quests.EnterRoomQuestMeta:
                    self.setOptions(
                        "you chose the following parameters:\nroom: "
                        + str(self.questParams)
                        + "\n\nDo you confirm?",
                        options,
                    )
                else:
                    self.setOptions("Do you confirm?", options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key, noRender=noRender, character=character)

            if self.getSelection():
                # instantiate quest
                # bad code: repetitive code
                if self.selection == "yes":
                    if self.quest == src.quests.MoveQuestMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.mainChar.room, 2, 2
                        )
                    elif self.quest == src.quests.ActivateQuestMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.terrain.tutorialMachineRoom.furnaces[
                                0
                            ]
                        )
                    elif self.quest == src.quests.EnterRoomQuestMeta:
                        questInstance = self.quest(self.questParams["room"])
                    elif self.quest == src.quests.FireFurnaceMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.terrain.tutorialMachineRoom.furnaces[
                                0
                            ]
                        )
                    elif self.quest == src.quests.WaitQuest:
                        questInstance = self.quest()
                    elif self.quest == src.quests.LeaveRoomQuest:
                        questInstance = self.quest(self.character.room)
                    elif self.quest == src.quests.ClearRubble:
                        questInstance = self.quest()
                    elif self.quest == src.quests.RoomDuty:
                        questInstance = self.quest()
                    elif self.quest == src.quests.ConstructRoom:
                        for room in src.gamestate.gamestate.terrain.rooms:
                            if isinstance(room, src.rooms.ConstructionSite):
                                constructionSite = room
                                break
                        questInstance = self.quest(
                            constructionSite,
                            src.gamestate.gamestate.terrain.tutorialStorageRooms,
                        )
                    elif self.quest == src.quests.StoreCargo:
                        for room in src.gamestate.gamestate.terrain.rooms:
                            if isinstance(room, src.rooms.StorageRoom):
                                storageRoom = room
                        questInstance = self.quest(
                            self.questParams["cargoRoom"],
                            self.questParams["storageRoom"],
                        )
                    elif self.quest == src.quests.MoveToStorage:
                        questInstance = self.quest(
                            [
                                src.gamestate.gamestate.terrain.tutorialLab.itemByCoordinates[
                                    (1, 9)
                                ][
                                    0
                                ],
                                src.gamestate.gamestate.terrain.tutorialLab.itemByCoordinates[
                                    (2, 9)
                                ][
                                    0
                                ],
                            ],
                            src.gamestate.gamestate.terrain.tutorialStorageRooms[1],
                        )
                    elif self.quest == "special_furnace":
                        questInstance = src.quests.KeepFurnaceFiredMeta(
                            self.character.room.furnaces[0]
                        )
                    else:
                        questInstance = self.quest()

                    # assign the quest

                    self.character.assignQuest(questInstance, active=True)

                    self.state = "done"

                # reset progress
                else:
                    self.state = "questSelection"

                self.selection = None
                self.lockOptions = False
            else:
                return False

        # close submenu
        if self.state == "done":
            if self.lockOptions:
                self.lockOptions = False
            else:
                return True

        # show rendered text via urwid
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False
