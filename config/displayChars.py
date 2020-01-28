import urwid


drill = (urwid.AttrSpec("#334","black"),"&|")
vatMaggot = (urwid.AttrSpec("#3f3","black"),"~-")
bioMass = (urwid.AttrSpec("#3f3","black"),"~=")
pressCake = (urwid.AttrSpec("#3f3","black"),"~#")
maggotFermenter = (urwid.AttrSpec("#3f3","black"),"%0")
bioPress = (urwid.AttrSpec("#3f3","black"),"%=")
gooProducer = (urwid.AttrSpec("#3f3","black"),"%=")
gooDispenser = (urwid.AttrSpec("#3f3","black"),"%=")
coalMine = (urwid.AttrSpec("#334","black"),"&c")
tree = (urwid.AttrSpec("#334","black"),"&/")
infoscreen = (urwid.AttrSpec("#334","black"),"iD")
blueprinter = (urwid.AttrSpec("#334","black"),"sX")
productionArtwork = (urwid.AttrSpec("#ff2","black"),"ßß")
gooflask_empty = (urwid.AttrSpec("#3f3","black"),"ò ")
gooflask_part1 = (urwid.AttrSpec("#3f3","black"),"ò.")
gooflask_part2 = (urwid.AttrSpec("#3f3","black"),"ò,")
gooflask_part3 = (urwid.AttrSpec("#3f3","black"),"ò-")
gooflask_part4 = (urwid.AttrSpec("#3f3","black"),"ò~")
gooflask_full = (urwid.AttrSpec("#3f3","black"),"ò=")
machineMachine = (urwid.AttrSpec("#334",'black'),"M\\")
machine = (urwid.AttrSpec("#334",'black'),"X\\")
scrapCompactor = (urwid.AttrSpec("#334",'black'),"RC")
blueprint = (urwid.AttrSpec("#334",'black'),"bb")
sheet = (urwid.AttrSpec("#334",'black'),"+#")
metalBars = (urwid.AttrSpec("#334",'black'),"==")
wall = (urwid.AttrSpec("#334",'black'),"⛝ ")
dirt = (urwid.AttrSpec("#330",'black'),".´")
grass = (urwid.AttrSpec("#030",'black'),",`")
pipe = (urwid.AttrSpec("#337","black"),"✠✠")
corpse = "࿊ "
unconciousBody = "࿌ "
growthTank_filled= (urwid.AttrSpec("#3b3","black"),"⏣ ")
growthTank_unfilled = (urwid.AttrSpec("#3f3","black"),"⌬ ")
hutch_free = (urwid.AttrSpec("#3b3","black"),"Ѻ ")
hutch_occupied = (urwid.AttrSpec("#3f3","black"),"ꙭ ")
lever_notPulled = (urwid.AttrSpec("#bb3","black"),"||")
lever_pulled = (urwid.AttrSpec("#ff3","black"),"//")
furnace_inactive = (urwid.AttrSpec("#b33","black"),"ΩΩ")
furnace_active = (urwid.AttrSpec("#f73","black"),"ϴϴ")
display = "۞ "
coal = " *"
door_closed = (urwid.AttrSpec("#bb3","black"),"⛒ ")
door_opened = (urwid.AttrSpec("#ff3","black"),'⭘ ')
pile = (urwid.AttrSpec("#888","black"),"ӫӫ")
acid = "♒♒"
notImplentedYet = "??"
floor = (urwid.AttrSpec("#336",'black'),"::")
floor_path = (urwid.AttrSpec("#888","black"),"::")
floor_nodepath = (urwid.AttrSpec("#ccc","black"),"::")
floor_superpath = (urwid.AttrSpec("#fff","black"),"::")
floor_node = (urwid.AttrSpec("#ff5","black"),"::")
floor_superNode = (urwid.AttrSpec("#ff5","black"),"::")
binStorage = "⛛ "
chains = "⛓ "
commLink = "ߐߐ"
grid = "░░"
acids = [(urwid.AttrSpec("#182","black"),"=="),(urwid.AttrSpec("#095","black"),"≈≈"),(urwid.AttrSpec("#282","black"),"≈="),(urwid.AttrSpec("#195","black"),"=≈"),(urwid.AttrSpec("#173","black"),"≈≈")]
foodStuffs = ["՞՞","🍖","☠ ","💀","👂","✋"]
machineries = ["⌺ ","⚙ ","⌼ ","⍯ ","⌸ "]
hub = "🜹 "
ramp = "⍌ "
noClue = "┅┅"
vatSnake = (urwid.AttrSpec("#194","black"),"🝇 ")
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
randomStuff1 = [(urwid.AttrSpec("#766","black"),"🜆 "),(urwid.AttrSpec("#676","black"),"🜾 "),(urwid.AttrSpec("#667","black"),"ꘒ "),(urwid.AttrSpec("#776","black"),"ꖻ "),(urwid.AttrSpec("#677","black"),"ᵺ ")]
randomStuff2 = [(urwid.AttrSpec("#767","black"),"🝍🝍"),(urwid.AttrSpec("#777","black"),"🝍🝍"),(urwid.AttrSpec("#566","black"),"🝍🝍"),(urwid.AttrSpec("#656","black"),"🖵 "),(urwid.AttrSpec("#665","black"),"⚲ "),(urwid.AttrSpec("#556","black"),"🖵 "),(urwid.AttrSpec("#655","black"),"⿴"),(urwid.AttrSpec("#565","black"),"⿴"),(urwid.AttrSpec("#555","black"),"⚲ "),(urwid.AttrSpec("#765","black"),"🜕 ")]
nonWalkableUnkown = "--"
questTargetMarker = (urwid.AttrSpec("white","black"),"xX")
pathMarker = (urwid.AttrSpec("white","black"),"xx")
questPathMarker = pathMarker
invisibleRoom = "⼞"
boiler_inactive = (urwid.AttrSpec("#33b","black"),"伫")
boiler_active = (urwid.AttrSpec("#77f","black"),"伾")
clamp_active = "⮹ "
clamp_inactive = "⮽ "
void = "  "
main_char = (urwid.AttrSpec("white",'black'),"＠")
staffCharacters = ["Ⓐ ","Ⓑ ","Ⓒ ","Ⓓ ",(urwid.AttrSpec("#33f","black"),"Ⓔ "),"Ⓕ ","Ⓖ ","Ⓗ ","Ⓘ ","Ⓙ ","Ⓚ ",(urwid.AttrSpec("#133","black"),"Ⓛ "),"Ⓜ ","Ⓝ ","Ⓞ ","Ⓟ ","Ⓠ ","Ⓡ ","Ⓢ ","Ⓣ ","Ⓤ ","Ⓥ ","Ⓦ ","Ⓧ ","Ⓨ ","Ⓩ "]
staffCharactersByLetter = {"a":"Ⓐ ","b":"Ⓑ ","c":"Ⓒ ","d":"Ⓓ ","e":(urwid.AttrSpec("#33f","black"),"Ⓔ "),"f":"Ⓕ ","g":"Ⓖ ","h":"Ⓗ ","i":"Ⓘ ","j":"Ⓙ ","k":"Ⓚ ","l":(urwid.AttrSpec("#193","black"),"Ⓛ "),"m":"Ⓜ ","n":"Ⓝ ","o":"Ⓞ ","p":"Ⓟ ","q":"Ⓠ ","r":"Ⓡ ","s":"Ⓢ ","t":"Ⓣ ","u":"Ⓤ ","v":"Ⓥ ","w":"Ⓦ ","x":"Ⓧ ","y":"Ⓨ ","z":"Ⓩ "}
winch = "🞇 "
winch_inactive = "🞅 "
winch_active = "🞇 "
scrap_light = "㌱"
scrap_medium = "㌭"
scrap_heavy = "㌕"

