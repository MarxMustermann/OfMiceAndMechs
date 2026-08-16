import urwid

landmine = (urwid.AttrSpec("#f00", "black"), "_~")
sunScreen = (urwid.AttrSpec("#420", "black"), "oo")
healingStation = (urwid.AttrSpec("#f00", "black"), "HS")
forceField2 = (urwid.AttrSpec("#373", "black"), "##")
staticCrystal = (urwid.AttrSpec("#aaf", "black"), "/\\")
staticSpark = (urwid.AttrSpec("#aaf", "black"), "*-")
sparkPlug = (urwid.AttrSpec("#aaf", "black"), "O-")
ripInReality = (urwid.AttrSpec("#aaf", "black"), "|#")
productionManager = (urwid.AttrSpec("#aaa", "black"), "PM")
autoFarmer = (urwid.AttrSpec("#446", "#252"), "::")
portableChallenger = (urwid.AttrSpec("#aaa", "black"), "pc")
typedStockpileManager = (urwid.AttrSpec("#aaa", "black"), "ST")
uniformStockpileManager = (urwid.AttrSpec("#aaa", "black"), "SU")
jobOrder = (urwid.AttrSpec("#33f", "black"), "j#")
jobBoard = (urwid.AttrSpec("#33f", "black"), "JB")
itemUpgrader = (urwid.AttrSpec("#aaa", "black"), "iU")
blueprint = (urwid.AttrSpec("#aaa", "black"), "bd")
command = (urwid.AttrSpec("#aaa", "black"), "c#")
map = (urwid.AttrSpec("#aaa", "black"), "m#")
note = (urwid.AttrSpec("#aaa", "black"), "n#")
bloomShredder = (urwid.AttrSpec("#373", "black"), "%>")
corpseShredder = (urwid.AttrSpec("#800", "black"), "%>")
sporeExtractor = (urwid.AttrSpec("#fff", "black"), "%o")
bloomContainer = (urwid.AttrSpec("#fff", "black"), "[H")
container = (urwid.AttrSpec("#446", "black"), "[H")
moldFeed = (urwid.AttrSpec("black", "#600"), "::")
seededMoldFeed = (urwid.AttrSpec("#436", "#600"), ";;")
moss = (urwid.AttrSpec("#030", "black"), ",.")
moldSpore = (urwid.AttrSpec("#436", "black"), ",.")
monster_spore = (urwid.AttrSpec("#030", "black"), "🝆 ")
monster_feeder = (urwid.AttrSpec("#252", "black"), "🝆~")
monster_grazer = (urwid.AttrSpec("#484", "black"), "🝆=")
monster_corpseGrazer = (urwid.AttrSpec("#824", "black"), "🝆-")
monster_hunter = (urwid.AttrSpec("#f48", "black"), "🝆>")
monster_exploder = (urwid.AttrSpec("#3f3", "black"), "🝆%")
sprout = (urwid.AttrSpec("#252", "black"), ",*")
sprout2 = (urwid.AttrSpec("#474", "black"), "**")
bloom = (urwid.AttrSpec("#fff", "black"), "**")
sickBloom = (urwid.AttrSpec("#ff2", "black"), "**")
poisonBloom = (urwid.AttrSpec("#3f3", "black"), "**")
commandBloom = (urwid.AttrSpec("#006", "black"), "**")
poisonBush = (urwid.AttrSpec("#3f3", "black"), "#%")
bush = (urwid.AttrSpec("#484", "black"), "#%")
encrustedBush = (urwid.AttrSpec("#484", "black"), "##")
encrustedPoisonBush = (urwid.AttrSpec("#3f3", "black"), "##")
monster = (urwid.AttrSpec("#33f", "#007"), "MM")
explosion = (urwid.AttrSpec("#fa0", "#f00"), "##")
reactionChamber = (urwid.AttrSpec("#aaa", "black"), "[}")
explosive = (urwid.AttrSpec("#a55", "black"), "be")
fireCrystals = (urwid.AttrSpec("#3f3", "black"), "bc")
bomb = (urwid.AttrSpec("#a88", "black"), "bb")
mortar = (urwid.AttrSpec("#aaa", "black"), "Bm")
pocketFrame = (urwid.AttrSpec("#aaa", "black"), "*h")
case = (urwid.AttrSpec("#aaa", "black"), "*H")
memoryCell = (urwid.AttrSpec("#33f", "black"), "*m")
frame = (urwid.AttrSpec("#aaa", "black"), "#O")
watch = (urwid.AttrSpec("#aaa", "black"), "ow")
backTracker = (urwid.AttrSpec("#aaa", "black"), "ob")
tumbler = (urwid.AttrSpec("#aaa", "black"), "ot")
positioningDevice = (urwid.AttrSpec("#aaa", "black"), "op")
stasisTank = (urwid.AttrSpec("#aaa", "black"), "$c")
engraver = (urwid.AttrSpec("#aaa", "black"), "eE")
gameTestingProducer = (urwid.AttrSpec("#aaa", "black"), "/\\")
token = (urwid.AttrSpec("#aaa", "black"), ". ")
macroRunner = (urwid.AttrSpec("#33f", "black"), "Rm")
objectDispenser = (urwid.AttrSpec("#aaa", "black"), "U\\")
markerBean_active = (urwid.AttrSpec("#aaa", "black"), " -")
markerBean_inactive = (urwid.AttrSpec("#aaa", "black"), "x-")
sorter = (urwid.AttrSpec("#aaa", "black"), "U\\")
scraper = (urwid.AttrSpec("#aaa", "black"), "RS")
simpleRunner = (urwid.AttrSpec("#aaa", "black"), "Rs")
roomBuilder = (urwid.AttrSpec("#aaa", "black"), "RB")
globalMacroStorage = (urwid.AttrSpec("#ff2", "black"), "mG")
memoryDump = (urwid.AttrSpec("#33f", "black"), "mD")
memoryBank = (urwid.AttrSpec("#33f", "black"), "mM")
memoryStack = (urwid.AttrSpec("#33f", "black"), "mS")
memoryReset = (urwid.AttrSpec("#33f", "black"), "mR")
tank = (urwid.AttrSpec("#888", "black"), "#o")
heater = (urwid.AttrSpec("#aaa", "black"), "#%")
connector = (urwid.AttrSpec("#aaa", "black"), "#H")
pusher = (urwid.AttrSpec("#aaa", "black"), "#>")
puller = (urwid.AttrSpec("#aaa", "black"), "#<")
sheet = (urwid.AttrSpec("#aaa", "black"), "+#")
coil = (urwid.AttrSpec("#aaa", "black"), "+g")
nook = (urwid.AttrSpec("#aaa", "black"), "+L")
stripe = (urwid.AttrSpec("#aaa", "black"), "+-")
bolt = (urwid.AttrSpec("#aaa", "black"), "+>")
rod = (urwid.AttrSpec("#aaa", "black"), "+|")
forceField = (urwid.AttrSpec("#aaf", "black"), "~~")
drill = (urwid.AttrSpec("#aaa", "black"), "&|")
vatMaggot = (urwid.AttrSpec("#3f3", "black"), "~-")
bioMass = (urwid.AttrSpec("#3f3", "black"), "~=")
pressCake = (urwid.AttrSpec("#3f3", "black"), "~#")
maggotFermenter = (urwid.AttrSpec("#3f3", "black"), "%0")
bioPress = (urwid.AttrSpec("#3f3", "black"), "%H")
gooProducer = (urwid.AttrSpec("#3f3", "black"), "%T")
gooDispenser = (urwid.AttrSpec("#3f3", "black"), "%=")
coalMine = (urwid.AttrSpec("#334", "black"), "&c")
tree = (urwid.AttrSpec("#383", "black"), "&/")
infoscreen = (urwid.AttrSpec("#aaa", "black"), "iD")
blueprinter = (urwid.AttrSpec("#aaa", "black"), "SX")
productionArtwork = (urwid.AttrSpec("#ff2", "black"), "QQ")
gooflask_empty = (urwid.AttrSpec("#3f3", "black"), "o ")
gooflask_part1 = (urwid.AttrSpec("#3f3", "black"), "o.")
gooflask_part2 = (urwid.AttrSpec("#3f3", "black"), "o,")
gooflask_part3 = (urwid.AttrSpec("#3f3", "black"), "o-")
gooflask_part4 = (urwid.AttrSpec("#3f3", "black"), "o~")
gooflask_full = (urwid.AttrSpec("#3f3", "black"), "o=")
vial_empty = (urwid.AttrSpec("#f33", "black"), "o ")
vial_part1 = (urwid.AttrSpec("#f33", "black"), "o.")
vial_part2 = (urwid.AttrSpec("#f33", "black"), "o,")
vial_part3 = (urwid.AttrSpec("#f33", "black"), "o-")
vial_part4 = (urwid.AttrSpec("#f33", "black"), "o~")
vial_full = (urwid.AttrSpec("#f33", "black"), "o=")
machineMachine = (urwid.AttrSpec("#aaa", "black"), "M\\")
machine = (urwid.AttrSpec("#aaa", "black"), "X\\")
scrapCompactor = (urwid.AttrSpec("#aaa", "black"), "RC")
metalBars = (urwid.AttrSpec("#aaa", "black"), "==")
wall = (urwid.AttrSpec("#334", "black"), "⛝ ")
dirt = (urwid.AttrSpec("#330", "black"), ".'")
grass = (urwid.AttrSpec("#030", "black"), ",`")
pipe = (urwid.AttrSpec("#337", "black"), "✠✠")
corpse = "࿊ "
unconciousBody = "࿌ "
growthTank_filled = (urwid.AttrSpec("#3b3", "black"), "⏣ ")
growthTank_unfilled = (urwid.AttrSpec("#3f3", "black"), "⌬ ")
corpseAnimator_filled = (urwid.AttrSpec("#f33", "black"), "⏣ ")
corpseAnimator_unfilled = (urwid.AttrSpec("#f33", "black"), "⌬ ")
hutch_free = (urwid.AttrSpec("#3b3", "black"), "Ѻ ")
hutch_occupied = (urwid.AttrSpec("#3f3", "black"), "ꙭ ")
lever_notPulled = (urwid.AttrSpec("#bb3", "black"), "||")
lever_pulled = (urwid.AttrSpec("#ff3", "black"), "//")
furnace_inactive = (urwid.AttrSpec("#b33", "black"), "ΩΩ")
furnace_active = (urwid.AttrSpec("#f73", "black"), "ϴϴ")
display = "۞ "
coal = " *"
door_closed = (urwid.AttrSpec("#bb3", "black"), "⛒ ")
door_opened = (urwid.AttrSpec("#660", "black"), "⭘ ")
bioDoor_closed = (urwid.AttrSpec("#030", "black"), "⛒ ")
bioDoor_opened = (urwid.AttrSpec("#070", "black"), "⭘ ")
pile = (urwid.AttrSpec("#888", "black"), "ӫӫ")
acid = "♒♒"
notImplentedYet = "??"
floor = (urwid.AttrSpec("#336", "black"), "::")
floor_path = (urwid.AttrSpec("#888", "black"), "::")
floor_nodepath = (urwid.AttrSpec("#ccc", "black"), "::")
floor_superpath = (urwid.AttrSpec("#fff", "black"), "::")
floor_node = (urwid.AttrSpec("#ff5", "black"), "::")
floor_superNode = (urwid.AttrSpec("#ff5", "black"), "::")
binStorage = "⛛ "
chains = "⛓ "
commLink = "ߐߐ"
grid = "░░"
acids = [
    (urwid.AttrSpec("#182", "black"), "=="),
    (urwid.AttrSpec("#095", "black"), "≈≈"),
    (urwid.AttrSpec("#282", "black"), "≈="),
    (urwid.AttrSpec("#195", "black"), "=≈"),
    (urwid.AttrSpec("#173", "black"), "≈≈"),
]
foodStuffs = ["՞՞", "🍖", "☠ ", "💀", "👂", "✋"]
machineries = ["⌺ ", "⚙ ", "⌼ ", "⍯ ", "⌸ "]
hub = "🜹 "
ramp = "⍌ "
noClue = "┅┅"
vatSnake = (urwid.AttrSpec("#194", "black"), "🝇 ")
pipe_lr = "━━"
pipe_lrd = "┳━"
pipe_ld = "┓ "
pipe_lu = "┛ "
pipe_ru = "┗━"
pipe_ud = "┃ "
spray_right_stage1 = "- "
spray_right_stage2 = "= "
spray_right_stage3 = "⚟ "
spray_left_stage1 = " -"
spray_left_stage2 = " ="
spray_left_stage3 = "⚞ "
spray_right_inactive = ": "
spray_left_inactive = " :"
outlet = "◎ "
barricade = "❖❖"
randomStuff1 = [
    (urwid.AttrSpec("#766", "black"), "🜆 "),
    (urwid.AttrSpec("#676", "black"), "🜾 "),
    (urwid.AttrSpec("#667", "black"), "ꘒ "),
    (urwid.AttrSpec("#776", "black"), "ꖻ "),
    (urwid.AttrSpec("#677", "black"), "ᵺ "),
]
randomStuff2 = [
    (urwid.AttrSpec("#767", "black"), "🝍🝍"),
    (urwid.AttrSpec("#777", "black"), "🝍🝍"),
    (urwid.AttrSpec("#566", "black"), "🝍🝍"),
    (urwid.AttrSpec("#656", "black"), "🖵 "),
    (urwid.AttrSpec("#665", "black"), "⚲ "),
    (urwid.AttrSpec("#556", "black"), "🖵 "),
    (urwid.AttrSpec("#655", "black"), "⿴"),
    (urwid.AttrSpec("#565", "black"), "⿴"),
    (urwid.AttrSpec("#555", "black"), "⚲ "),
    (urwid.AttrSpec("#765", "black"), "🜕 "),
]
nonWalkableUnkown = "--"
questTargetMarker = (urwid.AttrSpec("white", "black"), "xX")
pathMarker = (urwid.AttrSpec("white", "black"), "xx")
questPathMarker = pathMarker
invisibleRoom = "⼞"
boiler_inactive = (urwid.AttrSpec("#33b", "black"), "伫")
boiler_active = (urwid.AttrSpec("#77f", "black"), "伾")
clamp_active = "⮹ "
clamp_inactive = "⮽ "
void = "  "
main_char = (urwid.AttrSpec("white", "black"), "＠")
staffCharacters = [
    "Ⓐ ",
    "Ⓑ ",
    "Ⓒ ",
    "Ⓓ ",
    (urwid.AttrSpec("#33f", "black"), "Ⓔ "),
    "Ⓕ ",
    "Ⓖ ",
    "Ⓗ ",
    "Ⓘ ",
    "Ⓙ ",
    "Ⓚ ",
    (urwid.AttrSpec("#133", "black"), "Ⓛ "),
    "Ⓜ ",
    "Ⓝ ",
    "Ⓞ ",
    "Ⓟ ",
    "Ⓠ ",
    "Ⓡ ",
    "Ⓢ ",
    "Ⓣ ",
    "Ⓤ ",
    "Ⓥ ",
    "Ⓦ ",
    "Ⓧ ",
    "Ⓨ ",
    "Ⓩ ",
]
staffCharactersByLetter = {
    "a": "Ⓐ ",
    "b": "Ⓑ ",
    "c": "Ⓒ ",
    "d": "Ⓓ ",
    "e": (urwid.AttrSpec("#33f", "black"), "Ⓔ "),
    "f": "Ⓕ ",
    "g": "Ⓖ ",
    "h": "Ⓗ ",
    "i": "Ⓘ ",
    "j": "Ⓙ ",
    "k": "Ⓚ ",
    "l": (urwid.AttrSpec("#193", "black"), "Ⓛ "),
    "m": "Ⓜ ",
    "n": "Ⓝ ",
    "o": "Ⓞ ",
    "p": "Ⓟ ",
    "q": "Ⓠ ",
    "r": "Ⓡ ",
    "s": "Ⓢ ",
    "t": "Ⓣ ",
    "u": "Ⓤ ",
    "v": "Ⓥ ",
    "w": "Ⓦ ",
    "x": "Ⓧ ",
    "y": "Ⓨ ",
    "z": "Ⓩ ",
}
winch = "🞇 "
winch_inactive = "🞅 "
winch_active = "🞇 "
scrap_light = (urwid.AttrSpec("#830", "black"), "㌱")
scrap_medium = (urwid.AttrSpec("#740", "black"), "㌭")
scrap_heavy = (urwid.AttrSpec("#a50", "black"), "㌕")
