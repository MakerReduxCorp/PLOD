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
    
import types as typemod
try:
    import bson
    bson_available = True
except ImportError:
    bson_available = False

def convert_to_dict(item):
    '''Examine an item of any type and return a true dictionary.

    If it is already is a dictionary, then the item is returned as-is. Easy.

    Otherwise, it attempts to interpret it. So far, this routine can handle:
    
    * a class, function, or anything with a .__dict__ entry
    * a mongoEngine document (a class for MongoDb handling)
    * a list (index positions are used as keys)

    .. versionadded:: 0.0.4

    :param item:
        Any object such as a variable, instance, or function.
    :returns:
        A true dictionary. If unable to get convert 'item', then an empty dictionary '{}' is returned.
    '''
    # get type
    actual_type = _detect_type(item)
    # given the type, do conversion
    if actual_type=="dict":
        return item
    elif actual_type=="list":
        temp = {}
        ctr = 0
        for entry in item:
            temp[ctr]=entry
            ctr += 1
        return temp
    elif actual_type=="mongoengine":
        return item.__dict__['_data']
    elif actual_type=="class":
        return item.__dict__
    return {}

def _detect_type(item):
    # possible return values:
    # 'dict', 'list', 'mongoengine', 'class'
    # or 'unknown'
    if type(item) is typemod.DictType:
        return "dict"
    if type(item) is typemod.ListType:
        return "list"
    try:
        temp = item.__dict__
    except AttributeError:
        return "unknown"
    if '_data' in temp:
        try:
            if "mongoengine.base" in str(item.__metaclass__):
                return "mongoengine"
        except:
            pass
    return "class"


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
          classes with a .__dict__ attribute
          mongoEngine documents (a class for MongoDb handling)
          other lists (index positions used as keys)

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

        Args:
            table (list): the list of dictionaries.
            
        Returns:
            None
        '''
        self.table = table
        self.index_track = []
        for i in range(len(self.table)):
            self.index_track.append(i)
        return None

    def _dict_crawl(self, entry, key):
        ''' returns a triple tuple representing the location of the key/key-list.
        returns: (parent_dictionary, final_key, value_found)
        If unable to locate the key, then (None, None, None) is returned.
        '''
        value = None
        if type(key) is typemod.ListType:
            key_list = key
        else:
            key_list = [key]
        try:
            result = None
            success_flag = True
            temp = entry
            for next_key in key_list:
                parent = temp
                actual_type = _detect_type(temp)
                print "temp", repr(temp), actual_type
                if actual_type=="mongoengine":
                    temp = temp.__dict__['_data'][next_key]
                elif actual_type=="class":
                    temp = temp.__dict__[next_key]
                elif actual_type=="dict":
                    temp = temp[next_key]
                elif actual_type=="list":
                    temp = temp[next_key]
                else:
                    success_flag = False
            if success_flag:
                return (parent, key_list[-1], temp)
            return (None, None, None)
        except:
            pass
        return (None, None, None)

    def _modify_member(self, row, key, value):
        ''' properly modifies a dict or class attribute '''
        (target, tkey, tvalue) = self._dict_crawl(row, key)
        if target:
            target[tkey] = value
        return row

    def _remove_member(self, row, key):
        ''' properly modifies a dict or class attribute '''
        (target, tkey, tvalue) = self._dict_crawl(row, key)
        if target:
            del target[tkey]
        return row

    def _do_op(self, field, op, value):
        if op==self.NOOP:
            return True
        if field==None:
            if value==None:
                return True
            else:
                return False
        if value==None:
            return False
        if op==self.LESS:
            return (field < value)
        if op==self.LESSorEQUAL:
            return (field <= value)
        if op==self.EQUAL:
            if repr(type(field))=="<class 'bson.objectid.ObjectId'>":
                if type(value) is typemod.StringType:
                    try:
                        value = bson.ObjectId(value)
                    except:
                        pass
            return (field == value)
        if op==self.GREATERorEQUAL:
            return (field >= value)
        if op==self.GREATER:
            return (field > value)
        if op==self.NOT_EQUAL:
            return (field != value)
        return False
        
        
        
    def _get_index(self, field_name, op, value):
        ''' 
        Returns the index of the first list entry that matches. If no matches
        are found, it returns None
        NOTE: it is not returning a list. It is returning an integer in range 0..LEN(target)
        NOTE: both 'None' and 0 evaluate as False in python. So, if you are checking for a
           None being returned, be explicit. "if myindex==None:" not simply "if not myindex:"
        '''
        counter = 0
        for row in self.table:
            dict_row = convert_to_dict(row)
            if self._do_op(dict_row.get(field_name, None), op, value):
                return counter
            counter += 1
        return None


    def _get_value(self, row, field_name):
        '''
        Returns the value found in the field_name attribute of the row dictionary.
        '''
        result = None
        dict_row = convert_to_dict(row)
        if type(field_name) is typemod.ListType:
            temp = row
            for field in field_name:
                dict_temp = convert_to_dict(temp)
                temp = dict_temp.get(field, None)
            result = temp
        else:
            result = dict_row.get(field_name, None)
        return result
        
    def _detect_fields(self, field_name, row):
        if type(field_name) is typemod.ListType:
            ptr = row
            for field in field_name:
                # print field, repr(ptr)
                if field in ptr:
                    ptr = ptr[field]
                else:
                    return False
            return True
        else:
            if field_name in row:
                return True
        return False


    def _select(self, field_name, op, value, includeMissing):
        '''Modifies the self.table and self.index_track lists based on the comparison.
        '''
        result = []
        result_index = []
        counter = 0
        for row in self.table:
            if self._detect_fields(field_name, convert_to_dict(row)):
                final_value = self._get_value(row, field_name)
                if self._do_op(final_value, op, value):
                    result.append(row)
                    result_index.append(self.index_track[counter])
            else:
                if includeMissing:
                    result.append(row)
                    result_index.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_index
        return

    def _is_first_lessor(self, row_one, row_two, key_field, none_greater=False, reverse=False):
        missing_one_flag = not (self._get_value(row_one, key_field))
        missing_two_flag = not (self._get_value(row_two, key_field))
        if missing_one_flag:
            if none_greater:
                result = False
            else:
                result = True
        else:
            if missing_two_flag:
                if none_greater:
                    result = True
                else:
                    result = False
            else:
                if reverse:
                    # this subtle difference here is what makes the sorting
                    # algorithm "stable". that is, it only sorts values if a
                    # difference is seen, otherwise original order is left
                    # intact. (a reversed '<=' is a '>')
                    result = (self._get_value(row_one, key_field) <= self._get_value(row_two, key_field))
                else:
                    result = (self._get_value(row_one, key_field) < self._get_value(row_two, key_field))
        if reverse:
            result = not result
        return result

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
        >>> print PLOD(test).dropAttribute("income").returnString()
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
            result.append(self._remove_member(row, key))
        self.table = result
        return self

    ############################
    # List Modifications
    ############################

    def upsert(self, key, value, entry):
        '''Update or Insert an entry into the list of dictionaries.

        If an entry in the list of dictionary is found where key matches value, then
            the FIRST matching list entry is replaced with entry
        else
            the entry is appended to the end of the list.

        NOTE: the 'entry' is not examined in anyway. If the entry should have the
        key/value, then you must append that prior to calling this routine.

        Args:
            key (var): the dictionary key to examine for update vs. insert
            value (var): the value to compare against key
            entry (dict or var): the replacement or new entry for the list
            
        Returns:
            self
        '''
        index=self._get_index(key, self.EQUAL, value)
        if index==None:
            self.index_track.append(len(self.table))
            self.table.append(entry)
        else:
            self.table[index]=entry
        return self

    def insert(self, new_entry):
        '''
        The new_entry is appended to the end of the list.
        NOTE: The value and type of new_entry ARE NOT examined. It is used as-is.
        NOTE: If an update (replacement) is done, it only updates the FIRST MATCH
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
            new_row = self._modify_member(row, key, counter)
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
                if self._is_first_lessor(self.table[j], self.table[min], attr_name, none_greater=none_greater, reverse=reverse):
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
        self._select(attr_name, self.EQUAL, value, includeMissing)
        return self

    def ne(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is not equal (!=) value."
        self._select(attr_name, self.NOT_EQUAL, value, includeMissing)
        return self

    def gt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than (>) value."
        self._select(attr_name, self.GREATER, value, includeMissing)
        return self

    def gte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than-or-equal (=>) value."
        self._select(attr_name, self.GREATERorEQUAL, value, includeMissing)
        return self

    def lt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less than (<) value."
        self._select(field_name, self.LESS, value, includeMissing)
        return self

    def lte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less-than-or-equal (=<) value."
        self._select(field_name, self.LESSorEQUAL, value, includeMissing)
        return self

    def hasKey(self, attr_name):
        "Return list entries where named attribute(key) is present."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            d = convert_to_dict(row)
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
            d = convert_to_dict(row)
            if not attr_name in d:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self


    def _list_match_any(self, source, value):
        if type(source) is typemod.ListType:
            for sub_source in source:
                if type(value) is typemod.ListType:
                    # list vs list
                    for sub_val in value:
                        if self._do_op(sub_source, self.EQUAL, sub_val):
                            return True
                else:
                    # list vs non-list
                    if self._do_op(sub_source, self.EQUAL, value):
                        return True
            return False           
        else:
            if type(value) is typemod.ListType:
                # non-list vs list
                for sub_val in value:
                    if self._do_op(source, self.EQUAL, sub_val):
                        return True
                    return False
            else:
                # non-list vs non-list, that is a simple comparison:
                return self._do_op(source, self.EQUAL, value)
        return False

    def _list_match_all(self, source, value):
        success = True
        if type(value) is typemod.ListType:
            for sub_val in value:
                if type(source) is typemod.ListType:
                    # list vs list
                    entry_found = False
                    for sub_source in source:
                        if self._do_op(sub_source, self.EQUAL, sub_val):
                            entry_found = True
                    if not entry_found:
                        success = False
                else:
                    # non-list vs list
                    if not self._do_op(source, self.EQUAL, sub_val):
                        success = False
        else:
            if type(source) is typemod.ListType:
                # list vs non-list
                success = False
                for sub_source in source:
                    if self._do_op(sub_source, self.EQUAL, value):
                        success = True
            else:
                # non-list vs non-list, that is a simple comparison:
                success = self._do_op(source, self.EQUAL, value)
        return success



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
            d = convert_to_dict(row)
            if key in d:
                if findAll:
                    success = self._list_match_all(d[key], value)
                else:
                    success = self._list_match_any(d[key], value)
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

    def returnString(self, limit=False, omitBrackets=False):
        "Return a list of dictionaries formated as a basic indented string"
        result = ""
        # we limit the table if needed
        if not limit:
            limit = len(self.table)
        used_table = []
        for i in range(limit):
            if len(self.table)>i:
                used_table.append(convert_to_dict(self.table[i]))
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
            row_string = "    {"
            middle = []
            for key in attr_order:
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
        if len(body):
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
        dict_row = convert_to_dict(row)
        return dict_row.get(field_name, None)

    def returnValueList(self, field_list, last=False):
        result = []
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = convert_to_dict(row)
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
    print "This is a module for manipulating lists of dictionaries."
    print "It being a module, there is no point in running me as a script."

    if True:

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
        print help(PLOD)
        print
        print "==================================="
        print
        import doctest
        print "Testing begins. Errors found:"
        print doctest.run_docstring_examples(PLOD, None)
        print doctest.run_docstring_examples(PLOD.__init__, None)
        print doctest.run_docstring_examples(PLOD.dropAttribute, None)
        print "Tests done."
