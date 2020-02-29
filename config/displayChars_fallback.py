import urwid

pocketFrame = (urwid.AttrSpec("#aaa","black"),"*h")
case = (urwid.AttrSpec("#aaa","black"),"*H")
memoryCell = (urwid.AttrSpec("#33f","black"),"*m")
frame = (urwid.AttrSpec("#aaa","black"),"#O")
watch = (urwid.AttrSpec("#aaa","black"),"ow")
backTracker = (urwid.AttrSpec("#aaa","black"),"ob")
tumbler = (urwid.AttrSpec("#aaa","black"),"ot")
positioningDevice = (urwid.AttrSpec("#aaa","black"),"op")
stasisTank = (urwid.AttrSpec("#aaa","black"),"$c")
engraver = (urwid.AttrSpec("#aaa","black"),"eE")
gameTestingProducer = (urwid.AttrSpec("#aaa","black"),"/\\")
token = (urwid.AttrSpec("#aaa","black"),". ")
macroRunner = (urwid.AttrSpec("#33f","black"),"Rm")
objectDispenser = (urwid.AttrSpec("#aaa","black"),"U\\")
markerBean_active = (urwid.AttrSpec("#aaa","black")," -")
markerBean_inactive = (urwid.AttrSpec("#aaa","black"),"x-")
sorter = (urwid.AttrSpec("#aaa","black"),"U\\")
scraper = (urwid.AttrSpec("#aaa","black"),"RS")
simpleRunner = (urwid.AttrSpec("#aaa","black"),"Rs")
roomBuilder = (urwid.AttrSpec("#aaa","black"),"RB")
globalMacroStorage = (urwid.AttrSpec("#ff2","black"),"mG")
memoryDump = (urwid.AttrSpec("#33f","black"),"mD")
memoryBank = (urwid.AttrSpec("#33f","black"),"mM")
memoryStack = (urwid.AttrSpec("#33f","black"),"mS")
memoryReset = (urwid.AttrSpec("#33f","black"),"mR")
tank = (urwid.AttrSpec("#aaa","black"),"#o")
heater = (urwid.AttrSpec("#aaa","black"),"#%")
connector = (urwid.AttrSpec("#aaa","black"),"#H")
pusher = (urwid.AttrSpec("#aaa","black"),"#>")
puller = (urwid.AttrSpec("#aaa","black"),"#<")
sheet = (urwid.AttrSpec("#aaa","black"),"+#")
coil = (urwid.AttrSpec("#aaa","black"),"+g")
nook = (urwid.AttrSpec("#aaa","black"),"+L")
stripe = (urwid.AttrSpec("#aaa","black"),"+-")
bolt = (urwid.AttrSpec("#aaa","black"),"+i")
rod = (urwid.AttrSpec("#aaa","black"),"+|")
forceField = (urwid.AttrSpec("#aaf","black"),"##")
drill = (urwid.AttrSpec("#aaa","black"),"&|")
vatMaggot = (urwid.AttrSpec("#3f3","black"),"~-")
bioMass = (urwid.AttrSpec("#3f3","black"),"~=")
pressCake = (urwid.AttrSpec("#3f3","black"),"~#")
maggotFermenter = (urwid.AttrSpec("#3f3","black"),"%0")
bioPress = (urwid.AttrSpec("#3f3","black"),"%=")
gooProducer = (urwid.AttrSpec("#3f3","black"),"%=")
gooDispenser = (urwid.AttrSpec("#3f3","black"),"%=")
coalMine = (urwid.AttrSpec("#334","black"),"&c")
tree = (urwid.AttrSpec("#383","black"),"&/")
infoscreen = (urwid.AttrSpec("#aaa","black"),"iD")
blueprinter = (urwid.AttrSpec("#aaa","black"),"sX")
productionArtwork = (urwid.AttrSpec("#ff2","black"),"ßß")
gooflask_empty = (urwid.AttrSpec("#3f3","black"),"ò ")
gooflask_part1 = (urwid.AttrSpec("#3f3","black"),"ò.")
gooflask_part2 = (urwid.AttrSpec("#3f3","black"),"ò,")
gooflask_part3 = (urwid.AttrSpec("#3f3","black"),"ò-")
gooflask_part4 = (urwid.AttrSpec("#3f3","black"),"ò~")
gooflask_full = (urwid.AttrSpec("#3f3","black"),"ò=")
machineMachine = (urwid.AttrSpec("#aaa",'black'),"M\\")
machine = (urwid.AttrSpec("#aaa",'black'),"X\\")
scrapCompactor = (urwid.AttrSpec("#aaa",'black'),"RC")
blueprint = (urwid.AttrSpec("#aaa",'black'),"bb")
sheet = (urwid.AttrSpec("#aaa",'black'),"+#")
metalBars = (urwid.AttrSpec("#aaa",'black'),"==")
wall = (urwid.AttrSpec("#334",'black'),"XX")
dirt = (urwid.AttrSpec("#330",'black'),".´")
grass = (urwid.AttrSpec("#030",'black'),",`")
pipe = (urwid.AttrSpec("#337","black"),"**")
corpse = (urwid.AttrSpec("#f00",'black'),"@ ")
unconciousBody = (urwid.AttrSpec("#f22",'black'),"@ ")
growthTank_filled = (urwid.AttrSpec("#3b3","black"),"OO")
growthTank_unfilled = (urwid.AttrSpec("#3b3","black"),"00")
hutch_free = (urwid.AttrSpec("#3b3","black"),"==")
hutch_occupied = (urwid.AttrSpec("#3f3","black"),"=}")
lever_notPulled = (urwid.AttrSpec("#bb3","black"),"||")
lever_pulled = (urwid.AttrSpec("#ff3","black"),"//")
furnace_inactive = (urwid.AttrSpec("#b33","black"),"oo")
furnace_active = (urwid.AttrSpec("#f73,bold","black"),"öö")
display = (urwid.AttrSpec("#a63","black"),"DD")
coal = "sc"
door_closed = (urwid.AttrSpec("#bb3","black"),"[]")
door_opened = (urwid.AttrSpec("#ff3","black"),'[]')
pile = "UU"
acid = "~~"
notImplentedYet = "??"
floor = (urwid.AttrSpec("#336",'black'),"::")
floor_path = (urwid.AttrSpec("#888","black"),"::")
floor_nodepath = (urwid.AttrSpec("#ccc","black"),"::")
floor_superpath = (urwid.AttrSpec("#fff","black"),"::")
floor_node = (urwid.AttrSpec("#ff5","black"),"::")
floor_superNode = (urwid.AttrSpec("#ff5","black"),"::")
binStorage = "VV"
chains = "88"
commLink = (urwid.AttrSpec("#aaa","black"),"DC")
grid = "##"
acids = [(urwid.AttrSpec("#182","black"),"~="),(urwid.AttrSpec("#095","black"),"=~"),(urwid.AttrSpec("#282","black"),"=~"),(urwid.AttrSpec("#195","black"),"~="),(urwid.AttrSpec("#173","black"),"~~")]
foodStuffs = [(urwid.AttrSpec("#842","black"),"*-"),(urwid.AttrSpec("#841","black"),".*"),(urwid.AttrSpec("#742","black"),"-."),(urwid.AttrSpec("#832","black"),".-"),(urwid.AttrSpec("#843","black"),"-+"),(urwid.AttrSpec("#743","black"),"+.")]
machineries = [(urwid.AttrSpec("#334","black"),"Mm"),(urwid.AttrSpec("#336","black"),"Mm"),(urwid.AttrSpec("#347","black"),"Mm"),(urwid.AttrSpec("#335","black"),"Mm"),(urwid.AttrSpec("#335","black"),"Mm")]
hub = (urwid.AttrSpec("#337","black"),"++")
ramp = "fr"
noClue = (urwid.AttrSpec("#337","black"),"*━")
vatSnake = (urwid.AttrSpec("#194","black"),"<=")
pipe_lr = (urwid.AttrSpec("#337","black"),"━━")
pipe_lrd = (urwid.AttrSpec("#337","black"),"┳━")
pipe_ld = (urwid.AttrSpec("#337","black"),"┓ ")
pipe_lu = (urwid.AttrSpec("#337","black"),"┛ ")
pipe_ru = (urwid.AttrSpec("#337","black"),"┗━")
pipe_ud = (urwid.AttrSpec("#337","black"),"┃ ")
spray_right_stage1 = "-."
spray_left_stage1 = ".-"
spray_right_stage2 = "--"
spray_left_stage2 = "--"
spray_right_stage3 = "-="
spray_left_stage3 = "=-"
spray_right_inactive = "- "
spray_left_inactive = " -"
outlet = (urwid.AttrSpec("#337","black"),"o>")
barricade = "Xx"
randomStuff1 = [(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP")]
randomStuff2 = [(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP"),(urwid.AttrSpec("#334",'black'),"GP")]
nonWalkableUnkown = "::"
questTargetMarker = (urwid.AttrSpec("white","black"),"xX")
pathMarker = (urwid.AttrSpec("white","black"),"xx")
questPathMarker = pathMarker
invisibleRoom = ".."
boiler_inactive = (urwid.AttrSpec("#33b","black"),"OO")
boiler_active = (urwid.AttrSpec("#77f","black"),"00")
clamp_active = (urwid.AttrSpec("#338",'black'),"<>")
clamp_inactive = (urwid.AttrSpec("#338",'black'),"{}")
void = "  "
main_char = "@ "
staffCharacters = ["@a","@b","@c","@d",(urwid.AttrSpec("#33f","black"),"@e"),"@f","@g","@h","@i","@j","@k",(urwid.AttrSpec("#133","black"),"@l"),"@m","@n","@o","@p","@q","@r","@s","@t","@u","@v","@w","@x","@y","@z"]
staffCharactersByLetter = {"a":"@a","b":"@b","c":"@c","d":"@d","e":(urwid.AttrSpec("#33f","black"),"@e"),"f":"@f","g":"@g","h":"@h","i":"@i","j":"@j","k":"@k","l":(urwid.AttrSpec("#193","black"),"@l"),"m":"@m","n":"@n","o":"@o","p":"@p","q":"@q","r":"@r","s":"@s","t":"@t","u":"@u","v":"@v","w":"@w","x":"@x","y":"@y","z":"@z"}
winch = "8O"
winch_inactive = "80"
winch_active = "iW"
scrap_light = (urwid.AttrSpec("#f50",'black'),".;")
scrap_medium = (urwid.AttrSpec("#a60",'black'),"*,")
scrap_heavy = (urwid.AttrSpec("#860",'black'),"%#")
