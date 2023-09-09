try:
    import urwid
    AttrSpec = urwid.AttrSpec
except:
    class AttrSpec(object):
        """
        dumy object behaving like an urwid attribute
        this is used to prevent crashes
        """

        def __init__(self, fg, bg):
            """
            store basic attriutes

            Parameters:
                fg: foreground color
                bg: background color
            """

            self.fg = fg
            self.bg = bg

        def get_rgb_values(self):
            def convertValue(value):
                try:
                    return int(value)*16
                except:
                    if value == "a":
                        return 10*16
                    if value == "b":
                        return 11*16
                    if value == "c":
                        return 12*16
                    if value == "d":
                        return 13*16
                    if value == "e":
                        return 14*16
                    if value == "f":
                        return 15*16
            
            color = []
            if self.fg[0] == "#":
                color.append(convertValue(self.fg[1]))
                color.append(convertValue(self.fg[2]))
                color.append(convertValue(self.fg[3]))
            elif self.fg == "black":
                color.append(0)
                color.append(0)
                color.append(0)
            else:
                color.append(None)
                color.append(None)
                color.append(None)
                print(self.fg)
            if self.bg[0] == "#":
                color.append(convertValue(self.bg[1]))
                color.append(convertValue(self.bg[2]))
                color.append(convertValue(self.bg[3]))
            elif self.bg == "black":
                color.append(0)
                color.append(0)
                color.append(0)
            else:
                color.append(None)
                color.append(None)
                color.append(None)
                print(self.bg)
            return tuple(color)


landmine = (AttrSpec("#f00", "black"), "_~")
sunScreen = (AttrSpec("#420", "black"), "oo")
healingStation = (AttrSpec("#f00", "black"), "HS")
forceField2 = (AttrSpec("#3f3", "black"), "##")
staticCrystal = (AttrSpec("#aaf", "black"), "/\\")
staticSpark = (AttrSpec("#aaf", "black"), "*-")
sparkPlug = (AttrSpec("#aaf", "black"), "O-")
ripInReality = (AttrSpec("#aaf", "black"), "|#")
productionManager = (AttrSpec("#aaa", "black"), "PM")
autoFarmer = (AttrSpec("#fff", "#252"), "::")
portableChallenger = (AttrSpec("#aaa", "black"), "pc")
typedStockpileManager = (AttrSpec("#aaa", "black"), "ST")
uniformStockpileManager = (AttrSpec("#aaa", "black"), "SU")
jobOrder = (AttrSpec("#33f", "black"), "j#")
jobBoard = (AttrSpec("#33f", "black"), "JB")
itemUpgrader = (AttrSpec("#aaa", "black"), "iU")
blueprint = (AttrSpec("#aaa", "black"), "bd")
command = (AttrSpec("#aaa", "black"), "c#")
map = (AttrSpec("#aaa", "black"), "m#")
note = (AttrSpec("#aaa", "black"), "n#")
bloomShredder = (AttrSpec("#fff", "black"), "%>")
corpseShredder = (AttrSpec("#d88", "black"), "%>")
sporeExtractor = (AttrSpec("#fff", "black"), "%o")
bloomContainer = (AttrSpec("#fff", "black"), "[H")
container = (AttrSpec("#446", "black"), "[H")
moldFeed = (AttrSpec("#d00", "black"), "<~")
seededMoldFeed = (AttrSpec("#436", "#600"), ";;")
moss = (AttrSpec("#030", "black"), ",.")
moldSpore = (AttrSpec("#436", "black"), ",.")
monster_spore = (AttrSpec("#030", "black"), "🝆 ")
monster_feeder = (AttrSpec("#252", "black"), "🝆~")
monster_grazer = (AttrSpec("#484", "black"), "🝆=")
monster_corpseGrazer = (AttrSpec("#824", "black"), "🝆-")
monster_hunter = (AttrSpec("#f48", "black"), "🝆>")
monster_exploder = (AttrSpec("#3f3", "black"), "🝆%")
sprout = (AttrSpec("#252", "black"), ",*")
sprout2 = (AttrSpec("#474", "black"), "**")
bloom = (AttrSpec("#fff", "black"), "**")
sickBloom = (AttrSpec("#ff2", "black"), "**")
poisonBloom = (AttrSpec("#3f3", "black"), "**")
commandBloom = (AttrSpec("#006", "black"), "**")
poisonBush = (AttrSpec("#3f3", "black"), "#%")
bush = (AttrSpec("#484", "black"), "#%")
encrustedBush = (AttrSpec("#484", "black"), "##")
encrustedPoisonBush = (AttrSpec("#3f3", "black"), "##")
monster = (AttrSpec("#33f", "#007"), "MM")
explosion = (AttrSpec("#fa0", "#f00"), "##")
reactionChamber = (AttrSpec("#aaa", "black"), "[}")
explosive = (AttrSpec("#a55", "black"), "be")
fireCrystals = (AttrSpec("#3f3", "black"), "bc")
bomb = (AttrSpec("#a88", "black"), "bb")
mortar = (AttrSpec("#aaa", "black"), "Bm")
pocketFrame = (AttrSpec("#aaa", "black"), "*h")
case = (AttrSpec("#aaa", "black"), "*H")
memoryCell = (AttrSpec("#33f", "black"), "*m")
frame = (AttrSpec("#aaa", "black"), "#O")
watch = (AttrSpec("#aaa", "black"), "ow")
backTracker = (AttrSpec("#aaa", "black"), "ob")
tumbler = (AttrSpec("#aaa", "black"), "ot")
positioningDevice = (AttrSpec("#aaa", "black"), "op")
stasisTank = (AttrSpec("#aaa", "black"), "$c")
engraver = (AttrSpec("#aaa", "black"), "eE")
gameTestingProducer = (AttrSpec("#aaa", "black"), "/\\")
token = (AttrSpec("#aaa", "black"), ". ")
macroRunner = (AttrSpec("#33f", "black"), "Rm")
objectDispenser = (AttrSpec("#aaa", "black"), "U\\")
markerBean_active = (AttrSpec("#aaa", "black"), " -")
markerBean_inactive = (AttrSpec("#aaa", "black"), "x-")
sorter = (AttrSpec("#aaa", "black"), "U\\")
scraper = (AttrSpec("#aaa", "black"), "RS")
simpleRunner = (AttrSpec("#aaa", "black"), "Rs")
roomBuilder = (AttrSpec("#aaa", "black"), "RB")
globalMacroStorage = (AttrSpec("#ff2", "black"), "mG")
memoryDump = (AttrSpec("#33f", "black"), "mD")
memoryBank = (AttrSpec("#33f", "black"), "mM")
memoryStack = (AttrSpec("#33f", "black"), "mS")
memoryReset = (AttrSpec("#33f", "black"), "mR")
tank = (AttrSpec("#aaa", "black"), "#o")
heater = (AttrSpec("#aaa", "black"), "#%")
connector = (AttrSpec("#aaa", "black"), "#H")
pusher = (AttrSpec("#aaa", "black"), "#>")
puller = (AttrSpec("#aaa", "black"), "#<")
coil = (AttrSpec("#aaa", "black"), "+g")
nook = (AttrSpec("#aaa", "black"), "+L")
stripe = (AttrSpec("#aaa", "black"), "+-")
bolt = (AttrSpec("#aaa", "black"), "+i")
rod = (AttrSpec("#aaa", "black"), "+|")
forceField = (AttrSpec("#99a", "black"), "~~")
drill = (AttrSpec("#aaa", "black"), "&|")
vatMaggot = (AttrSpec("#3f3", "black"), "~-")
bioMass = (AttrSpec("#3f3", "black"), "~=")
pressCake = (AttrSpec("#3f3", "black"), "~#")
maggotFermenter = (AttrSpec("#3f3", "black"), "%0")
bioPress = (AttrSpec("#3f3", "black"), "%H")
gooProducer = (AttrSpec("#3f3", "black"), "%T")
gooDispenser = (AttrSpec("#3f3", "black"), "%=")
coalMine = (AttrSpec("#334", "black"), "&c")
tree = (AttrSpec("#383", "black"), "&/")
infoscreen = (AttrSpec("#aaa", "black"), "iD")
blueprinter = (AttrSpec("#aaa", "black"), "SX")
productionArtwork = (AttrSpec("#ff2", "black"), "QQ")
gooflask_empty = (AttrSpec("#3f3", "black"), "ò ")
gooflask_part1 = (AttrSpec("#3f3", "black"), "ò.")
gooflask_part2 = (AttrSpec("#3f3", "black"), "ò,")
gooflask_part3 = (AttrSpec("#3f3", "black"), "ò-")
gooflask_part4 = (AttrSpec("#3f3", "black"), "ò~")
gooflask_full = (AttrSpec("#3f3", "black"), "ò=")
vial_empty = (AttrSpec("#f33", "black"), "ò ")
vial_part1 = (AttrSpec("#f33", "black"), "ò.")
vial_part2 = (AttrSpec("#f33", "black"), "ò,")
vial_part3 = (AttrSpec("#f33", "black"), "ò-")
vial_part4 = (AttrSpec("#f33", "black"), "ò~")
vial_full = (AttrSpec("#f33", "black"), "ò=")
machineMachine = (AttrSpec("#aaa", "black"), "M\\")
machine = (AttrSpec("#aaa", "black"), "X\\")
scrapCompactor = (AttrSpec("#aaa", "black"), "RC")
sheet = (AttrSpec("#aaa", "black"), "+#")
metalBars = (AttrSpec("#aaa", "black"), "==")
wall = (AttrSpec("#334", "black"), "XX")
dirt = (AttrSpec("#330", "black"), ".´")
grass = (AttrSpec("#030", "black"), ",`")
pipe = (AttrSpec("#337", "black"), "**")
corpse = (AttrSpec("#f00", "black"), "@ ")
unconciousBody = (AttrSpec("#f22", "black"), "@ ")
growthTank_filled = (AttrSpec("#3b3", "black"), "OO")
growthTank_unfilled = (AttrSpec("#3b3", "black"), "00")
corpseAnimator_filled = (AttrSpec("#f33", "black"), "OO")
corpseAnimator_unfilled = (AttrSpec("#f33", "black"), "00")
hutch_free = (AttrSpec("#3b3", "black"), "==")
hutch_occupied = (AttrSpec("#3f3", "black"), "=}")
lever_notPulled = (AttrSpec("#bb3", "black"), "||")
lever_pulled = (AttrSpec("#ff3", "black"), "//")
furnace_inactive = (AttrSpec("#b33", "black"), "oo")
furnace_active = (AttrSpec("#f73,bold", "black"), "öö")
display = (AttrSpec("#a63", "black"), "DD")
coal = "sc"
door_closed = (AttrSpec("#bb3", "black"), "[]")
door_opened = (AttrSpec("#ff3", "black"), "[]")
bioDoor_closed = (AttrSpec("#030", "black"), "[]")
bioDoor_opened = (AttrSpec("#070", "black"), "[]")
pile = "UU"
acid = "~~"
notImplentedYet = "??"
floor = (AttrSpec("#336", "black"), "::")
floor_path = (AttrSpec("#888", "black"), "::")
floor_nodepath = (AttrSpec("#ccc", "black"), "::")
floor_superpath = (AttrSpec("#fff", "black"), "::")
floor_node = (AttrSpec("#ff5", "black"), "::")
floor_superNode = (AttrSpec("#ff5", "black"), "::")
binStorage = "VV"
chains = "88"
commLink = (AttrSpec("#aaa", "black"), "DC")
grid = "##"
acids = [
    (AttrSpec("#182", "black"), "~="),
    (AttrSpec("#095", "black"), "=~"),
    (AttrSpec("#282", "black"), "=~"),
    (AttrSpec("#195", "black"), "~="),
    (AttrSpec("#173", "black"), "~~"),
]
foodStuffs = [
    (AttrSpec("#842", "black"), "*-"),
    (AttrSpec("#841", "black"), ".*"),
    (AttrSpec("#742", "black"), "-."),
    (AttrSpec("#832", "black"), ".-"),
    (AttrSpec("#843", "black"), "-+"),
    (AttrSpec("#743", "black"), "+."),
]
machineries = [
    (AttrSpec("#334", "black"), "Mm"),
    (AttrSpec("#336", "black"), "Mm"),
    (AttrSpec("#347", "black"), "Mm"),
    (AttrSpec("#335", "black"), "Mm"),
    (AttrSpec("#335", "black"), "Mm"),
]
hub = (AttrSpec("#337", "black"), "++")
ramp = "fr"
noClue = (AttrSpec("#337", "black"), "*━")
vatSnake = (AttrSpec("#194", "black"), "<=")
pipe_lr = (AttrSpec("#337", "black"), "━━")
pipe_lrd = (AttrSpec("#337", "black"), "┳━")
pipe_ld = (AttrSpec("#337", "black"), "┓ ")
pipe_lu = (AttrSpec("#337", "black"), "┛ ")
pipe_ru = (AttrSpec("#337", "black"), "┗━")
pipe_ud = (AttrSpec("#337", "black"), "┃ ")
spray_right_stage1 = "-."
spray_left_stage1 = ".-"
spray_right_stage2 = "--"
spray_left_stage2 = "--"
spray_right_stage3 = "-="
spray_left_stage3 = "=-"
spray_right_inactive = "- "
spray_left_inactive = " -"
outlet = (AttrSpec("#337", "black"), "o>")
barricade = "Xx"
randomStuff1 = [
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
]
randomStuff2 = [
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
    (AttrSpec("#334", "black"), "GP"),
]
nonWalkableUnkown = "::"
questTargetMarker = (AttrSpec("white", "black"), "xX")
pathMarker = (AttrSpec("white", "black"), "xx")
questPathMarker = pathMarker
invisibleRoom = ".."
boiler_inactive = (AttrSpec("#33b", "black"), "OO")
boiler_active = (AttrSpec("#77f", "black"), "00")
clamp_active = (AttrSpec("#338", "black"), "<>")
clamp_inactive = (AttrSpec("#338", "black"), "{}")
void = "  "
main_char = "＠"
staffCharacters = [
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    (AttrSpec("#33f", "black"), "@ "),
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    (AttrSpec("#133", "black"), "@ "),
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
    "@ ",
]
staffCharactersByLetter = {
    "a": "@ ",
    "b": "@ ",
    "c": "@ ",
    "d": "@ ",
    "e": (AttrSpec("#33f", "black"), "@ "),
    "f": "@ ",
    "g": "@ ",
    "h": "@ ",
    "i": "@ ",
    "j": "@ ",
    "k": "@ ",
    "l": (AttrSpec("#193", "black"), "@ "),
    "m": "@ ",
    "n": "@ ",
    "o": "@ ",
    "p": "@ ",
    "q": "@ ",
    "r": "@ ",
    "s": "@ ",
    "t": "@ ",
    "u": "@ ",
    "v": "@ ",
    "w": "@ ",
    "x": "@ ",
    "y": "@ ",
    "z": "@ ",
}
winch = "8O"
winch_inactive = "80"
winch_active = "iW"
scrap_light = (AttrSpec("#830", "black"), ".;")
scrap_medium = (AttrSpec("#740", "black"), "*,")
scrap_heavy = (AttrSpec("#a50", "black"), "%#")
