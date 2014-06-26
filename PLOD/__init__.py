# PLOD\__init__.py
#
# Pythonic List of Dictionary module/class (PLOD)
#
# Version 0.0.4working

# TODO: procedures: replace, update
# TODO: add_column

# speculative TODO:
#   add support for JOINS and their variants
#   support for lists-treated-as-dictionaries in where key=index.

# TODO: _modify_member only tested on Mongo db

# TODO: support for 'code correct' returnString()
    
import internal
import types as typemod
try:
    import bson
    bson_available = True
except ImportError:
    bson_available = False

class PLOD(object):
    '''
    PLOD: Pythonic List of Dictionaries Handler

    This is a class that allows you to manipulate lists of dictionaries in a
    clear and easy-to-interpret manner.

    HOW TO USE

    To use, create an instance of the PLOD class with the list of dictinoaries as
    it's parameter. For example, given the following list:

    >>> test = [
    ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
    ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
    ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
    ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
    ...    {"name": "Bill",  "age": 19, "income": 29000                   },
    ... ]

    You can 'load' PLOD with:

    >>> my_list = PLOD(test)

    Then, one can 'stack' various methods together to manipulate that list of
    dictinoaries and return a result. For example:

    >>> print PLOD(test).gt("age", 18).sort("income").returnString()
    [
        {age: 29, income: None , name: 'Jim' , wigs: None     , zim: {'zam': '99'}},
        {age: 20, income: 15000, name: 'Joe' , wigs: [1, 2, 3], zim: None         },
        {age: 19, income: 29000, name: 'Bill', wigs: None     , zim: None         }
    ]

    PLOD is designed to be very forgiving and, as much as possible, very flexible.
    '''

    NOOP = -1  # 'NOOP' aka 'no operation' essentially means "always true"
    LESS = 0
    LESSorEQUAL = 1
    EQUALorLESS = 1
    EQUAL = 2
    GREATERorEQUAL = 3
    EQUALorGREATER = 3
    GREATER = 4
    NOT_EQUAL = 5
    NOTEQUAL = 5

    def __init__(self, table):
        '''Initialize PLOD with the list of dictionaries (table).

        While the 'table' must be a list, the entries in the table
        need not be dictionary in the strictest sense. It merely
        needs to be of a type that dictionary-like lookups may be done.

        In addition to pure dictionaries, this routine also inpreprets:
        * classes with a .__dict__ attribute
        * mongoEngine documents (a class for MongoDb handling)
        * other lists (index positions used as keys)

        Example of use:

        >>> class MyClass(object):
        ...     def __init__(self, name):
        ...         self.name = name
        >>> test = [
        ...    {"name": "Jim", "age": 29},
        ...    ["aye", "zip"],
        ...    MyClass("Smith")
        ... ]        
        >>> print PLOD(test).returnString()
        [
            {0: None , 1: None , age:   29, name: 'Jim'  },
            {0: 'aye', 1: 'zip', age: None, name: None   },
            {0: None , 1: None , age: None, name: 'Smith'}
        ]

        :param table:
           The list of dictionaries to work on.
            
        :returns:
            class
        '''
        self.table = table
        self.index_track = []
        for i in range(len(self.table)):
            self.index_track.append(i)
        return None

    ############################
    # Attribute Modifications
    ############################

    def dropKey(self, key):
        '''Drop an attribute/element/key-value pair from all the dictionaries.

        If the dictionary key does not exist in a particular dictionary, then
        that dictionary is left unchanged.

        Side effect: if the key is a number and it matches a list (interpreted
        as a dictionary), it will cause the "keys" to shift just as a list
        would be expected to.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).dropKey("income").returnString()
        [
            {age:  3, name: 'Jim'  , wigs:        68, zim: None         },
            {age:  3, name: 'Larry', wigs: [3, 2, 9], zim: None         },
            {age: 20, name: 'Joe'  , wigs: [1, 2, 3], zim: None         },
            {age: 29, name: 'Jim'  , wigs: None     , zim: {'zam': '99'}},
            {age: 19, name: 'Bill' , wigs: None     , zim: None         }
        ]
        
        .. versionadded:: 0.0.2
        
        :param key:
            The dictionary key that should be removed.
        :returns: self

        '''
        result = []
        for row in self.table:
            result.append(internal.remove_member(row, key))
        self.table = result
        return self

    ############################
    # List Modifications
    ############################

    def upsert(self, key, value, entry):
        '''Update or Insert an entry into the list of dictionaries.

        If a dictionary in the list is found where key matches the value, then
           the FIRST matching list entry is replaced with entry
        else
           the entry is appended to the end of the list.

        The new entry is not examined in any way. It is, in fact, possible
        to upsert an entry that does not match the supplied key/value.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> entryA = {"name": "Willie", "age": 77}
        >>> myPLOD = PLOD(test)
        >>> print myPLOD.upsert("name", "Willie", entryA).returnString()
        [
            {age:  3, income: 93000, name: 'Jim'   , wigs:        68},
            {age:  3, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'   , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]
        >>> entryB = {"name": "Joe", "age": 20, "income": 30, "wigs": [3, 2, 9]}
        >>> print myPLOD.upsert("name", "Joe", entryB).returnString()
        [
            {age:  3, income: 93000, name: 'Jim'   , wigs:        68},
            {age:  3, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income:    30, name: 'Joe'   , wigs: [3, 2, 9]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]

        :param key:
           The dictionary key to examine.
        :param value:
           The value to search for as referenced by the key.
        :param entry:
           The replacement (or new) entry for the list.
        :returns:
           class
        '''
        index=internal.get_index(self.table, key, self.EQUAL, value)
        if index is None:
            self.index_track.append(len(self.table))
            self.table.append(entry)
        else:
            self.table[index]=entry
        return self

    def insert(self, new_entry):
        '''Insert a new entry to the end of the list of dictionaries.

        This entry retains the original index tracking but adds this
        entry incrementally at the end.

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> entryA = {"name": "Willie", "age": 77}
        >>> print PLOD(test).insert(entryA).returnString()
        [
            {age:  3, income: 93000, name: 'Jim'   , wigs:        68},
            {age:  3, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'   , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]

        :param new_entry:
           The new list entry to insert.
        '''
        self.index_track.append(len(self.table))
        self.table.append(new_entry)
        return self

    def deleteByIndex(self, index):
        "Removes a single entry from the list given the index reference."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            if counter != index:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self

    def deleteByIndexList(self, indexList):
        "Removes all the entriest from the list given the index references."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            if not counter in indexList:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self


        
    ############################
    # List Sorting/Arrangement routines
    ############################

    def renumber(self, key, start=1, increment=1):
        '''Incrementally number a key based on the current order of the list.

        Please note that if an entry in the list does not have the specified
        key, it is NOT created. The entry is, however, still counted.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 3 ,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).renumber("order", start=10).returnString()
        [
            {age:  3, income: 93000, name: 'Jim'  , order: 10},
            {age:  3, income: None , name: 'Larry', order: 11},
            {age: 20, income: 15000, name: 'Joe'  , order: 12},
            {age: 19, income: 29000, name: 'Bill' , order: 13}
        ]
        
        .. versionadded:: 0.0.2
        
        :param key:
            The dictionary key that should receive the numbering. The previous
            value is replaced, regardles of type or content. However, if the
            key does not exist, it is not created. However, that entry is still
            counted.
        :param start:
            Defaults to 1. The starting number to begin counting with.
        :param increment:
            Defaults to 1. The amount to increment by for each entry in the list.
        :returns: self

        '''
        result = []
        counter = start
        for row in self.table:
            new_row = internal.modify_member(row, key, counter)
            result.append(row)
            counter += increment
        self.table = result
        return self

    def sort(self, attr_name, reverse=False, none_greater=False):
        "Sort the list in the order of the named attribute."
        "If passed 'reverse=True', then the list is ordered in reverse."
        "If passed 'none_greater=True', then entries missing the attribute are placed at the top of the list."
        "  Otherwise, the entries missing the attribute (if any) are placed at the bottom of the list."
        for i in range(0, len(self.table)):
            min = i
            for j in range(i + 1, len(self.table)):
                if internal.is_first_lessor(self.table[j], self.table[min], attr_name, none_greater=none_greater, reverse=reverse):
                    min = j
            if i!=min:
                self.table[i], self.table[min] = self.table[min], self.table[i] # swap
                self.index_track[i], self.index_track[min] = self.index_track[min], self.index_track[i] # swap
        return self

    #################################
    # filters
    #################################

    def eq(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is is equal (==) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, attr_name, self.EQUAL, value, includeMissing)
        return self

    def ne(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is not equal (!=) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, attr_name, self.NOT_EQUAL, value, includeMissing)
        return self

    def gt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than (>) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, attr_name, self.GREATER, value, includeMissing)
        return self

    def gte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than-or-equal (=>) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, attr_name, self.GREATERorEQUAL, value, includeMissing)
        return self

    def lt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less than (<) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, field_name, self.LESS, value, includeMissing)
        return self

    def lte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less-than-or-equal (=<) value."
        (self.table, self.index_track) = internal.select(self.table, self.index_track, field_name, self.LESSorEQUAL, value, includeMissing)
        return self

    def hasKey(self, attr_name):
        "Return list entries where named attribute(key) is present."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            d = internal.convert_to_dict(row)
            if attr_name in d:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self

    def missingKey(self, attr_name):
        "Return list entries where named attribute(key) is not present."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            d = internal.convert_to_dict(row)
            if not attr_name in d:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self


    def contains(self, key, value, findAll=False, exclude=False, includeMissing=False):
        '''Return entries that:
        
        * have the key
        * key points to a list, and
        * value is found in the list.

        If value is also a list itself, then the list entry is return if any of the values match.

        If value is also a list itself and findAll=True, then all of the values must be in the list.
        
        .. versionadded:: 0.0.3b
        
        :param key:
            The dictionary key that should point to a list.
        :param value:
            The value to locate in the list. This argument can be an immutable value
            such as a string, tuple, or number.

            If this argument is a list of values instead, then this method will search for any of the values in that list. If the optional 'findAll' parameter is set to True, then all of the values in that list must be found. 
            
        Optional named arguments:
        
        :param finalAll: x
        :param exclude: if 'exclude' is True, then the entries that do NOT match the above conditions are returned.

        :param includeMissing: x
        :returns: self

        '''
        result = []
        result_index = []
        counter = 0
        for row in self.table:
            d = internal.convert_to_dict(row)
            if key in d:
                if findAll:
                    success = internal.list_match_all(d[key], value)
                else:
                    success = internal.list_match_any(d[key], value)
                if exclude:
                    success = not success
                if success:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    # item missing from list, so skip over
                    pass
            else:
                # if key key doesn't exist, then it is the same as an empty list
                if includeMissing:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    pass
            counter += 1
        self.table = result
        self.index_track = result_index
        return self



    ##############################
    #  Means of Returning Results
    ##############################

    def returnList(self, limit=False):
        "Return a list of dictionaries."
        if limit==False:
            return self.table
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.table[i])
        return result

    def returnString(self, limit=False, omitBrackets=False, executable=False):
        '''Return a string containing the list of dictionaries in easy
        human-readable read format.

        Each entry is on one line. Key/value pairs are 'spaced' in such a way
        as to have them all line up vertically if using a monospace font. The
        fields are normalized to alphabetical order. Missing keys in a
        dictionary are inserted with a value of 'None'.

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 3 ,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnString()
        [
            {age:  3, income: 93000, name: 'Jim'  , order: 2},
            {age:  3, income: None , name: 'Larry', order: 3},
            {age: 20, income: 15000, name: 'Joe'  , order: 1},
            {age: 19, income: 29000, name: 'Bill' , order: 4}
        ]
        >>> print PLOD(test).returnString(limit=3, omitBrackets=True, executable=True)
        {'age':  3, 'income': 93000, 'name': 'Jim'  , 'order': 2},
        {'age':  3, 'income': None , 'name': 'Larry', 'order': 3},
        {'age': 20, 'income': 15000, 'name': 'Joe'  , 'order': 1}
        
        :param limit:
           A number limiting the quantity of entries to return. Defaults to
           False, which means that the full list is returned.
        :param omitBrackets:
           If set to True, the outer square brackets representing the entire
           list are omitted. Defaults to False.
        :param executable:
           If set to True, the string is formatted in such a way that it
           conforms to Python syntax. Defaults to False.
        '''
        result = ""
        # we limit the table if needed
        if not limit:
            limit = len(self.table)
        used_table = []
        for i in range(limit):
            if len(self.table)>i:
                used_table.append(internal.convert_to_dict(self.table[i]))
        # we locate all of the attributes and their lengths
        attr_width = {}
        # first pass to get the keys themselves
        for row in used_table:
            for key in row:
                if not key in attr_width:
                    attr_width[key] = 0
        # get a sorted list of keys
        attr_order = attr_width.keys()
        attr_order.sort()
        # not get minimum widths
        #  (this is done as a seperate step to account for 'None' and other conditions.
        for row in used_table:
            for key in attr_width:
                if not key in row:
                    if attr_width[key] < len("None"):
                        attr_width[key] = len("None")
                else:
                    if len(repr(row[key])) > attr_width[key]:
                        attr_width[key] = len(repr(row[key]))
        # now we do the pretty print
        if not omitBrackets:
            result += "[\n"
        body = []
        for row in used_table:
            row_string = ""
            if not omitBrackets:
                row_string += "    "
            row_string += "{"
            middle = []
            for key in attr_order:
                if executable:
                    item = "'"+str(key) + "': "
                else:
                    item = str(key) + ": "
                if key in row:
                    s = repr(row[key])
                    if type(row[key]) is typemod.IntType:
                        s = s.rjust(attr_width[key])
                else:
                    s = "None"
                item += s.ljust(attr_width[key])
                middle.append(item)
            row_string += ", ".join(middle)
            row_string += "}"
            body.append(row_string)
        result += ",\n".join(body)
        if len(body) and not omitBrackets:
            result += "\n"
        if not omitBrackets:
            result += "]"
        return result

    def returnCSV(self, limit=False, omitHeaderLine=False):
        '''Return a list of dictionaries formated as a comma seperated values (CSV) list
        as a string.'''
        # we limit the table if needed
        used_table = self.table
        if limit:
            used_table = []
            for i in range(limit):
                if len(self.table)>i:
                    used_table.append(self.table[i])
        # we locate all of the attributes
        attr_list = []
        for row in used_table:
            for key in row:
                if not key in attr_list:
                    attr_list.append(key)
        # now we do the pretty print
        if not omitHeaderLine:
            result = ",".join(attr_list)
            result += "\n"
        for row in used_table:
            ml = []
            for key in attr_list:
                if key in row:
                    ml.append(repr(row[key]))
                else:
                    ml.append("")
            result += ",".join(ml)
            result += "\n"
        return result

    def returnIndexList(self, limit=False):
        "Return a list of integers that are list-index references to the original list of dictionaries."
        if limit==False:
            return self.index_track
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.index_track[i])
        return result


    def returnOneIndex(self, last=False):
        "Return one integer that is a list-index reference to the original list of dictionaries."
        "If the last=True, then the last reference is returned. Otherwise, the first reference is returned."
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.index_track.pop()
            else:
                return self.index_track[0]


    def returnOneEntry(self, last=False):
        "Return the first entry in the current list. If 'last=True', then the last entry is returned."
        "Returns None is the list is empty."
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.table[len(self.table)-1]
            else:
                return self.table[0]

    def returnValue(self, field_name, last=False):
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = internal.convert_to_dict(row)
        return dict_row.get(field_name, None)

    def returnValueList(self, field_list, last=False):
        result = []
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = internal.convert_to_dict(row)
        for field in field_list:
            result.append(dict_row.get(field, None))
        return result
    
    def found(self):
        "Return True if list has at least one item; otherwise return False."
        if len(self.table)==0:
            return False
        return True

    def missing(self):
        "Return True if list is empty; otherwise return False."
        if len(self.table)==0:
            return True
        return False

    def count(self):
        "Return an integer representing the number of items in the list."
        return len(self.table)


if __name__ == "__main__":

    if False:

        my_list = [
            {"name": "Joe",   "age": 82, "zip": {"zap": "ping"}},
            {"name": "Billy", "age": 22, "zip": {"zap": "ping"}},
            {"name": "Zam",   "age": 30, "zip": {"zap": "ping"}},
            {"name": "Julio", "age": 30},
            {"name": "Bob",   "age": 19, "zip": {"zap": "ping"}}
        ]

        def foo():
            print "hi"
        foo.jj = 'blah'
        # my_list.append(foo)


        final = PLOD(my_list).renumber(["zip", "zap"]).returnList()
        print PLOD(final).returnString()

    else:
        print "==================================="
        print
        import doctest
        print "Testing begins. Errors found:"
        print doctest.run_docstring_examples(PLOD, None)
        print doctest.run_docstring_examples(PLOD.__init__, None)
        # list modification
        print doctest.run_docstring_examples(PLOD.dropKey, None)
        print doctest.run_docstring_examples(PLOD.upsert, None)
        print doctest.run_docstring_examples(PLOD.insert, None)
        # list arrangement
        print doctest.run_docstring_examples(PLOD.renumber, None)
        # list return results
        print doctest.run_docstring_examples(PLOD.returnString, None)
        print "Tests done."
