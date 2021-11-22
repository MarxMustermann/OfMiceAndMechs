import src


class Spawner(src.items.Item):
    type = "Spawner"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.fireCrystals)

        self.name = "spawner"
        self.charges = 1

    def apply(self, character):

        if not self.terrain:
            character.addMessage("this has to be placed outside to be used")
            return
        corpses = []
        for item in character.inventory:
            if item.type == "Corpse":
                corpses.append(item)

        for corpse in corpses:
            self.charges += 1
            character.inventory.remove(corpse)

        if self.charges:
            event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 100
            )
            event.setCallback({"container": self, "method": "spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        character = characters.Character(
            src.canvas.displayChars.staffCharactersByLetter["a".lower()],
            name="a",
        )

        character.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "NaiveDropQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest" "NaiveDropQuest",
            "DropQuestMeta",
            "NaiveMurderQuest",
        ]

        character.inventory.append(Tumbler())
        character.inventory.append(BackTracker())
        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["WALKTo"] = splitCommand("$=aa$=ww$=ss$=dd")
        """
        character.macroState["macros"]["MURDEr"] = splitCommand("ope_WALKTomijj_u")
        character.macroState["macros"]["u"] = splitCommand("%E_i_o")
        character.macroState["macros"]["i"] = splitCommand("_MURDEr")
        character.macroState["macros"]["o"] = splitCommand("%c_p_a")
        character.macroState["macros"]["p"] = splitCommand("_GETBODYs")
        character.macroState["macros"]["a"] = splitCommand("ijj_u")
        character.macroState["macros"]["s"] = splitCommand("_u")
        character.macroState["macros"]["GETBODYs"] = splitCommand("opM_WALKTokijsjajijsjijj_u")
        character.macroState["macros"]["STARt"] = splitCommand("ijsj_a")
        character.macroState["macros"]["m"] = splitCommand("_STARt")
        """
        character.macroState["macros"]["_GOTOTREe"] = splitCommand("opt_WALKTo")
        character.macroState["macros"]["_RANDOMWALk"] = splitCommand("ijj")
        character.macroState["macros"]["_a"] = splitCommand("_RANDOMWALk")
        character.macroState["macros"]["m"] = splitCommand("ijj_GOTOTREe")

        character.runCommandString("_m",clear=True)
        character.satiation = 100000
        self.container.addCharacter(character, self.xPosition + 1, self.yPosition)

        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick + 100
        )
        event.setCallback({"container": self, "method": "spawn"})
        self.terrain.addEvent(event)

        self.charges -= 1

    def getLongInfo(self):
        return """
item: Spawner

description:
spawner with %s charges
""" % (
            self.charges
        )


src.items.addType(Spawner)
