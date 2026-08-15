import src

import tcod
import math

class NameNumberPairSetter(src.menues.SubMenu):
    '''
    a generic menue to change name/number pairs
    '''
    def __init__(self, character, data_to_change, description=None, title=None, choices=None):
        self.type = "NameNumberPairSetter"
        self.selected_name = None
        self.character = character
        self.data_to_change = data_to_change
        self.description = description
        self.title = title
        self.choices = choices
        self.page_index = 0
        self.page_size = 20
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        '''
        handles a keystroke by a user
        '''

        # exit menu
        if key in ("esc",):
            if self.followUp:
                self.callIndirect(self.followUp)
            self.done = True
            return True

        # get sorted duties
        names = self._get_sorted_names(names_only=True)
        if not self.selected_name or self.selected_name not in names:
            self.selected_name = names[0]

        # handle edge case
        if not names:
            return False

        # handle general keypresses
        if key in ("w","up","W","a"):
            index = names.index(self.selected_name)
            change_amount = 1
            if key == "W":
                change_amount = 10
            if key == "a":
                change_amount = self.page_size
            index -= change_amount
            if index < 0:
                index = len(names)-1
            self.selected_name = names[index]
        if key in ("s","down","S","d"):
            index = names.index(self.selected_name)
            change_amount = 1
            if key == "S":
                change_amount = 10
            if key == "d":
                change_amount = self.page_size
            index += change_amount
            if index >= len(names):
                index = 0
            self.selected_name = names[index]

        # change the values
        if key in ("k","K",):
            value = self.data_to_change.get(self.selected_name,0)
            change_amount = 1
            if key.isupper():
                change_amount = 10
            value -= change_amount
            if value < 1:
                if self.selected_name in self.data_to_change:
                    del self.data_to_change[self.selected_name]
            else:
                self.data_to_change[self.selected_name] = value
        if key in ("j","J",):
            value = self.data_to_change.get(self.selected_name,0)
            change_amount = 1
            if key.isupper():
                change_amount = 10
            value += change_amount
            self.data_to_change[self.selected_name] = value

        # reset the index
        names = self._get_sorted_names(names_only=True)
        if not self.selected_name or self.selected_name not in names:
            self.selected_name = names[0]

        # open correct page
        index = names.index(self.selected_name)
        self.page_index = index//self.page_size

        # signal to keep menu open
        return False

    def getTitle(self):
        '''
        return the menues title
        '''
        return self.title

    def render(self,size=None):
        '''
        returns a text showing the contents of the menu
        '''

        # set up the basi text
        text = []
        
        # add description
        if self.description:
            text.append(self.description)

        # add list of names to show
        names = self._get_sorted_names()
        start_index = self.page_index*self.page_size
        reduced_names = names[start_index:start_index+self.page_size]
        for (entry_name,entry_amount) in reduced_names:
            if entry_name == self.selected_name:
                text.append(f"=> ")
            else:
                text.append(f"*  ")
            spacer = " "*(25-len(entry_name))
            text.append(f"{entry_name}:{spacer} {entry_amount}\n")
        num_pages = int(math.ceil(len(names)/self.page_size))

        # show paging information
        text.append(f"\npage: {self.page_index+1}/{num_pages}\n")

        # add usage instructions
        text.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),["""
press """,src.interaction.ActionMeta(payload="w",content="w"),"/",src.interaction.ActionMeta(payload="s",content="s"),""" to move cursor
""",src.interaction.ActionMeta(payload="a",content="press a to decrease value"),"""
""",src.interaction.ActionMeta(payload="d",content="press d to increase value"),"""
"""]))

        # return the generated text
        return text

    def _get_sorted_names(self,names_only=False):
        '''
        return the sorted list of names 
        '''

        # get names
        names = list(self.data_to_change.items())
        for choice in self.choices:
            if not choice in self.data_to_change:
                names.append((choice,0))

        # sort names
        names.sort(key=lambda entry: entry[0])
        names.sort(key=lambda entry: entry[1],reverse=True)

        # remove value
        if names_only:
            new_name = []
            for name_entry in names:
                new_name.append(name_entry[0])
            names = new_name

        # return result
        return names

# register the menu type
src.menues.add_menu(NameNumberPairSetter)
