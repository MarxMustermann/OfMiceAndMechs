import src
import random


class SickBloom(src.items.Item):
    type = "SickBloom"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.sickBloom)

        self.name = "sick bloom"
        self.walkable = True
        self.charges = 1
        self.dead = False
        self.attributesToStore.extend(["charges", "dead"])

    def apply(self, character):
        if self.charges and not self.dead:
            if isinstance(character, src.characters.Monster):
                if character.phase == 1:
                    character.satiation += 300
                    if character.satiation > 1000:
                        character.satiation = 1000
                    self.spawn()
                    self.charges -= 1
                    self.dead = True
                elif character.phase == 2:
                    character.enterPhase3()
                    self.charges -= 1
                    self.destroy(generateSrcap=False)
                else:
                    character.satiation += 400
                    self.charges -= 1
            else:
                self.spawn()
                character.satiation += 100
                if character.satiation > 1000:
                    character.satiation = 1000
        else:
            character.satiation += 100
            if character.satiation > 1000:
                character.satiation = 1000
            self.destroy(generateSrcap=False)
        character.addMessage("you eat the sick bloom and gain 100 satiation")

    def pickUp(self, character):
        self.bolted = False
        self.dead = True
        self.charges = 0
        super().pickUp(character)

    def startSpawn(self):
        event = src.events.RunCallbackEvent(
            src.gamestate.gamestate.tick
            + (2 * self.xPosition + 3 * self.yPosition + src.gamestate.gamestate.tick)
            % 2500,
        )
        event.setCallback({"container": self, "method": "spawn"})
        self.container.addEvent(event)

    def spawn(self):
        if not self.charges:
            return

        if self.dead:
            return

        character = src.characters.Monster()

        character.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "NaiveMurderQuest",
            "NaiveDropQuest",
        ]

        character.faction = "monster"

        def splitCommand(newCommand):
            splittedCommand = []
            for char in newCommand:
                splittedCommand.append(char)
            return splittedCommand

        character.macroState["macros"]["w"] = splitCommand("wj")
        character.macroState["macros"]["a"] = splitCommand("aj")
        character.macroState["macros"]["s"] = splitCommand("sj")
        character.macroState["macros"]["d"] = splitCommand("dj")

        counter = 1
        command = ""
        directions = ["w", "a", "s", "d"]
        while counter < 8:
            command += "j%s_%sk" % (
                random.randint(1, counter * 4),
                directions[random.randint(0, 3)],
            )
            counter += 1
        character.macroState["macros"]["m"] = splitCommand(command + "_m")

        character.macroState["commandKeyQueue"] = [("_", []), ("m", [])]
        character.satiation = 10
        if self.container:
            self.container.addCharacter(character, self.xPosition, self.yPosition)

        self.charges -= 1

    def getLongInfo(self):
        satiation = 115
        if self.dead:
            satiation = 100
        return """
item: SickBloom

description:
This is a mold bloom. Its spore sacks are swollen and developed a protective shell

you can eat it to gain %s satiation.
""" % (
            satiation
        )

    def destroy(self, generateSrcap=True):

        if not self.dead:
            new = src.items.itemMap["Mold"]()
            self.container.addItem(new, self.getPosition())
            new.startSpawn()

        super().destroy(generateSrcap=False)


src.items.addType(SickBloom)
