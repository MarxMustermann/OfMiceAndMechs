import cProfile

import src


class PerformanceTester(src.items.Item):
    """
    """


    type = "PerformanceTester"

    def __init__(self, name="PerformanceTester", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="PL", name=name)

        self.applyOptions.extend(
                        [
                                                                ("test1000", "test 1000"),
                                                                ("test100", "test 100"),
                                                                ("test10", "test 10"),
                        ]
                        )
        self.applyMap = {
                    "test1000": self.test1000,
                    "test100": self.test100,
                    "test10": self.test10,
                        }

        self.faction = ""

    def test1000(self,character):
        self.teststart(character,1000)

    def test100(self,character):
        self.teststart(character,100)

    def test10(self,character):
        self.teststart(character,10)

    def teststart(self,character,count):
        submenue = src.menuFolder.ViewNPCsMenu.ViewNPCsMenu(self)
        character.macroState["submenue"] = submenue
        self.faction = character.faction

        params = {"character":character}

        character.timeTaken += count
        submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu("testing",targetParamName="abortKey")
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"test_end","params":params}
        character.runCommandString(".")

        self.profiler = cProfile.Profile()
        self.profiler.enable()

    def test_end(self,extraInfo):
        character = extraInfo["character"]
        self.profiler.dump_stats("perfLog.prof")
        self.profiler = None
        character.addMessage("-------------------- end")
        pass

src.items.addType(PerformanceTester)
