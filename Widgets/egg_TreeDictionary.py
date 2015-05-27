# -*- coding: utf-8 -*-
"""
@author: jaxankey
@author: jayich

This object was borrowed from the spinmob project (see https://github.com/Spinmob/spinmob).

I modified it slightly to make it work with this project
"""
import pyqtgraph as _pg
#import spinmob as _spinmob
#_d = _spinmob.data
#import os as _os

class egg_TreeDictionary(_pg.parametertree.ParameterTree):

    def __init__(self, default_save_path="settings.txt", show_header=False):
        """
        Simplified / Modified version of pyqtgraph's ParameterTree() object,
        designed to store databox-ready header information and settings.

        Main changes:
         * simplified methods for setting parameters and getting them.
         * all parameter names must not have self.naughty characters.
         * default_save_path is where the settings will be saved / loaded
           from when calling self.save() and self.load(). The settings
           file is just a databox with no data, and you can use other
           databox files.

        Note: because of some weirdness in how things are defined, I had to
        write a special self.connect_...() functions for the tree

        Note2: For the 'list' type, currently you must specify a list of strings.
        Otherwise there will be confusion upon loading.
        """
        _pg.parametertree.ParameterTree.__init__(self, showHeader=show_header)
        self.naughty            = [' ', '\t', '\n', '\r', ',', ';']
        self.default_save_path  = default_save_path


    def __repr__(self):
        """
        How do display this object.
        """
        s = "\nTreeDictionary() -> "+str(self.default_save_path)+"\n"

        for k in self.get_dictionary()[0]:
            s = s + "  "+k+" = "+repr(self[k])+"\n"

        return s

    def connect_any_signal_changed(self, function):
        """
        Connects the "anything changed" signal for all of the tree to the
        specified function.
        """
        # loop over all top level parameters
        for i in range(self.topLevelItemCount()):

            # make sure there is only one connection!
            self.topLevelItem(i).param.sigTreeStateChanged.connect(function, type=_pg.QtCore.Qt.UniqueConnection)

        return self

    def connect_signal_changed(self, name, function):
        """
        Connects a changed signal from the parameters of the specified name
        to the supplied function.
        """
        x = self._find_parameter(name.split("/"))

        # if it pooped.
        if x==None: return None

        # connect it
        x.sigValueChanged.connect(function)

        return self

    def _find_parameter(self, name_list, create_missing=False, quiet=False):
        """
        Tries to find and return the parameter of the specified name. The name
        should be of the form

        "branch1/branch2/parametername"

        Setting create_missing=True means if it doesn't find a branch it
        will create one.

        Setting quiet=True will suppress error messages (for checking)
        """

        # make a copy so this isn't destructive to the supplied list
        s = list(name_list)

        # if the length is zero, return the root widget
        if len(s)==0: return self

        # the first name must be treated differently because it is
        # the main widget, not a branch
        r = self._clean_up_name(s.pop(0))

        # search for the root name
        result = self.findItems(r, _pg.QtCore.Qt.MatchCaseSensitive | _pg.QtCore.Qt.MatchFixedString)

        # if it pooped and we're not supposed to create it, quit
        if len(result) == 0 and not create_missing:
            if not quiet: print("ERROR: Could not find '"+r+"'")
            return None

        # otherwise use the first value
        elif len(result): x = result[0].param

        # otherwise, if there are more names in the list,
        # create the branch and keep going
        else:
            x = _pg.parametertree.Parameter.create(name=r, type='group', children=[])
            self.addParameters(x)

        # loop over the remaining names, and use a different search method
        for n in s:

            # first clean up
            n = self._clean_up_name(n)

            # only allow the parameter search if x is a branch
            if not x.isType('group'):
                if not quiet: print("ERROR: '"+x.name()+"' is not a branch and can't be searched.")
                return None

            # try to search for the name
            try: x = x.param(n)

            # name doesn't exist
            except:

                # if we're supposed to, create the new branch
                if create_missing: x = x.addChild(_pg.parametertree.Parameter.create(name=n, type='group', children=[]))

                # otherwise poop out
                else:
                    if not quiet: print("ERROR: Could not find '"+n+"' in '"+x.name()+"'")
                    return None

        # return the last one we found / created.
        return x


    def add_button(self, name, **kwargs):
        """
        Adds (and returns) a limited-functionality button of the
        specified location. The clicked signal still lives in
        button.signal_clicked, though.
        """

        # first clean up the name
        name = self._clean_up_name(name)

        # split into (presumably existing) branches and parameter
        s = name.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            print("Error: '"+name+"' already exists.")
            return None

        # get the leaf name off the list.
        p = self._clean_up_name(s.pop(-1))

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None: return None

        # create the leaf object
        button = _pg.parametertree.Parameter.create(name=p, type='action', **kwargs)

        # add it to the tree (different methods for root)
        if b == self: b.addParameters(button)
        else:                 b.addChild(button)

        # modify the existing class to fit our conventions
        button.signal_clicked = button.sigActivated

        return button

    def _clean_up_name(self, name):
        """
        Cleans up the name according to the rules specified in this exact
        function. Uses self.naughty, a list of naughty characters.
        """
        for n in self.naughty: name = name.replace(n, '_')
        return name

    def add_parameter(self, name='test', value='42', **kwargs):
        """
        Adds a parameter "leaf" to the tree.

        The name should be a string of the form

        "branch1/branch2/parametername"

        and will be nested as indicated. The value should match the type
        (the default type is 'str'). More keyword arguments can be used.
        See pyqtgraph ParameterTree for more info.

        Here are the other default kwargs:
            type     = 'str'
            values   = not used  # used for 'list' type
            step     = 1         # step size of incrementing numbers
            limits   = not used  # used to limit numerical values
            default  = not used  # used to set the default numerical value
            siPrefix = False     # used for displaying units on numbers
            suffix   = not used  # used to add units (awesome)

        """

        # update the default kwargs
        other_kwargs = dict(type = 'str')
        other_kwargs.update(kwargs)

        # split into (presumably existing) branches and parameter
        s = name.split('/')

        # make sure it doesn't already exist
        if not self._find_parameter(s, quiet=True) == None:
            print("Error: '"+name+"' already exists.")
            return self

        # get the leaf name off the list.
        p = self._clean_up_name(s.pop(-1))

        # create / get the branch on which to add the leaf
        b = self._find_parameter(s, create_missing=True)

        # quit out if it pooped
        if b == None: return self

        # create the leaf object
        leaf = _pg.parametertree.Parameter.create(name=p, value=value, **other_kwargs)

        # add it to the tree (different methods for root)
        if b == self: b.addParameters(leaf)
        else:                 b.addChild(leaf)

        return self


    def _get_parameter_dictionary(self, base_name, dictionary, sorted_keys, parameter):
        """
        Recursively loops over the parameter's children, adding
        keys (starting with base_name) and values to the supplied dictionary
        (provided they do not have a value of None).
        """

        # assemble the key for this parameter
        k = base_name + "/" + parameter.name()

        # first add this parameter (if it has a value)
        if not parameter.value()==None:
            sorted_keys.append(k[1:])
            dictionary[sorted_keys[-1]] = parameter.value()

        # now loop over the children
        for p in parameter.children():
            self._get_parameter_dictionary(k, dictionary, sorted_keys, p)

    def get_dictionary(self):
        """
        Returns the list of parameters and a dictionary of values
        (good for writing to a databox header!)

        Return format is sorted_keys, dictionary
        """

        # output
        k = list()
        d = dict()

        # loop over the root items
        for i in range(self.topLevelItemCount()):

            # grab the parameter item, and start building the name
            x = self.topLevelItem(i).param

            # now start the recursive loop
            self._get_parameter_dictionary('', d, k, x)

        return k, d

    def get_value(self, name):
        """
        Returns the value of the parameter with the specified name.
        """
        # first clean up the name
        name = self._clean_up_name(name)

        # now get the parameter object
        x = self._find_parameter(name.split('/'))

        # quit if it pooped.
        if x == None: return None

        return x.value()

    __getitem__ = get_value

    def set_value(self, name, value, block_events=False, ignore_error=False):
        """
        Sets the variable of the supplied name to the supplied value.

        Setting block_events=True will temporarily block the widget from
        sending any signals when setting the value.
        """
        if block_events: self.block_events()

        # first clean up the name
        name = self._clean_up_name(name)

        # now get the parameter object
        x = self._find_parameter(name.split('/'), quiet=ignore_error)

        # quit if it pooped.
        if x == None: return None

        # for lists, make sure the value exists!!
        if x.type() in ['list']:
            if value in x.forward.keys(): x.setValue(value)
            else:                         x.setValue(x.forward.keys()[0])

        # otherwise just set the value
        else: x.setValue(value)

        if block_events: self.unblock_events()

        return self

    __setitem__ = set_value

    def _signal_changed_handler(self, *args):
        """
        If we're supposed to autosave when something changes,
        do so.
        """
        print("signal change!")
        #if self.autosave: self.save()
        

#    def save(self, path=None):
#        """
#        Saves all the parameters to a text file using the databox
#        functionality. If path=None, saves to self.default_save_path.
#
#        If the file doesn't exist, it will use hard-coded defaults.
#        """
#        if path==None: path = self.default_save_path
#
#        # make the databox object
#        d = _d.databox()
#
#        # get the keys and dictionary
#        keys, dictionary = self.get_dictionary()
#
#        # loop over the keys and add them to the databox header
#        for k in keys: d.insert_header(k, repr(dictionary[k]))
#
#        # save it
#        d.save_file(path, force_overwrite=True)
#
#    def load(self, path=None):
#        """
#        Loads all the parameters from a databox text file. If path=None,
#        loads from self.default_save_path.
#        """
#        if path==None: path = self.default_save_path
#
#        # make the databox object
#        d = _d.databox()
#
#        # only load if it exists
#        if _os.path.exists(path): d.load_file(path, header_only=True)
#        else:                     return None
#
#        # update the settings
#        self.update(d)
#        return self

    def update(self, d, ignore_errors=False):
        """
        Supply a dictionary or databox with a header of the same format
        and see what happens! (Hint: it updates the existing values.)
        """
        if not type(d) == dict: d = d.headers

        # loop over the dictionary and update
        for k in d.keys():

            # for safety: by default assume it's a repr() with python code
            try:    self.set_value(k, eval(str(d[k])), ignore_error=ignore_errors)

            # if that fails try setting the value directly
            except: self.set_value(k, d[k], ignore_error=ignore_errors)

        return self