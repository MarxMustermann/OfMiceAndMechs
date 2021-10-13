import src

class AutoTutor(src.items.Item):
    """
    ingame item serving as a tutorial
    """

    type = "AutoTutor"

    def __init__(self):
        """
        set up internal state
        """

        self.knownBlueprints = []
        self.knownInfos = []
        self.availableChallenges = {}

        super().__init__(display=src.canvas.displayChars.infoscreen)

        self.name = "auto tutor"

        self.submenue = None
        self.text = None
        self.blueprintFound = False
        self.gooChallengeDone = False
        self.metalbarChallengeDone = False
        self.sheetChallengeDone = False
        self.machineChallengeDone = False
        self.blueprintChallengeDone = False
        self.commandChallengeDone = False
        self.energyChallengeDone = False
        self.activateChallengeDone = False
        self.activateChallenge = 100
        self.metalbarChallenge = 100
        self.wallChallenge = 25
        self.autoScribeChallenge = 25
        self.challengeRun2Done = False
        self.challengeRun3Done = False
        self.challengeRun4Done = False
        self.challengeRun5Done = False
        self.initialChallengeDone = False
        self.challengeInfo = {}

        self.attributesToStore.extend(
            [
                "gooChallengeDone",
                "metalbarChallengeDone",
                "sheetChallengeDone",
                "machineChallengeDone",
                "blueprintChallengeDone",
                "energyChallengeDone",
                "activateChallengeDone",
                "commandChallengeDone",
                "challengeRun2Done",
                "challengeRun3Done",
                "challengeRun4Done",
                "challengeRun5Done",
                "initialChallengeDone",
                "activateChallenge",
                "wallChallenge",
                "autoScribeChallenge",
                "knownBlueprints",
                "availableChallenges",
                "knownInfos",
                "challengeInfo",
            ]
        )

    def addScraps(self, amount=1):
        """
        add scrap to the environment

        Parameters:
            amount: how much scrap to add
        Returns:
            flag indicating wheter or not the scrap was added 
        """

        targetFull = False
        scrapFound = None
        itemList = self.container.getItemByPosition(
            (self.xPosition, self.yPosition + 1)
        )
        if len(itemList) > 15:
            targetFull = True
        for item in itemList:
            if item.walkable == False:
                targetFull = True
            if item.type == "Scrap":
                scrapFound = item

        if targetFull:
            return False

        if scrapFound:
            scrapFound.amount += amount
            scrapFound.setWalkable()
        else:
            # spawn scrap
            new = src.items.itemMap["Scrap"](
                amount = 1
            )
            self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))
            new.setWalkable()

        return True

    def apply(self, character):
        """
        handle a character using this item
        by starting to show the tutorial

        Parameters:
            character: the character trying to use this item
        """

        self.character = character

        options = []

        options.append(("level1", "check information"))
        options.append(("challenge", "do challenge"))

        self.submenue = src.interaction.SelectionMenu(
            "This is the automated tutor. Complete challenges and get information.\n\nwhat do you want do to?",
            options,
        )

        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.step2

        self.character = character

    def step2(self):
        """
        handle a character using this item
        by offering the character a selection of actions

        Parameters:
            character: the character trying to use this item
        """

        selection = self.submenue.getSelection()
        self.submenue = None

        if selection == "level1":
            self.basicInfo()
        elif selection == "challenge":
            self.challenge()
        elif selection == "level2":
            self.l2Info()
        elif selection == "level3":
            self.l3Info()
        elif selection == "level4":
            self.l4Info()
        else:
            self.character.addMessage("NOT ENOUGH ENERGY")

    def challenge(self):
        """
        handle a character using this item
        by confronting the character with a challenge

        Parameters:
            character: the character trying to use this item
        """

        if not self.activateChallengeDone:
            if not self.initialChallengeDone:
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: find the challenges\nstatus:challenge completed.\n\nReturn to this menu item and you will find more challenges.\nNew challenge "pick up goo flask"\n\n'
                )
                self.initialChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.gooChallengeDone:
                if not self.checkInInventory(src.items.itemMap["GooFlask"]):
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: pick up goo flask\nstatus: challenge in progress - Try again with a goo flask in your inventory.\n\ncomment:\nA goo flask is represnted by ò=. There should be some flasks in the room.\n\n"
                    )
                else:
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: pick up goo flask\nstatus: challenge completed.\n\ncomment:\nTry to always keep a goo flask with some charges in your inventory.\nIf you are hungry you will drink from it automatically.\nIf you do not drink regulary you will die.\n\nreward:\nNew information option on "information->machines"\nNew Information option on "information->food"\nNew challenge "gather metal bars"\n\n'
                    )
                    self.gooChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.metalbarChallengeDone:
                if not self.checkInInventory(src.items.itemMap["MetalBars"]):
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: gather metal bars\nstatus: challenge in progress - Try again with a metal bar in your inventory.\n\ncomment: \nMetal bars are represented by ==\ncheck "information->machines->metal bar production" on how to produce metal bars.\n\n'
                    )
                else:
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: gather metal bars\nstatus: challenge completed.\n\nreward:\nNew information option on "information->machines->simple item production"\nNew challenge "produce sheet"\n\n'
                    )
                    self.metalbarChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.sheetChallengeDone:
                if not self.checkInInventoryOrInRoom(src.items.itemMap["Sheet"]):
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce sheet\nstatus: challenge in progress - Try again with a sheet in your inventory.\n\ncomment: \ncheck "information->machines->simple item production" on how to produce simple items.\nA sheet machine should be within this room.\n\n'
                    )
                else:
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce sheet\nstatus: challenge completed.\n\nreward:\nNew information option on "information->machines->machine production"\nNew challenge "produce rod machine"\n\n'
                    )
                    self.sheetChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.machineChallengeDone:
                foundMachine = False
                for item in self.character.inventory + self.container.itemsOnFloor:
                    if isinstance(item, src.items.itemMap["Machine"]) and item.toProduce == "Rod":
                        foundMachine = True
                if not foundMachine:
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce rod machine\nstatus: challenge in progress - Try again with a machine that produces rods in your inventory.\n\ncomment:\n\ncheck "information->machines->machine production" on how to produce machines.\nBlueprints for the basic materials including rods should be in this room.\nblueprints are represented by bb\n\n'
                    )
                else:
                    self.knownBlueprints.append("Frame")
                    self.knownBlueprints.append("Rod")
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce rod machine\nstatus: challenge completed.\n\nreward:\nNew information option on "information->machines->blueprint production"\nNew information option on "information->blueprint reciepes"\nNew challenge "produce blueprint for frame"\n\n'
                    )
                    self.machineChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.blueprintChallengeDone:
                foundBluePrint = False
                for item in self.character.inventory + self.container.itemsOnFloor:
                    if (
                        isinstance(item, src.items.itemMap["BluePrint"])
                        and item.endProduct == "Frame"
                    ):
                        foundBluePrint = True
                if not foundBluePrint:
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce blueprint for frame\nstatus: challenge in progress - Try again with a blueprint for frame in your inventory.\n\ncomment: \ncheck "information->machines->blueprint production" on how to produce blueprints.\nThe reciepe for Frame is rod+metalbar\n\n'
                    )
                else:
                    self.knownBlueprints.append("Bolt")
                    self.knownBlueprints.append("Sheet")
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: produce blueprint for frame\nstatus: challenge completed.\n\nreward:\nNew information option on "information->automation"\nNew blueprint reciepe for bolt\nNew blueprint reciepe for sheet\nNew challenge "create command"\n\n'
                    )
                    self.blueprintChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.commandChallengeDone:
                if not self.checkInInventoryOrInRoom(src.items.itemMap["Command"]):
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge: create command\nstatus: challenge in progress - Try again with a command in your inventory.\n\ncomment: \ncheck "information->automation->command creation" on how to record commands.\n\n'
                    )
                else:
                    self.knownBlueprints.append("Stripe")
                    self.knownBlueprints.append("Mount")
                    self.knownBlueprints.append("Radiator")
                    self.submenue = src.interaction.TextMenu(
                        '\n\nchallenge completed.\n\nreward:\nNew information option on "information->automation->multiplier"\n\nreward:\nNew blueprint reciepe for stripe.\nNew blueprint reciepe for mount.\nNew blueprint reciepe for radiator.\nNew challenge "repeat challenge"\n\n'
                    )
                    self.commandChallengeDone = True
                self.character.macroState["submenue"] = self.submenue
            elif not self.activateChallengeDone:
                if self.activateChallenge:
                    self.activateChallenge -= 1
                    if self.activateChallenge == 100:
                        self.submenue = src.interaction.TextMenu(
                            '\n\nchallenge: repeat challenge\n\nstatus: challenge in progress - Use this menu item a 100 times. The first step is done. Activations remaining %s\n\ncomment: use a command to activate the menu item and multipliers to do this often.\n check "information->automation" on how to do this.'
                            % (self.activateChallenge,)
                        )
                    else:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: repeat challenge\nstatus: challenge in progress - Use this menu item a 100 times. Activations remaining %s\n\ncomment: use a command to activate the menu item and multipliers to do this often"
                            % (self.activateChallenge,)
                        )
                else:
                    if len(self.character.inventory):
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: repeat challenge\nstatus: in progress. Try again with empty inventory to complete.\n\n"
                        )
                    else:
                        self.submenue = src.interaction.TextMenu(
                            '\n\nchallenge: repeat challenge\nstatus: challenge completed.\n\ncomment:\nyou completed the first set of challenges\ncome back for more\n\nreward:\nNew blueprint reciepe for scrap compactor\nNew challenge "produce scrap compactor"\nNew challenge "gather bloom"\nNew challenge "create note"\n\n'
                        )
                        self.activateChallengeDone = True
                        self.knownBlueprints.append("ScrapCompactor")
                        self.availableChallenges = {
                            "produceScrapCompactors": {
                                "text": "produce scrap compactor"
                            },
                            "gatherBloom": {"text": "gather bloom"},
                            "note": {"text": "create note"},
                        }
                self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun2Done:
            if len(self.availableChallenges):
                options = []
                for (key, value) in self.availableChallenges.items():
                    options.append([key, value["text"]])

                self.submenue = src.interaction.SelectionMenu(
                    "select the challenge to do:", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if self.metalbarChallenge:

                    metalBarFound = None
                    for item in self.character.inventory:
                        if isinstance(item, src.items.itemMap["MetalBars"]):
                            metalBarFound = item
                            break

                    if not metalBarFound:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 100 metal bars\nstatus: no progress - Try again with metal bars in your inventory\nMetal bars remaining %s\n\n"
                            % (self.metalbarChallenge,)
                        )
                        self.character.macroState["submenue"] = self.submenue
                        return

                    didAdd = self.addScraps(amount=1)
                    if not didAdd:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 100 metal bars\nstatus: no progress - no space to drop scrap\nMetal bars remaining %s\n\n"
                            % (self.metalbarChallenge,)
                        )
                        self.character.macroState["submenue"] = self.submenue
                        return

                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress.\nMetal bars remaining %s\n\ncomment: \nscrap ejected to the south/below\nuse commands and multipliers to do this.\n\n"
                        % (self.metalbarChallenge,)
                    )
                    self.character.inventory.remove(metalBarFound)
                    self.metalbarChallenge -= 1

                else:
                    if len(self.character.inventory):
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 100 metal bars\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n"
                        )
                    else:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 100 metal bars\nstatus: challenge completed.\n\nreward:\nNew challenges added\nnew reciepes for Connector Pusher\n\n"
                        )
                        self.availableChallenges["differentBlueprints"] = {
                            "text": "9 different blueprints"
                        }
                        self.availableChallenges["9blooms"] = {"text": "9 blooms"}
                        self.availableChallenges["produceAdvanced"] = {
                            "text": "produce items"
                        }
                        self.availableChallenges["produceScraper"] = {"text": "scraper"}
                        self.challengeRun2Done = True
                        self.knownBlueprints.append("Connector")
                        self.knownBlueprints.append("Pusher")
                self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun3Done:
            if len(self.availableChallenges):
                options = []
                for (key, value) in self.availableChallenges.items():
                    options.append([key, value["text"]])

                self.submenue = src.interaction.SelectionMenu(
                    "select the challenge", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if self.wallChallenge:
                    wallFound = None
                    for item in self.character.inventory:
                        if isinstance(item, src.items.itemMap["Wall"]):
                            wallFound = item
                            break

                    if not wallFound:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - try again with walls in inventory\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"
                            % (self.wallChallenge,)
                        )
                        self.character.macroState["submenue"] = self.submenue
                        return

                    didAdd = self.addScraps(amount=2)
                    if not didAdd:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nno progress - no space to drop scrap\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"
                            % (self.wallChallenge,)
                        )
                        self.character.macroState["submenue"] = self.submenue
                        return

                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: produce 25 walls\nstatus: challenge in progress.\nWalls remaining: %s\n\ncomment:\nuse commands and multipliers to do this.\n\n"
                        % (self.wallChallenge,)
                    )
                    self.character.inventory.remove(wallFound)
                    self.wallChallenge -= 1
                    self.character.macroState["submenue"] = self.submenue

                else:
                    if len(self.character.inventory):
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 25 walls\nstatus: challenge in progress. Try again with empty inventory to complete.\n\n"
                        )
                    else:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge: produce 25 walls\nstatus: challenge completed\n\n"
                        )
                        self.availableChallenges["produceBioMasses"] = {
                            "text": "produce 9 bio mass"
                        }
                        self.availableChallenges["createMap"] = {"text": "create map"}
                        self.availableChallenges["produceProductionManager"] = {
                            "text": "produce production manager"
                        }
                        self.challengeRun3Done = True
                        self.knownBlueprints.append("RoomBuilder")
                        self.knownBlueprints.append("FloorPlate")
                        self.knownBlueprints.append("ProductionManager")
                        self.knownBlueprints.append("MemoryCell")
                    self.character.macroState["submenue"] = self.submenue
        elif not self.challengeRun4Done:
            self.character.addMessage("challenge run 4")
            if len(self.availableChallenges):
                options = []
                for (key, value) in self.availableChallenges.items():
                    options.append([key, value["text"]])

                self.submenue = src.interaction.SelectionMenu(
                    "select the challenge", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                if not self.challengeInfo:
                    self.challengeInfo = {"numSucesses": 0, "type": None}

                if self.challengeInfo["numSucesses"] >= 25:
                    if self.character.inventory:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nactivate with empty inventory to complete challenge.\n\n"
                        )
                        self.character.macroState["submenue"] = self.submenue
                    else:
                        self.submenue = src.interaction.TextMenu(
                            "\n\nchallenge completed.\n\n"
                        )
                        self.character.macroState["submenue"] = self.submenue
                        self.challengeRun4Done = True

                        self.challengeInfo = {"challengerGiven": []}

                        self.availableChallenges["produceAutoScribe"] = {
                            "text": "produce auto scribe"
                        }
                        self.availableChallenges["produceFilledGooDispenser"] = {
                            "text": "produce goo"
                        }
                        self.availableChallenges["gatherSickBloom"] = {
                            "text": "gather sick bloom"
                        }
                else:
                    text = """challenge: run job orders\n\njob orders for Wall or Door or Floor plates will be dropped to the south. Produce the item named on the job order and return with the item.

finish 25 round (%s remaining):

""" % (
                        25 - self.challengeInfo["numSucesses"],
                    )
                    if self.challengeInfo["type"]:
                        jobOrder = None
                        itemDelivered = None
                        for item in self.character.inventory:
                            if item.type == "GooFlask":
                                pass
                            elif (
                                item.type == "JobOrder"
                                and item.done
                                and item.tasks[-1]["toProduce"]
                                == self.challengeInfo["type"]
                                and item.tasks[-1]["task"] == "produce"
                            ):
                                itemDelivered = item

                        fail = False
                        if not itemDelivered:
                            text += (
                                "you need to have the completed job order for "
                                + self.challengeInfo["type"]
                                + " in your inventory\n"
                            )
                            fail = True

                        if not fail:
                            self.character.inventory.remove(itemDelivered)
                            text += "you succeded this round\n"
                            self.challengeInfo["type"] = None
                            self.challengeInfo["numSucesses"] += 1

                    if (
                        self.challengeInfo["type"] is None
                        and not self.challengeInfo["numSucesses"] >= 25
                    ):
                        itemType = random.choice(["Wall", "Door", "FloorPlate"])
                        self.character.addMessage(itemType)

                        self.challengeInfo["type"] = itemType
                        newItem = src.items.itemMap["JobOrder"]()
                        newItem.tasks[-1]["toProduce"] = itemType
                        self.container.addItems(newItem,(self.xPosition,self.yPosition+1,self.zPosition))

                        text += "new job order outputted on the south of the machine"

                        text += """

comment:

* set the production managers commands to produce walls and doors and floor plates
* use the dropped job order with the production manager to produce the required items
* return to the auto tutor with the completed job order
* use commands and multipliers to do this multiple times"""

                    self.submenue = src.interaction.TextMenu("\n\n" + text + "\n\n")
                    self.character.macroState["submenue"] = self.submenue

        elif not self.challengeRun5Done:
            if len(self.availableChallenges):
                options = []
                for (key, value) in self.availableChallenges.items():
                    options.append([key, value["text"]])

                self.submenue = src.interaction.SelectionMenu(
                    "select the challenge to do:", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.challengeRun2
            else:
                numFlasksFound = 0
                for item in self.character.inventory:
                    if item.type == "GooFlask" and item.uses == 100:
                        numFlasksFound += 1

                if not numFlasksFound > 3:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: Produce 4 filled goo flasks. \nchallenge in progress. Try again with 4 goo flasks with 100 uses left in each in your inventory.\n\n"
                    )
                    self.character.macroState["submenue"] = self.submenue
                else:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: Produce 4 filled goo flasks. \nchallenge completed.\n\nreward: Character spawned. Talk to it by pressing h and command it.\n\n"
                    )
                    self.character.macroState["submenue"] = self.submenue
                    gooFlask1 = None
                    gooFlask2 = None
                    for item in reversed(self.character.inventory):
                        if item.type == "GooFlask" and item.uses == 100:
                            if gooFlask1 is None:
                                gooFlask1 = item
                            else:
                                gooFlask2 = item
                                break

                    self.character.inventory.remove(gooFlask2)
                    gooFlask1.uses = 0

                    # add character
                    name = "Erwin Lauterbach"
                    newCharacter = characters.Character(
                        src.canvas.displayChars.staffCharactersByLetter[
                            name[0].lower()
                        ],
                        name=name,
                    )

                    newCharacter.solvers = [
                        "SurviveQuest",
                        "Serve",
                        "NaiveMoveQuest",
                        "MoveQuestMeta",
                        "NaiveActivateQuest",
                        "ActivateQuestMeta",
                        "NaivePickupQuest",
                        "PickupQuestMeta",
                        "DrinkQuest",
                        "ExamineQuest",
                        "FireFurnaceMeta",
                        "CollectQuestMeta",
                        "WaitQuest" "NaiveDropQuest",
                        "NaiveDropQuest",
                        "DropQuestMeta",
                    ]

                    self.challengeRun5Done = True

                    self.container.addCharacter(
                        newCharacter, self.xPosition, self.yPosition + 1
                    )
                    newCharacter.macroState["macros"]["j"] = "Jf"
                    newCharacter.inventory.append(gooFlask2)

        else:
            self.submenue = src.interaction.TextMenu("\n\nTBD\n\n")
            self.character.macroState["submenue"] = self.submenue

    def checkForOtherItem(self, itemType):
        """
        checks wheter a characters inventory contains exactly one item of a type

        Returns:
            whether or not items were found
        """

        if len(self.character.inventory) > 2:
            return True
        foundOtherItem = None
        for item in self.character.inventory:
            if item.type not in ["GooFlask", itemType]:
                foundOtherItem = item
                break
        if foundOtherItem:
            return True
        return False

    def getFromInventory(self, itemType):
        """
        get a item of a certain type from the characters inventory

        Parameters:
            itemType: the type of item to check for

        Returns:
            the item found or None
        """

        foundItem = None
        for item in self.character.inventory:
            if item.type in [itemType]:
                foundItem = item
                break
        return foundItem

    def challengeRun2(self):
        """
        handle a character using this item
        by confronting the character with a second tier of challenges
        """

        selection = self.submenue.getSelection()
        self.submenue = None

        # <=
        #
        # Note
        # gatherBloom
        # R SporeExtractor
        # R Puller
        # I food/moldfarming
        # produceSporeExtractor
        # produceScrapCompactors
        # R Tank
        # R Scraper
        # produceBasics
        # R Case
        # R Wall
        # prodCase
        # R Heater
        # => produce 100 metal bars

        if selection == "note":  # from root
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Note"]):
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: write note\nstatus: challenge in progress - Try again with a note in your inventory.\n\ncomment:\n check "information->items->notes" on how to create notes.\n\n'
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: write note\nstatus: challenge completed.\n\nreward:\nnew Information option on "Information->automation->maps"\n\n'
                )
                del self.availableChallenges["note"]

        elif selection == "gatherBloom":  # from root
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Bloom"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather bloom\nstatus: challenge in progress - Try again with a bloom in your inventory.\n\ncomment: \nBlooms are represented by ** and are white.\nYou should be able to collect some outside of the wall, the exit is on the east.\n\n"
                )
            else:
                del self.availableChallenges["gatherBloom"]
                self.availableChallenges["produceSporeExtractor"] = {
                    "text": "produce a Spore Extractor"
                }
                self.knownBlueprints.append("SporeExtractor")
                self.knownBlueprints.append("Puller")
                self.knownInfos.append("food/moldfarming")
                blooms = []
                for i in range(0, 4):
                    new = itemMap["MoldSpore"]()
                    blooms.append((new,(self.xPosition,self.yPosition+1,self.zPosition)))
                self.container.addItems(blooms)
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: gather bloom\nstatus: challenge completed.\n\nreward:\nchallenge "produce a Spore Extractor" added\nmold spores added to south/below\nnew Information option on "information->food->mold farming"\nNew blueprint reciepes for Tank + Puller\n\n'
                )

        elif selection == "produceSporeExtractor":  # from gatherBloom
            if not self.checkInInventoryOrInRoom(src.items.itemMap["SporeExtractor"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce spore extractor\nstatus: challenge in progress - try again with spore extractor in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce spore extractor\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceSporeExtractor"]

        elif selection == "produceScrapCompactors":  # from root
            if not self.checkInInventory(src.items.itemMap["ScrapCompactor"]):
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce scrap compactor\nstatus: challenge in progress - try again with scrap compactor in your inventory.\n\ncomment:\n * check "information->blueprint reciepes" and "information -> machines -> machine production" on how to do this.\n\n'
                )
            else:
                self.knownBlueprints.append("Tank")
                self.knownBlueprints.append("Scraper")
                self.availableChallenges["produceBasics"] = {"text": "produce basics"}
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce scrap compactor\nstatus: challenge completed.\n\nreward:\nchallenge "%s" added\nNew blueprint reciepes for Tank, Scraper\n\n'
                    % (self.availableChallenges["produceBasics"]["text"])
                )
                del self.availableChallenges["produceScrapCompactors"]

        elif selection == "produceBasics":  # from produceScrapCompactors
            if self.checkListAgainstInventoryOrIsRoom(
                ["Rod", "Bolt", "Stripe", "Mount", "Radiator", "Sheet"]
            ):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce basics\nstatus: challenge in progress. Try again with rod + bolt + stripe + mount + radiator + sheet in your inventory.\n\ncomment:\nThe blueprints required should be in this room.\n\n"
                )
            else:
                del self.availableChallenges["produceBasics"]
                self.knownBlueprints.append("Case")
                self.knownBlueprints.append("Wall")
                self.availableChallenges["prodCase"] = {"text": "produce case"}
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce basics\nstatus: challenge completed.\n\nreward:\nchallenge "%s" added\nNew blueprint reciepes for Case, Wall\n'
                    % (self.availableChallenges["prodCase"]["text"])
                )

        elif selection == "prodCase":  # from produceBasics
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Case"]):
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce case\nstatus: challenge in progress - Try again with a case in your inventory.\n\ncomment:\nCases are produced from Frames\n which are produced from rods\n which are produced from metal bars\n which are produced from scrap\ncheck "information -> blueprint reciepes" for the reciepes\n\n'
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce case\nstatus: challenge completed.\n\nreward:\nNew blueprint reciepes for Heater, Door\n\n"
                )
                self.knownBlueprints.append("Heater")
                self.knownBlueprints.append("Door")
                del self.availableChallenges["prodCase"]

        # <=
        # R Connector
        # R Pusher
        # differentBlueprints
        # 9blooms
        # R BloomShredder
        # processedBloom
        # produceAdvanced
        # produceWall
        # R Door
        # produceDoor
        # R FloorPlate
        # produceFloorPlate
        # produceScraper

        # => 25 walls

        elif selection == "differentBlueprints":  # from root2
            blueprints = []
            for item in self.character.inventory + self.container.itemsOnFloor:
                if (
                    isinstance(item, src.items.itemMap["BluePrint"])
                    and item.endProduct not in blueprints
                ):
                    blueprints.append(item.endProduct)
            if not len(blueprints) > 8:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce 9 different blueprint\nstatus: challenge in progress - try again with 9 different blueprints in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce 9 different blueprint\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["differentBlueprints"]

        elif selection == "9blooms":  # from root2
            if self.countInInventoryOrRoom(src.items.itemMap["Bloom"]) < 9:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather 9 blooms\nstatus: failed. Try with 9 bloom in your inventory.\n\n\n\n"
                )
            else:
                self.availableChallenges["processedBloom"] = {"text": "process bloom"}
                self.knownBlueprints.append("BloomShredder")
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge completed.\n\nreward:\n* new blueprint reciepe for bloom shredder\n* challenge %s added\n\n"
                    % (self.availableChallenges["processedBloom"]["text"])
                )
                del self.availableChallenges["9blooms"]

        elif selection == "processedBloom":  # from 9blooms
            if not self.checkInInventoryOrInRoom(src.items.itemMap["BioMass"]):
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: process bloom\nstatus: challenge in progress - try with bio mass in your inventory.\n\ncomment:\n* use a bloom shreder to produce bio mass\n* check "information->food->mold farming" for more information\n\n'
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: process bloom\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["processedBloom"]

        elif selection == "produceAdvanced":  # from root2
            if self.checkListAgainstInventoryOrIsRoom(
                ["Tank", "Heater", "Connector", "pusher", "puller", "Frame"]
            ):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge in progress - try again with tank + heater + connector + pusher + puller + frame in your inventory.\n\n"
                )
            else:
                del self.availableChallenges["produceAdvanced"]
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge completed.\n\n"
                )

        elif selection == "produceWall":  # from produceAdvanced
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Wall"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge in progress - try again with wall in your inventory.\n\n"
                )
            else:
                del self.availableChallenges["produceWall"]
                self.knownBlueprints.append("Door")
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge completed.\n\nreward:\n* new blueprint reciepe for door\n\n"
                )

        elif selection == "produceDoor":  # from produceWall
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Door"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge in progress - try again with door in your inventory.\n\nreward:\n* new blueprint reciepe for floor plate\n\n"
                )
            else:
                del self.availableChallenges["produceDoor"]
                self.knownBlueprints.append("FloorPlate")
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge completed.\n\n"
                )

        elif selection == "produceFloorPlate":  # from produceDoor
            if not self.checkInInventoryOrInRoom(src.items.itemMap["FloorPlate"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge in progress - try again with floor plate in your inventory.\n\n"
                )
            else:
                del self.availableChallenges["produceFloorPlate"]
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce items\nstatus: challenge completed.\n\n"
                )

        elif selection == "produceScraper":  # from root2
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Scraper"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce scraper\nstatus: challenge in progress. Try with scraper in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce scraper\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceScraper"]

        # <=
        # R RoomBuilder
        # R FloorPlate
        # R Production Manager
        # produceBioMasses
        # R BioPress
        # processBioMass
        # build autofarmer
        # producePressCakes
        # R GooDispenser
        # R GooFlask
        # buildGooProducer
        # R GooProducer
        # R AutoFarmer
        # createMap
        # createMapWithPaths
        # build production manager
        # R AutoScribe
        # R uniformStockpileManager
        # build uniformStockpileManager

        # => produce random door/wall/floorplate things

        elif selection == "produceBioMasses":  # from root3
            if self.countInInventoryOrRoom(src.items.itemMap["BioMass"]) < 9:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce 9 Biomass\nstatus: challenge in progress. Try with 9 BioMass in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce 9 Biomass\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["processBioMass"] = {
                    "text": "process bio mass"
                }
                self.knownBlueprints.append("BioPress")
                del self.availableChallenges["produceBioMasses"]

        elif selection == "processBioMass":  # from produceBioMasses
            if not self.checkInInventoryOrInRoom(src.items.itemMap["PressCake"]):
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce press cake\nstatus: challenge in progress. Try with Press cake in your inventory.\n\ncomment:\n* use a bio press to produce press cake\n* check "information->food->mold farming" for more information\n\n'
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce press cake\nstatus: challenge completed.\n\nreward:\n* new blueprint reciepes for GooProducer, AutoFarmer\n\n"
                )
                self.availableChallenges["producePressCakes"] = {
                    "text": "produce press cakes"
                }
                self.availableChallenges["buildGooProducer"] = {
                    "text": "build goo producer"
                }
                self.availableChallenges["produceAutofarmer"] = {
                    "text": "produce autofarmer"
                }
                self.knownBlueprints.append("GooProducer")
                self.knownBlueprints.append("AutoFarmer")
                del self.availableChallenges["processBioMass"]

        elif selection == "producePressCakes":  # from processBioMass
            if self.countInInventoryOrRoom(src.items.itemMap["PressCake"]) < 4:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce press cakes\nstatus: challenge in progress. Try with 4 press cake in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce press cake\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["producePressCakes"]

                self.knownBlueprints.append("GooDispenser")
                self.knownBlueprints.append("GooFlask")

        elif selection == "buildGooProducer":  # from processBioMass
            if not self.checkInInventoryOrInRoom(src.items.itemMap["GooProducer"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build goo producer\nstatus: challenge in progress. Try with goo producer in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build goo producer\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["buildGooProducer"]

        elif selection == "produceAutofarmer":  # from processBioMass
            if not self.checkInInventoryOrInRoom(src.items.itemMap["AutoFarmer"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build auto farmer\nstatus: challenge in progress. Try with auto farmer in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build auto farmer\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceAutofarmer"]

        elif selection == "createMap":  # from root3
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Map"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: create map\nstatus: challenge in progress. Try with map in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: create map\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["createMapWithPaths"] = {
                    "text": "create map with routes"
                }
                del self.availableChallenges["createMap"]

        elif selection == "createMapWithPaths":  # from createMap
            itemFound = False
            for item in self.character.inventory + self.container.itemsOnFloor:
                if isinstance(item, src.items.itemMap["Map"]) and item.routes:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: create map with paths\nstatus: challenge in progress. Try with map with paths in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: create map with paths\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["createMapWithPaths"]

        elif selection == "produceProductionManager":  # from root 3
            if not self.checkInInventoryOrInRoom(
                src.items.itemMap["ProductionManager"]
            ):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build production manager\nstatus: challenge in progress. Try with production manager in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build production manager\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["produceUniformStockpileManager"] = {
                    "text": "produce uniform stockpile manager"
                }
                self.knownBlueprints.append("AutoScribe")
                self.knownBlueprints.append("UniformStockpileManager")
                del self.availableChallenges["produceProductionManager"]

        elif (
            selection == "produceUniformStockpileManager"
        ):  # from produceProductionManager
            if not self.checkInInventoryOrInRoom(src.items.itemMap["UniformStockpileManager"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build uniform stockpile manager\nstatus: challenge in progress. Try with uniform stockpile manager in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: build uniform stockpile manager\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceUniformStockpileManager"]
        # <=
        # - produceFilledGooDispenser
        # - > strengthen mold growth
        # - R Container
        # - R BloomContainer
        # - R GrowthTank
        # - autoScribe
        # - > go to tile center
        # - copy commmand
        # - > decide inventory full
        # - > decide inventory empty
        # - > activate 4 directions
        # - gather sick bloom
        # - gather coal
        # - build fire crystals
        # - > go to food
        # - > decide food
        # - X tile completely covered in mold
        # - X tile with 9 living blooms
        # - X tile with 3 living sick blooms
        # - X goto north west edge
        # - X goto north east edge
        # - X goto south east edge
        # - X goto south west edge
        # - > go to west tile border
        # - > go to north tile border
        # - > go to east tile border
        # - > go to south tile border
        # - gather 9 sick bloom

        # => proudce 3 goo flasks

        elif selection == "produceFilledGooDispenser":  # NOT ASSIGNED
            itemFound = False
            for item in self.character.inventory + self.container.itemsOnFloor:
                if isinstance(item, src.items.itemMap["GooDispenser"]) and item.charges > 0:
                    itemFound = True
                    break
            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce goo\nstatus: challenge in progress. Try again with a goo dispenser with at least one charge in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce goo\nstatus: challenge completed.\n\nreward:\nNew Blueprint reciepe for growth tank\nCommand "STIMULATE MOLD GROWTh" dropped to the south\n\n'
                )

                self.knownBlueprints.append("GrowthTank")
                self.knownBlueprints.append("Container")
                self.knownBlueprints.append("BloomContainer")

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                        "a",
                        "j",
                        "a",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "s",
                        "s",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "w",
                        "w",
                        "a",
                        "j",
                        "a",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "s",
                        "s",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "d",
                        "d",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "s",
                        "s",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "w",
                        "w",
                        "d",
                        "j",
                        "d",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "s",
                        "s",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "w",
                        "w",
                        "d",
                        "j",
                        "d",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "w",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "s",
                        "s",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "s",
                        "j",
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "a",
                        "a",
                    ]
                )
                newCommand.extraName = "STIMULATE MOLD GROWTh"
                newCommand.description = "using this command will make you move around and pick mold to make it grow.\nIf there are things lying around they might be activated."
                self.container.addItems(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                del self.availableChallenges["produceFilledGooDispenser"]

        elif selection == "produceAutoScribe":  # from root 4
            if not self.checkInInventoryOrInRoom(src.items.itemMap["AutoScribe"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce auto scribe\nstatus: challenge in progress. Try with auto scribe in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: produce auto scribe\nstatus: challenge completed.\nreward: "GO TO TILE CENTEr" command dropped to south/below\n\n'
                )
                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "x",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GO TO TILE CENTEr"
                newCommand.description = "using this command will make you move to the center of the tile. If the path is blocked the command will not work properly."
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))
                self.availableChallenges["copyCommand"] = {"text": "copy command"}
                del self.availableChallenges["produceAutoScribe"]

        elif selection == "copyCommand":  # from produceAutoScribe
            itemCount = 0
            for item in self.character.inventory + self.container.itemsOnFloor:
                if isinstance(item, src.items.itemMap["Command"]) and item.command == [
                    "o",
                    "p",
                    "x",
                    "$",
                    "=",
                    "a",
                    "a",
                    "$",
                    "=",
                    "w",
                    "w",
                    "$",
                    "=",
                    "s",
                    "s",
                    "$",
                    "=",
                    "d",
                    "d",
                ]:
                    itemCount += 1

            if not itemCount > 2:
                self.submenue = src.interaction.TextMenu(
                    '\n\nchallenge: copy command\nstatus: challenge in progress. Try again with 3 copies of the "GO TO TILE CENTEr" command\n\ncomment:\nuse the auto scribe to copy commands.\nthe "GO TO TILE CENTEr" command was dropped as reward for the "produce auto scribe" challenge.\n\n'
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce auto scribe\nstatus: challenge completed.\n\n"
                )

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["%", "i", "a", "d"])
                newCommand.extraName = "DECIDE INVENTORY EMPTY EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is empty and will move you east otherwise"
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["%", "I", "a", "d"])
                newCommand.extraName = "DECIDE INVENTORY FULL EAST WESt"
                newCommand.description = "using this command will make you move west in case your inventory is completely filled and will move you east otherwise"
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["w", "%", "b", "d", "s"])
                newCommand.extraName = "DECIDE NORTH BLOCKED EAST STAy"
                newCommand.description = "using this command will make you move east in case the field to the north is not walkable and will make you stay in place otherwise"
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["w", "j"])
                newCommand.extraName = "ACTIVATE NORTh"
                newCommand.description = (
                    "using this command will make you activate to the north."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["s", "j"])
                newCommand.extraName = "ACTIVATE SOUTh"
                newCommand.description = (
                    "using this command will make you activate to the south."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["d", "j"])
                newCommand.extraName = "ACTIVATE EASt"
                newCommand.description = (
                    "using this command will make you activate to the east."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["a", "j"])
                newCommand.extraName = "ACTIVATE WESt"
                newCommand.description = (
                    "using this command will make you activate to the west."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                del self.availableChallenges["copyCommand"]

        # copy command
        elif selection == "gatherSickBloom":  # from root 4
            if not self.checkInInventoryOrInRoom(src.items.itemMap["SickBloom"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather sick bloom\nstatus: challenge in progress. Try with sick bloom in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather sick bloom\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["gatherCoal"] = {"text": "gather coal"}
                self.availableChallenges["challengerExplore1"] = {
                    "text": "explore mold"
                }
                self.availableChallenges["challengerGoTo1"] = {
                    "text": "explore terrain"
                }
                self.availableChallenges["gatherSickBlooms"] = {
                    "text": "gather sick blooms"
                }

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "f",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = (
                    "using this command will make you go to a food source nearby."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["%", "F", "a", "d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                del self.availableChallenges["gatherSickBloom"]

        elif selection == "gatherCoal":  # from gatherSickBloom
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Coal"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather coal\nstatus: challenge in progress. Try with coal in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather coal\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["produceFireCrystals"] = {
                    "text": "produce fire crystals"
                }
                self.knownBlueprints.append("FireCrystals")

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "C",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GOTO FOOd"
                newCommand.description = (
                    "using this command will make you go to a food source nearby."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["%", "F", "a", "d"])
                newCommand.extraName = "DECIDE FOOD NEARBY WEST EASt"
                newCommand.description = "using this command will make you go west in case there is a food source nearby and to the east otherwise."
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                del self.availableChallenges["gatherCoal"]

        elif selection == "produceFireCrystals":  # from gatherCoal
            if not self.checkInInventoryOrInRoom(src.items.itemMap["FireCrystals"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce fire crystals\nstatus: challenge in progress. Try with fire crystals in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce fire crystals\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceFireCrystals"]

        elif selection == "gatherSickBlooms":  # from gatherSickBloom
            if self.countInInventoryOrRoom(src.items.itemMap["SickBloom"]) < 9:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather sick blooms\nstatus: challenge in progress. Try with 9 sick blooms in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather sick blooms\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["gatherSickBlooms"]

        elif selection == "challengerExplore1":  # from gatherSickBloom
            secret = "epxplore1:-)"
            if "explore" not in self.challengeInfo["challengerGiven"]:
                new = src.items.itemMap["PortableChallenger"]()
                new.secret = secret
                new.challenges = ["3livingSickBlooms", "9livingBlooms", "fullMoldCover"]
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: explore mold\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\ncomment: do not loose or destroy the challenger\n\n"
                )
                self.challengeInfo["challengerGiven"].append("explore")
                self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))
            else:
                itemFound = None
                for item in self.character.inventory + self.container.itemsOnFloor:
                    if (
                        item.type == "PortableChallenger"
                        and item.done
                        and item.secret == secret
                    ):
                        itemFound = item

                if not itemFound:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: explore mold\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n"
                    )
                else:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: explore mold\nstatus: challenge completed.\n\n"
                    )
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerExplore1"]
        elif selection == "challengerGoTo1":  # from gatherSickBloom
            secret = "goto1:-)"
            if "goto" not in self.challengeInfo["challengerGiven"]:
                new = src.items.itemMap["PortableChallenger"]()
                new.secret = secret
                new.challenges = [
                    "gotoWestSouthTile",
                    "gotoEastSouthTile",
                    "gotoEastNorthTile",
                    "gotoWestNorthTile",
                ]
                self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))

                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: explore terrain\nstatus: challenge in progress. A portable challanger was outputted to the south. \nUse it and complete its challenges. Return afterwards.\n\n"
                )
                self.challengeInfo["challengerGiven"].append("goto")
            else:
                itemFound = None
                for item in self.character.inventory + self.container.itemsOnFloor:
                    if (
                        item.type == "PortableChallenger"
                        and item.done
                        and item.secret == secret
                    ):
                        itemFound = item

                if not itemFound:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: explore terrain\nstatus: challenge in progress. \nUse the portable challenger and complete its challenges.\nTry again with the completed portable challenger in you inventory.\n\n"
                    )
                else:
                    self.submenue = src.interaction.TextMenu(
                        "\n\nchallenge: explore terrain\nstatus: challenge completed.\n\n"
                    )
                    self.character.inventory.remove(itemFound)
                    del self.availableChallenges["challengerGoTo1"]

                    newCommand = src.items.itemMap["Command"]()
                    newCommand.setPayload(["@", "$", "=", "S", "E", "L", "F", "x", "a"])
                    newCommand.extraName = "GOTO WEST BORDEr"
                    newCommand.description = (
                        "using this command will make you go the west tile edge."
                    )
                    self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                    newCommand = src.items.itemMap["Command"]()
                    newCommand.setPayload(
                        [
                            "$",
                            ">",
                            "x",
                            "$",
                            "x",
                            "=",
                            "1",
                            "4",
                            "@",
                            "$",
                            "x",
                            "-",
                            "S",
                            "E",
                            "L",
                            "F",
                            "x",
                            "$",
                            "=",
                            "x",
                            "a",
                            "<",
                            "x",
                        ]
                    )
                    newCommand.extraName = "GOTO EAST BORDEr"
                    newCommand.description = (
                        "using this command will make you go the east tile edge."
                    )
                    self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                    newCommand = src.items.itemMap["Command"]()
                    newCommand.setPayload(["@", "$", "=", "S", "E", "L", "F", "y", "w"])
                    newCommand.extraName = "GOTO NORTH BORDEr"
                    newCommand.description = (
                        "using this command will make you go the north tile edge."
                    )
                    newCommand.xPosition = self.xPosition
                    newCommand.yPosition = self.yPosition + 1
                    self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                    newCommand = src.items.itemMap["Command"]()
                    newCommand.setPayload(
                        [
                            "$",
                            ">",
                            "y",
                            "$",
                            "y",
                            "=",
                            "1",
                            "4",
                            "@",
                            "$",
                            "y",
                            "-",
                            "S",
                            "E",
                            "L",
                            "F",
                            "y",
                            "$",
                            "=",
                            "y",
                            "s",
                            "<",
                            "y",
                        ]
                    )
                    newCommand.extraName = "GOTO SOUTH BORDEr"
                    newCommand.description = (
                        "using this command will make you go the south tile edge."
                    )
                    self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

        # - build growth tank
        # - build NPC
        # - > go to scrap
        # - > go to character
        # - gather corpse
        # - > go to corpse
        # - > decide corpse
        # - build item upgrader
        # - upgrade Command to 4
        # - upgrade BloomContainer 3
        # - upgrade Sheet to 4
        # - upgrade Machine
        # - memory cell
        # learn command
        # => learn 25 commands

        elif selection == "produceGrowthTank":  # from root 5
            if not self.checkInInventoryOrInRoom(src.items.itemMap["GrowthTank"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce growth tank\nstatus: challenge in progress. Try with growth tank in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce growth tank\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["spawnNPC"] = {"text": "spawn NPC"}
                del self.availableChallenges["produceGrowthTank"]

        elif selection == "spawnNPC":  # from produceGrowthTank
            if len(self.container.characters) < 2:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: spawn NPC\nstatus: challenge in progress. Try with a NPC in the room.\n\n"
                )

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "s",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GOTO SCRAp"
                newCommand.description = (
                    "using this command will make you go to scrap nearby."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "c",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GOTO CHARACTEr"
                newCommand.description = (
                    "using this command will make you go to a character nearby."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: spawn NPC\nstatus: challenge completed.\n\n"
                )

        elif selection == "gatherCorpse":  # from spawnNPC
            if not self.checkInInventoryOrInRoom(src.items.itemMap["Corpse"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather corpse\nstatus: challenge in progress. Try with corpse in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather corpse\nstatus: challenge completed.\n\n"
                )

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(
                    [
                        "o",
                        "p",
                        "M",
                        "$",
                        "=",
                        "a",
                        "a",
                        "$",
                        "=",
                        "w",
                        "w",
                        "$",
                        "=",
                        "s",
                        "s",
                        "$",
                        "=",
                        "d",
                        "d",
                    ]
                )
                newCommand.extraName = "GOTO CORPSe"
                newCommand.description = (
                    "using this command will make you go to a corpse nearby."
                )
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                newCommand = src.items.itemMap["Command"]()
                newCommand.setPayload(["%", "M", "a", "d"])
                newCommand.extraName = "DECIDE CORPSE EAST WESt"
                newCommand.description = "using this command will make you move west in case a corpse is nearby and will move you east otherwise"
                self.container.addItem(newCommand,(self.xPosition,self.yPosition+1,self.zPosition))

                del self.availableChallenges["gatherCorpse"]

        elif selection == "produceItemUpgrader":  # from root 5
            if not self.checkInInventoryOrInRoom(src.items.itemMap["ItemUpgrader"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce item upgrader\nstatus: challenge in progress. Try with item upgrader in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce item upgrader\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceItemUpgrader"]

        elif selection == "upgradeCommand4":  # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.container.itemsOnFloor:
                if item.type == "Command" and item.level >= 4:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade command to level 4\nstatus: challenge in progress. Try with a command with level 4 in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade command to level 4\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeBloomContainer3":  # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.container.itemsOnFloor:
                if item.type == "BloomContainer" and item.level >= 3:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade bloom container to level 3\nstatus: challenge in progress. Try with a bloom container with level 3 in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade bloom container to level 3\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeSheet4":  # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.container.itemsOnFloor:
                if item.type == "Sheet" and item.level >= 4:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade sheet to level 4\nstatus: challenge in progress. Try with a sheet with level 4 in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade sheet to level 4\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["upgradeCommand4"]

        elif selection == "upgradeMachine2":  # from produceItemUpgrader
            itemFound = None
            for item in self.character.inventory + self.container.itemsOnFloor:
                if item.type == "Machine" and item.level >= 2:
                    itemFound = item

            if not itemFound:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade machine to level 2\nstatus: challenge in progress. Try with a machine with level 2 in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: upgrade machine to level 2\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["upgradeCommand4"]

        # - gather posion bloom
        # - produce room builder
        # - build floor plate
        # X clear tile x/y
        # > floor right empty
        # build room
        # X goto map center
        # tile with 9 living sick blooms
        # produce goo flask with >100 charges
        #
        # => build mini mech

        elif selection == "gatherPoisonBloom":  # from root 6
            if self.countInInventoryOrRoom(src.items.itemMap["PoisonBloom"]) < 9:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with poison bloom in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["gatherPoisonBloom"]

        elif selection == "produceRoomBuilder":  # from root 6
            if not self.checkInInventoryOrInRoom(src.items.itemMap["RoomBuilder"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce room builder\nstatus: challenge in progress. Try with room builder in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce room builder\nstatus: challenge completed.\n\n"
                )
                self.availableChallenges["produceFloorPlate"] = {
                    "text": "produce floor plate"
                }
                del self.availableChallenges["produceRoomBuilder"]

        elif selection == "produceFloorPlate":  # from produceRoomBuilder
            if self.checkInInventoryOrRoom(src.items.itemMap["FloorPlate"]):
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce floor plates\nstatus: challenge in progress. Try with 9 floor plates in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: produce floor plates\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["produceFloorPlate"]

        # build map to room
        # build working map (drop marker in 5 rooms with requirement, make random star movement)
        # gather poision blooms

        elif selection == "gatherPoisonBlooms":  # from gatherPoisonBloom
            if self.countInInventoryOrRoom(src.items.itemMap["PoisonBloom"]) < 5:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather poison bloom\nstatus: challenge in progress. Try with 5 poison blooms in your inventory.\n\n"
                )
            else:
                self.submenue = src.interaction.TextMenu(
                    "\n\nchallenge: gather poison bloom\nstatus: challenge completed.\n\n"
                )
                del self.availableChallenges["gatherPoisonBlooms"]

        self.character.macroState["submenue"] = self.submenue

    def countInInventory(self, itemType):
        """
        count items of a certain type from the characters inventory

        Parameters:
            itemType: the typ of item to search for
        Returns:
            the number of items found
        """

        num = 0
        for item in self.character.inventory:
            if isinstance(item, itemType):
                num += 1
        return num

    def countInInventoryOrRoom(self, itemType):
        """
        count items of a certain type from the characters inventory or the local room

        Parameters:
            itemType: the typ of item to search for
        Returns:
            the number of items found
        """

        num = self.countInInventory(itemType)
        for item in self.container.itemsOnFloor:
            if isinstance(item, itemType):
                num += 1
        return num

    def checkListAgainstInventory(self, itemTypes):
        """
        check whether a characters inventory contains items of some types

        Parameters:
            itemTypes: the items to search for
        Returns:
            a list of items not found
        """

        for item in self.character.inventory:
            if item.type in itemTypes:
                itemTypes.remove(item.type)
        return itemTypes

    def checkListAgainstInventoryOrIsRoom(self, itemTypes):
        """
        check whether a characters inventory and local room contains items of some types

        Parameters:
            itemTypes: the items to search for
        Returns:
            a list of items not found
        """

        itemTypes = self.checkListAgainstInventory(itemTypes)
        if itemTypes:
            for item in self.container.itemsOnFloor:
                if item.type in itemTypes:
                    itemTypes.remove(item.type)
        return itemTypes

    # abstraction: should use character class functionality
    def checkInInventory(self, itemType):
        """
        checks whether a characters inventory contains items of a certain type

        Parameters:
            itemType: the type of item to search for
        Returns:
            flag indication whether or not an item was found
        """

        for item in self.character.inventory:
            if isinstance(item, itemType):
                return True
        return False

    def checkInInventoryOrInRoom(self, itemType):
        """
        checks whether a characters inventory or local room contains items of a certain type

        Parameters:
            itemType: the type of item to search for
        Returns:
            flag indication whether or not an item was found
        """

        if self.checkInInventory(itemType):
            return True
        for item in self.container.itemsOnFloor:
            if isinstance(item, itemType):
                return True

        return False

    def basicInfo(self):
        """
        show a menu to get basic information from
        """

        options = []

        options.append(("movement", "movement"))
        options.append(("interaction", "interaction"))

        if self.gooChallengeDone:
            options.append(("machines", "machines"))

        if self.gooChallengeDone:
            options.append(("food", "food"))

        if self.blueprintChallengeDone:
            options.append(("automation", "automation"))

        if self.machineChallengeDone:
            options.append(("blueprints", "blueprint reciepes"))

        self.submenue = src.interaction.SelectionMenu(
            "select the information you need", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level1_selection

    def level1_selection(self):
        """
        show level1 information
        """

        selection = self.submenue.getSelection()

        if selection == "movement":
            self.submenue = src.interaction.TextMenu(
                "\n\n * press ? for help\n\n * press a to move left/west\n * press w to move up/north\n * press s to move down/south\n * press d to move right/east\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "interaction":
            self.submenue = src.interaction.TextMenu(
                "\n\n * press k to pick up\n * press l to pick up\n * press i to view inventory\n * press @ to view your stats\n * press j to activate \n * press e to examine\n * press ? for help\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with it\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "machines":
            options = []

            options.append(("level1_machines_bars", "metal bar production"))
            if self.metalbarChallengeDone:
                options.append(("level1_machines_simpleItem", "simple item production"))
            if self.sheetChallengeDone:
                options.append(("level1_machines_machines", "machine production"))
            if self.machineChallengeDone:
                options.append(
                    ("level1_machines_machineMachines", "machine machine production")
                )
                options.append(("level1_machines_blueprints", "blueprint production"))
                # options.append(("level1_machines_food","food production"))
                # options.append(("level1_machines_energy","energy production"))

            self.submenue = src.interaction.SelectionMenu(
                "select the information you need", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Machines
        elif selection == "food":
            options = []

            options.append(("food_basics", "food basics"))
            if "food/moldfarming" in self.knownInfos:
                options.append(("food_moldfarming", "mold farming"))

            self.submenue = src.interaction.SelectionMenu(
                "select the information you need", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Food
        elif selection == "automation":
            options = []

            options.append(("commands", "creating commands"))
            if self.commandChallengeDone:
                options.append(("multiplier", "multiplier"))
            if self.activateChallengeDone:
                options.append(("notes", "notes"))
            if self.blueprintChallengeDone:
                options.append(("maps", "maps"))

            self.submenue = src.interaction.SelectionMenu(
                "select the information you need", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.stepLevel1Automation
        elif selection == "blueprints":
            text = "\n\nknown blueprint recieps:\n\n"

            shownText = False
            if "Rod" in self.knownBlueprints:
                text += " * rod             <= rod\n"
                shownText = True
            if "Radiator" in self.knownBlueprints:
                text += " * radiator        <= radiator\n"
                shownText = True
            if "Mount" in self.knownBlueprints:
                text += " * mount           <= mount\n"
                shownText = True
            if "Stripe" in self.knownBlueprints:
                text += " * stripe          <= stripe\n"
                shownText = True
            if "Bolt" in self.knownBlueprints:
                text += " * bolt            <= bolt\n"
                shownText = True
            if "Sheet" in self.knownBlueprints:
                text += " * sheet           <= sheet\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Frame" in self.knownBlueprints:
                text += " * frame           <= rod + metal bars\n"
                shownText = True
            if "Heater" in self.knownBlueprints:
                text += " * heater          <= radiator + metal bars\n"
                shownText = True
            if "Connector" in self.knownBlueprints:
                text += " * connector       <= mount + metal bars\n"
                shownText = True
            if "Pusher" in self.knownBlueprints:
                text += " * pusher          <= stripe + metal bars\n"
                shownText = True
            if "Puller" in self.knownBlueprints:
                text += " * puller          <= bolt + metal bars\n"
                shownText = True
            if "Tank" in self.knownBlueprints:
                text += " * tank            <= sheet + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Case" in self.knownBlueprints:
                text += " * case            <= frame + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Wall" in self.knownBlueprints:
                text += " * wall            <= metal bars\n"
                shownText = True
            if "Door" in self.knownBlueprints:
                text += " * door            <= connector\n"
                shownText = True
            if "FloorPlate" in self.knownBlueprints:
                text += " * floor plate     <= sheet + rod + bolt\n"
                shownText = True
            if "RoomBuilder" in self.knownBlueprints:
                text += " * room builder    <= puller\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "BloomShredder" in self.knownBlueprints:
                text += " * bloom shredder  <= bloom\n"
                shownText = True
            if "BioPress" in self.knownBlueprints:
                text += " * bio press       <= bio mass\n"
                shownText = True
            if "GooFlask" in self.knownBlueprints:
                text += " * goo flask       <= tank\n"
                shownText = True
            if "GooDispenser" in self.knownBlueprints:
                text += " * goo dispenser   <= flask\n"
                shownText = True
            if "SporeExtractor" in self.knownBlueprints:
                text += " * spore extractor <= bloom + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "GooProducer" in self.knownBlueprints:
                text += " * goo producer    <= press cake\n"
                shownText = True
            if "GrowthTank" in self.knownBlueprints:
                text += " * growth tank     <= goo flask + tank\n"
                shownText = True
            if "FireCrystals" in self.knownBlueprints:
                text += " * fire crystals   <= coal + sick bloom\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "ProductionManager" in self.knownBlueprints:
                text += " * production manager <= memory cell + connector + command\n"
                shownText = True
            if "AutoFarmer" in self.knownBlueprints:
                text += " * auto farmer     <= memory cell + bloom + sick bloom\n"
                shownText = True
            if "UniformStockpileManager" in self.knownBlueprints:
                text += " * uniform stockpile manager <= memory cell + connector + floor plate\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "ScrapCompactor" in self.knownBlueprints:
                text += " * scrap compactor <= scrap\n"
                shownText = True
            if "Scraper" in self.knownBlueprints:
                text += " * scraper         <= scrap + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            shownText = False
            if "Container" in self.knownBlueprints:
                text += " * container       <= case + sheet\n"
                shownText = True
            if "BloomContainer" in self.knownBlueprints:
                text += " * bloom container <= case + sheet + bloom\n"
                shownText = True
            if "AutoScribe" in self.knownBlueprints:
                text += " * auto scribe     <= command\n"
                shownText = True
            if "MemoryCell" in self.knownBlueprints:
                text += " * memory cell     <= connector + metal bars\n"
                shownText = True
            if shownText:
                text += "\n"

            text += "\n\n"
            self.submenue = src.interaction.TextMenu(text)
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Food(self):
        """
        show level1 information about food
        """

        selection = self.submenue.getSelection()

        if selection == "food_basics":
            self.submenue = src.interaction.TextMenu(
                "\n\nYou need to eat/drink regulary to not starve\nIf you do not drink for 1000 ticks you will starve,\n\nMost actions will take a tick. So you will need to drink every 1000 steps or you will starve.\n\nDrinking/Eating usually happens automatically as long as you have something eatable in you inventory.\n\nYou check your satiation in your character screen or on the lower right edge of the screen\n\nThe most common food is goo stored in a goo flask. Every sip from a goo flask gains you 1000 satiation.\nWith a maximum or 100 charges a full goo flask can hold enough food for up to 100000 moves.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        if selection == "food_moldfarming":
            self.submenue = src.interaction.TextMenu(
                "\n\nMold is a basis for goo production and can be eaten directly.\nMold grows in patches and develop blooms.\nMold blooms can be collected and give 100 satiation when eaten or be processed into goo.\n\ngoo production:\n * Blooms can be processed into bio mass using the bloom shredder.\n * Bio mass can be processed into press cakes using the bio press.\n * press cake can be used to produce goo\n * The goo producer needs a goo dispenser to store the goo in.\n * The goodispenser allows you fill your flask.\n\nNew Mold patches can be started using mold spores. Growth in stagnant mold patches can be restarted by picking some sprouts or blooms\n\n"
            )
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Automation(self):
        """
        show level1 information about automation
        """

        selection = self.submenue.getSelection()

        if selection == "commands":
            self.submenue = src.interaction.TextMenu(
                '\n\nCommands are a way of automating actions. A character will run a command after activating it.\n\nThe easiest way of creating a command is:\n * drop a sheet on the floor\n * activate the sheet on the floor\n * select "create a written command"\n * select "start recording"\n * do the action\n * return to the sheet on the ground\n * activate the sheet again\n\nTo do the recorded action activate the command on the floor.\nWhile running the command you are not able the control your character and the game will speed up the longer the command runs.\n\nYou can press ctrl-d to abort running a commmand.'
            )
            self.character.macroState["submenue"] = self.submenue
        if selection == "multiplier":
            self.submenue = src.interaction.TextMenu(
                "\n\nThe multiplier allow to do something x times. For example walking 5 steps to the right, waiting 100 turns, activating commands 3 times\n\nTo use multiplier type in the number of times you want to do something and the action.\n\nexamples:\n\n5d => 5 steps to the right\n100. => wait a hundred turns\n3j => activating a command you are standing on 3 times\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        if selection == "notes":
            self.submenue = src.interaction.TextMenu(
                "\n\nNotes do not do anything except holding a text.\n\nYou can use this to place reminder on how things work and similar\n\nnotes can be created from sheets\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        if selection == "maps":
            self.submenue = src.interaction.TextMenu(
                '\n\nMaps allow for easier movement on a wider scale. Maps store routes between points.\n\nIf you are at the starting point of a route you can use the map to walk to the routes end point\nFor example if a map holds the route between point a and b you can use the map to travel to point b if you are at point a.\nMarking the startpoints of your routes is recomended, since you have stand at the exact coordinate to walk a route,\n\nYou create a route by: \n * moving to the start location of the route.\n * using the map\n * select the "add route" option\n * move to your target location\n * use the map again\n * select the "add route" option again.\n\nSince recording routes behaves like recording commands you can include actions like opening/closing doors or getting equipment.\nThe routes are not adapting to change and a closed door might disrupt your route.\n\n'
            )
            self.character.macroState["submenue"] = self.submenue

    def stepLevel1Machines(self):
        """
        show level1 information about machines
        """

        selection = self.submenue.getSelection()

        if selection == "level1_machines_bars":
            self.submenue = src.interaction.TextMenu(
                "\n\nMetal bars are used to produce most things. You can produce metal bars by using a scrap compactor.\nA scrap compactor is represented by RC. Place the scrap to the left/west of the scrap compactor.\nActivate it to produce a metal bar. The metal bar will be outputted to the right/east of the scrap compactor.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_simpleItem":
            self.submenue = src.interaction.TextMenu(
                "\n\nMost items are produced in machines. A machine usually produces only one type of item.\nThese machines are shown as X\\. Place raw materials to the west/left/north/above of the machine and activate it to produce the item.\n\nYou can examine machines to get a more detailed descripton.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = src.interaction.TextMenu(
                "\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n"
            )
        elif selection == "level1_machines_machines":
            self.submenue = src.interaction.TextMenu(
                "\n\nThe machines are produced by a machine-machine. The machine machines are shown as M\\\nMachine-machines require blueprints to produce machines.\n\nTo produce a machine for producing rods for example a blueprint for rods is required.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_blueprints":
            self.submenue = src.interaction.TextMenu(
                "\n\nBlueprints are produced by a blueprinter.\nThe blueprinter takes items and a sheet as input and produces blueprints.\n\nDifferent items or combinations of items produce blueprints for different things.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_machineMachines":
            self.submenue = src.interaction.TextMenu(
                "\n\nMachine-machines can only be produced by the production artwork. The production artwork is represented by ßß.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_food":
            self.submenue = src.interaction.TextMenu(
                "\n\nFood production is based on vat maggots. Vat maggots can be harvested from trees.\nActivate the tree and a vat maggot will be dropped to the east of the tree.\n\nvat maggots are processed into bio mass using a maggot fermenter.\nPlace 10 vat maggots left/west to the maggot fermenter and activate it to produce 1 bio mass.\n\nThe bio mass is processed into press cake using a bio press.\nPlace 10 biomass left/west to the bio press and activate it to produce one press cake.\n\nThe press cake is processed into goo by a goo producer. Place 10 press cakes west/left to the goo producer and a goo dispenser to the right/east of the goo producer.\nActivate the goo producer to add a charge to the goo dispenser.\n\nIf the goo dispenser is charged, you can fill your flask by having it in your inventory and activating the goo dispenser.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level1_machines_energy":
            self.submenue = src.interaction.TextMenu(
                "\n\nEnergy production is steam based. Steam is generated heating a boiler.\nA boiler is represented by OO or 00.\n\nA boiler is heated by placing a furnace next to it and fireing it. A furnace is fired by activating it while having coal in you inventory.\nA furnace is represented by oo or öö.\n\nCoal can be harvested from coal mines. Coal mines are represented by &c.\nActivate it and a piece of coal will be outputted to the right/east.\ncoal is represented by sc.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue

    def l2Info(self):
        """
        show selection for level 2 information
        """

        options = []

        options.append(("level2_multiplier", "action multipliers"))
        options.append(("level2_rooms", "room creation"))

        self.submenue = src.interaction.SelectionMenu(
            "select the information you need", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level2_selection

    def level2_selection(self):
        """
        show level 2 information
        """

        selection = self.submenue.getSelection()

        if selection == "level2_multiplier":
            self.submenue = src.interaction.TextMenu(
                "\n\nyou can use multiplicators with commands. Typing a number followed by a command will result in the command to to be run multiple times\n\nTyping 10l is the same as typing llllllllll.\nThis will result in you dropping 10 items from your inventory\n\nThe multiplicator only applies to the following command.\nTyping 3aj will be expanded to aaaj.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level2_rooms":
            self.submenue = src.interaction.TextMenu(
                "\n\nmany machines only work within rooms. You can build new rooms.\nRooms are rectangular and have one door.\n\nYou can build new rooms. Prepare by placing walls and a door in the form of a rectangle on the ground.\n\nPlace a room builder within the walls and activate it to create a room from the basic items.\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: " + selection)

    def l3Info(self):
        """
        show selection for level 3 information
        """

        options = []

        options.append(("level3_macrosBasic", "macro basics"))
        options.append(("level3_macrosExtra", "macro extra"))
        options.append(("level3_macrosShortcuts", "macro shortCuts"))

        self.submenue = src.interaction.SelectionMenu(
            "select the information you need", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level3_selection

    def level3_selection(self):
        """
        show level 3 information
        """

        selection = self.submenue.getSelection()

        if selection == "level3_macrosBasic":
            self.submenue = src.interaction.TextMenu(
                "\n\nyou can use macros to automate task. This means you can record and replay keystrokes.\n\nTo record a macro press - to start recording and press the key to record to.\nAfterwards do your movement and press - to stop recording.\nTo replay the recorded macro press _ and the key the macro was recorded to.\n\nFor example typing -kasdw- will record asdw to the buffer k\nPressing _k afterwards will be the same as pressing asdw\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosExtra":
            self.submenue = src.interaction.TextMenu(
                "\n\nMacros can be combined with each other. You can do this by replaying a macro while recording a macro\nFor example -qaaa- will record aaa to the buffer q.\nPressing -wddd_q- will record ddd_q to the buffer w. Pressing _w will be the same as dddaaa\nThe macro are referenced not copied. This means overwriting a macro will change alle macros referencing it. \n\nYou also can use multipliers within and with macros.\nPressing 5_q for example is the same as _q_q_q_q_q\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        elif selection == "level3_macrosShortcuts":
            self.submenue = src.interaction.TextMenu(
                "\n\nThere are some shortcuts that are usefull in combination with macros.\n\nctrl-d - aborts running the current macro\nctrl-p - pauses/unpauses running the current macro\nctrl-k writes macros fo disk\nctrl-o loads macros from disk\nctrl-x - saves and exits the game without interrupting running macros\n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: " + selection)

    def l4Info(self):
        """
        show selection for level 4 information
        """

        options = []

        options.append(("level4_npcCreation", "npc creation"))
        options.append(("level4_npcControl", "npc control"))
        options.append(("level4_npcCreation", "npc creation"))

        self.submenue = src.interaction.SelectionMenu(
            "select the information you need", options
        )
        self.character.macroState["submenue"] = self.submenue
        self.character.macroState["submenue"].followUp = self.level4_selection

    def level4_selection(self):
        """
        show level 4 information
        """

        if selection == "level4_npcCreation":
            self.submenue = src.interaction.TextMenu(
                "\n\nYou can spawn new npcs. Npcs work just like your main character\nNpcs are generated from growth tanks. You need to activate the growth tank with a full flask in your inventory\nActivate the filled growth tank to spwan the npc. \n\n"
            )
            self.character.macroState["submenue"] = self.submenue
        else:
            self.character.addMessage("unknown selection: " + selection)

    def getState(self):
        state = super().getState()
        state["availableChallenges"] = self.availableChallenges
        state["knownBlueprints"] = self.knownBlueprints
        state["knownInfos"] = self.knownInfos
        return state

    def setState(self, state):
        """
        load from semi serialised state

        Parameters:
            state: the state to load
        """

        super().setState(state)
        self.availableChallenges = state["availableChallenges"]
        self.knownBlueprints = state["knownBlueprints"]
        self.knownInfos = state["knownInfos"]

    def getLongInfo(self):
        """
        returns a description text

        Returns:
            the description text
        """

        text = """

This machine hold the information and practices needed to build a base.

Activate/Apply it to complete challenges and gain more information.

"""
        return text

src.items.addType(AutoTutor)
