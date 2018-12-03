import urwid

"""
split a mix of strings and urwid formating into a list where each element contains exactly
one character and its formating
bad code: this should not be an inline function but accessible as a helper
"""
def flattenToPeseudoString(urwidText):
    # split strings
    if isinstance(urwidText,str):
        return list(urwidText)

    # recursively handle list items
    elif isinstance(urwidText,list):
        result = []
        for item in urwidText:
            result.extend(flattenToPeseudoString(item))
        return result

    # resolve references
    elif isinstance(urwidText,int):
        result = flattenToPeseudoString(displayChars.indexedMapping[urwidText][1])
        return result
            
    # handle formatters
    else:
        result = []
        for item in flattenToPeseudoString(urwidText[1]):
            #result.append((urwidText[0],item)) # bad code: commented out code
            result.append(item) # bad code: nukes all the pretty colors
        return result

'''
add rusty colors to a string
bad code: this should be a generally available function not an inline function
'''
def makeRusty(payload):
    converted = []
    colours = ['#f50',"#a60","#f80","#fa0","#860"]
    counter = 0
    for char in payload:
        counter += 1
        if len(char):
            converted.append((urwid.AttrSpec(colours[counter*7%5],'default'),char))
    return converted
