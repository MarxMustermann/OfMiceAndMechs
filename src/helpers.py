import tcod

import src


def clamp(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n


def draw_frame_text(con, width, height, t, x, y):
    for cx in range(x - 2, x + width+1):
        for cy in range(y - 2, y + height+1):
            con.rgb[cx, cy] = ord(" "), (0, 0, 0), (0, 0, 0)
    for cx in range(x - 2, x + width+1):
        con.rgb[cx, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)
        con.rgb[cx, y + height+1] = ord("-"), (255, 255, 255), (0, 0, 0)
    for cy in range(y - 2, y + height+1):
        con.rgb[x - 2, cy] = ord("|"), (255, 255, 255), (0, 0, 0)
        con.rgb[x + width+1, cy] = ord("|"), (255, 255, 255), (0, 0, 0)

    con.rgb[x - 2, y - 2] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 2, y - 3] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 3, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x + width+1, y - 2] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width+1, y - 3] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width + 1, y - 2] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x - 2, y + height + 1] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 2, y + height + 1] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x - 3, y + height + 1] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.rgb[x + width + 1, y + height + 1] = ord("+"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width + 1, y + height + 2] = ord("|"), (255, 255, 255), (0, 0, 0)
    con.rgb[x + width + 2, y + height+1] = ord("-"), (255, 255, 255), (0, 0, 0)

    con.print_box(x, y, width, height, t, (255, 255, 255), (0, 0, 0), tcod.constants.BKGND_SET, tcod.constants.CENTER)


def fade_between_consoles_rgb(current, target, t):
    transition_array = ["?", "/", "."]
    for width in range(current.shape[0]):
        for height in range(current.shape[1]):
            transition_state = int(t * 4)
            match transition_state:
                case 0:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = current[width, height]["ch"]
                case 4:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = target[width, height]["ch"]
                case _:
                    src.interaction.tcodConsole.rgb[width, height]["ch"] = ord(transition_array[transition_state - 1])
            src.interaction.tcodConsole.rgb[width, height]["fg"] = src.pseudoUrwid.AttrSpec.interpolate(
                current[width, height]["fg"], target[width, height]["fg"], t
            )
            src.interaction.tcodConsole.rgb[width, height]["bg"] = src.pseudoUrwid.AttrSpec.interpolate(
                current[width, height]["bg"], target[width, height]["bg"], t
            )
