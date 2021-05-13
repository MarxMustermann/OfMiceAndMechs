import src

'''
'''
class Case(src.items.Item):
    type = "Case"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__()
        self.display = src.canvas.displayChars.case
        self.name = "case"

    def getLongInfo(self):
        text = """

A case. Is complex building item. It is used to build bigger things.

"""
        return text

src.items.addType(Case)

